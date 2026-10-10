"""Irregular waves and annual energy for either backend (no UI imports). SI units.

Linear superposition: a sea state with one-sided spectrum S(w) [m^2 s/rad] is a sum of regular
components of amplitude a_i = sqrt(2 S(w_i) dw). Each backend's regular-wave power is quadratic in
amplitude, so the mean absorbed power is
    P = integral 2 S(w) P1(w) dw,        P1 = power in a regular wave of amplitude 1 m,
and the incident power per metre of crest is J = rho g integral S(w) cg(w) dw.
Assumptions (shown in the app): long-crested waves, one direction, no wave transformation between
where the sea state was measured and the device, a turbine setting cPTO that is fixed within a
sea state (it can be changed between sea states, not between wave components).
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

import owc_toy as o

G = o.G
DATA_DIR = Path(__file__).with_name("data")


def jonswap(w, hm0, tp, gamma=3.3):
    """One-sided JONSWAP spectrum S(w) [m^2 s/rad], scaled so that 4 sqrt(m0) = hm0 exactly."""
    w = np.asarray(w, dtype=float)
    wp = 2 * np.pi / tp

    def shape(x):
        sig = np.where(x <= wp, 0.07, 0.09)
        r = np.exp(-((x - wp) ** 2) / (2 * sig**2 * wp**2))
        with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
            pm = np.where(x > 0, x**-5.0 * np.exp(-1.25 * (wp / x) ** 4), 0.0)
        return pm * gamma**r

    xf = np.linspace(0.05 * wp, 12 * wp, 20001)  # fine grid for the normalisation only
    m0 = np.trapezoid(shape(xf), xf)
    return shape(w) * (hm0**2 / 16) / m0


def te_over_tp(gamma=3.3):
    """Energy period over peak period, Te/Tp = 2 pi m_{-1}/m0 / Tp, computed from the spectrum shape."""
    tp = 10.0
    w = np.linspace(0.05, 12, 40001) * 2 * np.pi / tp
    s = jonswap(w, 1.0, tp, gamma)
    return float(2 * np.pi * np.trapezoid(s / w, w) / np.trapezoid(s, w) / tp)


def spectrum(w, hm0, te, gamma=3.3):
    """JONSWAP from the energy period Te (the scatter tables use Te)."""
    return jonswap(w, hm0, te / te_over_tp(gamma), gamma)


def incident_power(w, s, h, rho=1025.0):
    """J = rho g integral S cg dw [W/m], finite depth."""
    return float(rho * G * np.trapezoid(s * o.group_velocity(w, h), w))


def absorbed_power(w, s, p1):
    """P = integral 2 S(w) P1(w) dw [W], with P1 the regular-wave power per unit amplitude squared."""
    return float(np.trapezoid(2 * s * p1, w))


def unit_power(c, a, qe_unit, a_pto, c_pto):
    """Regular-wave turbine power for A = 1 m from the chamber equation (any backend) [W]."""
    return 0.5 * c_pto * qe_unit**2 / ((c + c_pto) ** 2 + (a + a_pto) ** 2)


def captured_fraction(w, s, hm0):
    """Share of the sea state's energy inside the frequency grid w (jonswap is normalised to m0 = hm0^2/16)."""
    return float(np.trapezoid(s, w) / (hm0**2 / 16))


# ------------------------------------------------------------------ scatter table and annual energy
def load_scatter(path=None):
    """Sipora 2022 Hs-Te scatter (hours) inside the thesis direction sector; bin centres are used."""
    path = Path(path) if path else DATA_DIR / "sipora_2022_sector_scatter_counts.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    hs = np.array([(float(r["hs_lower_m"]) + float(r["hs_upper_m"])) / 2 for r in rows])
    te = np.array([(float(r["te_lower_s"]) + float(r["te_upper_s"])) / 2 for r in rows])
    hours = np.array([float(r["hours"]) for r in rows])
    return {"hs": hs, "te": te, "hours": hours, "rows": rows}


def site_energy(w, coeffs, a_pto, scatter, h, c_pto=None, gamma=3.3, rho=1025.0):
    """Mean power per sea state and annual energy.

    coeffs: dict with c, a, qe_unit on the frequency grid w (from either backend, A = 1 m).
    c_pto None: the single fixed cPTO that maximises the energy over the whole table is found.
    Returns per-bin P [W] and J [W/m] for that fixed cPTO and for cPTO retuned per sea state
    (the upper bound for a turbine tuned slowly, once per sea state).
    """
    c, a, q = coeffs["c"], coeffs["a"], coeffs["qe_unit"]
    specs = [spectrum(w, hs, te, gamma) for hs, te in zip(scatter["hs"], scatter["te"])]
    J = np.array([incident_power(w, s, h, rho) for s in specs])
    hours = scatter["hours"]

    def bin_power(cp):
        p1 = unit_power(c, a, q, a_pto, cp)
        return np.array([absorbed_power(w, s, p1) for s in specs])

    def neg_energy(log_cp):
        return -float(np.sum(bin_power(10**log_cp) * hours))

    if c_pto is None:
        r = minimize_scalar(neg_energy, bounds=(-6, 1), method="bounded", options={"xatol": 1e-4})
        c_pto = 10**r.x
    P_fixed = bin_power(c_pto)
    P_tuned = np.array([max(-minimize_scalar(lambda lc: -absorbed_power(w, s, unit_power(c, a, q, a_pto, 10**lc)),
                                             bounds=(-6, 1), method="bounded", options={"xatol": 1e-3}).fun, 0.0)
                        for s in specs])
    return {"c_pto": float(c_pto), "J": J, "P_fixed": P_fixed, "P_tuned": P_tuned, "hours": hours,
            "E_fixed_MWh": float(np.sum(P_fixed * hours) / 1e6), "E_tuned_MWh": float(np.sum(P_tuned * hours) / 1e6),
            "E_incident_MWh_per_m": float(np.sum(J * hours) / 1e6), "total_hours": float(hours.sum())}


def toy_coeffs(w, p: o.Params):
    """Toy coefficients on w for A = 1 m (dict for site_energy) and aPTO."""
    from dataclasses import replace
    p1 = replace(p, A=1.0)
    c, a = o.radiation_coefficients(w, p1)
    return {"c": c, "a": a, "qe_unit": o.excitation_flow(w, p1)}, o.a_pto(w, p1)
