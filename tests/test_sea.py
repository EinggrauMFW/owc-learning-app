"""Irregular waves and annual energy (owc_sea.py)."""
from dataclasses import replace

import numpy as np

import owc_sea as s
import owc_toy as o


def test_spectrum_normalisation_and_periods():
    w = np.linspace(0.05, 6, 6000)
    S = s.spectrum(w, 2.0, 10.0)
    assert abs(4 * np.sqrt(np.trapezoid(S, w)) - 2.0) < 1e-3          # Hm0 = 4 sqrt(m0)
    assert abs(s.te_over_tp(3.3) - 0.903) < 2e-3                       # JONSWAP gamma 3.3 (thesis ~0.90)
    assert abs(s.te_over_tp(1.0) - 0.857) < 2e-3                       # Pierson-Moskowitz
    te = 2 * np.pi * np.trapezoid(S / w, w) / np.trapezoid(S, w)       # energy period recovered
    assert abs(te - 10.0) < 0.01


def test_deep_water_incident_power_is_the_049_rule():
    w = np.linspace(0.05, 6, 6000)
    J = s.incident_power(w, s.spectrum(w, 2.0, 10.0), h=5000.0)
    assert abs(J / (1025 * 9.81**2 * 2.0**2 * 10.0 / (64 * np.pi)) - 1) < 1e-4


def test_superposition_matches_regular_power_for_flat_response():
    """With P1 = 1 W per m^2 of amplitude, P = 2 m0 = Hm0^2 / 8 (a regular wave of the same energy)."""
    w = np.linspace(0.05, 6, 6000)
    S = s.spectrum(w, 2.0, 10.0)
    assert abs(s.absorbed_power(w, S, np.ones_like(w)) - 2.0**2 / 8) < 1e-3


def test_unit_power_matches_toy_regular_power():
    p = o.Params()
    w = np.linspace(0.5, 3, 50)
    co, ap = s.toy_coeffs(w, p)
    assert np.allclose(s.unit_power(co["c"], co["a"], co["qe_unit"], ap, 0.01), o.power(w, 0.01, p), rtol=1e-12)


def test_site_energy_bounds_and_scatter():
    sc = s.load_scatter()
    assert len(sc["hours"]) == 59 and sc["hours"].sum() == 5194
    w = np.linspace(0.2, 4.0, 800)
    p = replace(o.Params(), damping="froude_krylov")
    co, ap = s.toy_coeffs(w, p)
    r = s.site_energy(w, co, ap, sc, p.h)
    assert 0 < r["E_fixed_MWh"] <= r["E_tuned_MWh"] * (1 + 1e-6)       # retuning per sea state cannot lose
    assert np.all(r["P_fixed"] <= r["J"] * 2 / np.array([o.wavenumber(2 * np.pi / te, p.h) for te in sc["te"]]))
