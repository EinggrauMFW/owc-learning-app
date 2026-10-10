"""Physics verification of the toy OWC model (owc_toy.py), independent of its frequency-domain code.

Three kinds of check:
  S. symbolic (sympy): every formula in owc_toy.py derived from the governing equations below;
  N. numerical: a time-domain simulation of the same ODEs (scipy solve_ivp) must reproduce the
     frequency-domain power, pressure and capture width;
  P. physical plausibility: the toy's free parameters compared with an independent hydrodynamic
     estimate (Froude-Krylov force + Haskind relation).

Governing equations (linear, time factor exp(-i w t)):
  water column (piston, area S, mass m = rho S L):  m x'' + B x' + K x = F_e(t) - S p,  K = rho g S
  air chamber (isentropic, linearised):              p' = (rho0 v^2 / V0) (S x' - cPTO p)
  turbine (linear Wells):                            volume flow out = cPTO p
Run:  python verification/verify_toy.py
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import j1

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import owc_toy as o  # noqa: E402

I = sp.I


# ---------------------------------------------------------------- S: symbolic derivations
def s1_piston_admittance():
    """Column ODE in the frequency domain gives Y = c - i a = S^2 / (B - i X), X = w m - K/w,
    hence c = S^2 B/(B^2+X^2), a = -S^2 X/(B^2+X^2) exactly as radiation_coefficients()."""
    w, m, B, K, S = sp.symbols("omega m B K S", positive=True)
    Xa, F = sp.symbols("X_a F")
    # x = Xa e^{-iwt}: (-w^2 m - i w B + K) Xa = F ; U = -i w Xa (velocity amplitude)
    U = -I * w * sp.solve(sp.Eq((-w**2 * m - I * w * B + K) * Xa, F), Xa)[0]
    X = w * m - K / w
    assert sp.simplify(U - F / (B - I * X)) == 0
    # radiation: F = -S p  ->  water-surface volume flow Q_R = S U = -(S^2/(B - iX)) p = -(c - i a) p (paper Eq. 4)
    Y = S**2 / (B - I * X)
    c_code = S**2 * B / (B**2 + X**2)
    a_code = -S**2 * X / (B**2 + X**2)
    assert sp.simplify(Y - (c_code - I * a_code)) == 0
    # natural frequency: a = 0 <=> X = 0 <=> w = sqrt(K/m); with K = rho g S, m = rho S L -> sqrt(g/L)
    rho, g, L = sp.symbols("rho g L", positive=True)
    wn = sp.solve(sp.Eq(X, 0), w)[0].subs({K: rho * g * S, m: rho * S * L})
    assert sp.simplify(wn - sp.sqrt(g / L)) == 0
    # c is largest at X = 0, where c = S^2 / B
    assert sp.simplify(c_code.subs(K, w**2 * m) - S**2 / B) == 0
    return {"Y": Y, "c": c_code, "a": a_code, "w_nat": wn}


def s2_air_chamber():
    """Linearised isentropic air: p' = (rho0 v^2/V0)(S x' - cPTO p)  =>  S U = (cPTO - i aPTO) p,
    aPTO = w V0/(v^2 rho0), as a_pto(). (v^2 rho0 = gamma p_atm: the adiabatic bulk modulus.)"""
    w, V0, v, rho0, cP = sp.symbols("omega V0 v rho0 c_PTO", positive=True)
    p, SU = sp.symbols("p SU")
    SU_sol = sp.solve(sp.Eq(-I * w * p, rho0 * v**2 / V0 * (SU - cP * p)), SU)[0]
    a_pto = w * V0 / (v**2 * rho0)
    assert sp.simplify(SU_sol - (cP - I * a_pto) * p) == 0
    return {"SU": SU_sol, "a_pto": a_pto}


def s3_chamber_equation():
    """Superposition: S U = Qe - (c - i a) p (Qe = flow with p = 0). With S2: Eq. 2 of the paper,
    [(c + cPTO) - i (a + aPTO)] p = Qe, i.e. pressure()."""
    c, a, cP, aP = sp.symbols("c a c_PTO a_PTO", real=True)
    p, Qe = sp.symbols("p Q_e")
    p_sol = sp.solve(sp.Eq(Qe - (c - I * a) * p, (cP - I * aP) * p), p)[0]
    assert sp.simplify(p_sol - Qe / ((c + cP) - I * (a + aP))) == 0
    return {"p": p_sol}


def s4_power_optimum():
    """P = cPTO |p|^2/2 is maximised by cPTO = sqrt(c^2 + (a+aPTO)^2) (paper Eq. 39, optimal_c_pto());
    at a + aPTO = 0 that is cPTO = c and P_max = |Qe|^2/(8c); the closed form in optimal_power()."""
    c, cP, s, Q = sp.symbols("c c_PTO s Q", positive=True)  # s = |a + aPTO|, Q = |Qe|
    P = cP / 2 * Q**2 / ((c + cP) ** 2 + s**2)
    crit = sp.solve(sp.diff(P, cP), cP)
    assert crit == [sp.sqrt(c**2 + s**2)]
    copt = crit[0]
    assert sp.simplify(sp.diff(P, cP, 2).subs(cP, copt)) .is_negative
    assert sp.simplify(P.subs(cP, copt) - Q**2 / (4 * (c + copt))) == 0
    assert sp.simplify(P.subs({cP: c, s: 0}) - Q**2 / (8 * c)) == 0
    return {"c_opt": copt}


def s5_energy_balance():
    """Work done by the wave on the column, Re(Qe p*)/2, equals radiated c|p|^2/2 + absorbed cPTO|p|^2/2
    (the air spring stores and returns energy: zero mean)."""
    c, a, cP, aP = sp.symbols("c a c_PTO a_PTO", real=True)
    pr, pi_ = sp.symbols("p_r p_i", real=True)
    p = pr + I * pi_
    Qe = ((c + cP) - I * (a + aP)) * p
    lhs = sp.re(sp.expand(Qe * sp.conjugate(p))) / 2
    rhs = (c + cP) * (pr**2 + pi_**2) / 2
    assert sp.simplify(lhs - rhs) == 0
    return True


def s6_waves():
    """Group velocity from w^2 = g k tanh(kh): cg = dw/dk = (w/2k)(1 + 2kh/sinh 2kh) (group_velocity());
    deep-water limit gives Pin = rho g^2 A^2 T/(8 pi); irregular-sea rule rho g^2 Hs^2 Te/(64 pi) = 0.49 Hs^2 Te kW/m."""
    k, h, g = sp.symbols("k h g", positive=True)
    w = sp.sqrt(g * k * sp.tanh(k * h))
    cg_code = w / (2 * k) * (1 + 2 * k * h / sp.sinh(2 * k * h))
    diff = (sp.diff(w, k) - cg_code).rewrite(sp.exp)
    assert sp.simplify(diff) == 0
    # deep water: tanh -> 1, cg -> g/(2w); Pin = rho g A^2 cg / 2 with w = 2 pi / T
    rho, A, T = sp.symbols("rho A T", positive=True)
    Pin_deep = rho * g * A**2 / 2 * (g / (2 * (2 * sp.pi / T)))
    assert sp.simplify(Pin_deep - rho * g**2 * A**2 * T / (8 * sp.pi)) == 0
    coef = float((1025 * 9.81**2 / (64 * sp.pi) / 1000).evalf())
    assert abs(coef - 0.49) < 0.005, coef
    return {"rule_coefficient_kW": coef}


# ---------------------------------------------------------------- N: independent numerics
def n1_dispersion(p=o.Params()):
    """owc_toy.wavenumber (Newton) against an independent bracketing root solver."""
    out = []
    for w in (0.3, 0.8, 1.647, 3.0, 6.0):
        kb = brentq(lambda k: o.G * k * np.tanh(k * p.h) - w**2, 1e-9, 50.0, xtol=1e-14)
        out.append(abs(float(o.wavenumber(w, p.h)) - kb) / kb)
    return max(out)


def _qe_force(w, p):
    """Excitation force amplitude F_e that gives the toy's |Qe| through the column ODE:
    Qe = S F_e / (B - i X)  =>  F_e = |Qe| |B - i X| / S (phase irrelevant for power)."""
    m, K = p.rho * p.S * p.L, p.rho * o.G * p.S
    B = 2 * p.zeta * np.sqrt(K * m)
    X = w * m - K / w
    return float(o.excitation_flow(w, p)) * abs(B - 1j * X) / p.S, m, K, B


def n2_time_domain(w, c_pto, p=o.Params(), periods=80, keep=20):
    """Integrate the ODEs to steady state; return (mean absorbed power, |p| amplitude, energy residual)."""
    Fe, m, K, B = _qe_force(w, p)
    kair = p.rho0 * p.v**2 / p.V0

    def rhs(t, y):
        x, u, pr = y
        return [u, (Fe * np.cos(w * t) - B * u - K * x - p.S * pr) / m, kair * (p.S * u - c_pto * pr)]

    T = 2 * np.pi / w
    t_end = periods * T
    t_eval = np.linspace(t_end - keep * T, t_end, keep * 400 + 1)
    sol = solve_ivp(rhs, (0, t_end), [0.0, 0.0, 0.0], method="DOP853", rtol=1e-10, atol=1e-12,
                    t_eval=t_eval)
    x, u, pr = sol.y
    P_turb = np.trapezoid(c_pto * pr**2, sol.t) / (sol.t[-1] - sol.t[0])
    P_in = np.trapezoid(Fe * np.cos(w * sol.t) * u, sol.t) / (sol.t[-1] - sol.t[0])
    P_rad = np.trapezoid(B * u**2, sol.t) / (sol.t[-1] - sol.t[0])
    return P_turb, 0.5 * (pr.max() - pr.min()), (P_in - P_rad - P_turb) / P_in


def n2_compare(p=o.Params()):
    """Time domain vs frequency domain at several periods and turbine settings."""
    w_res = o.resonance_frequency_with_pto(p)
    rows = []
    for w in (0.9 * w_res, w_res, 1.3 * w_res):
        for cp in (float(o.optimal_c_pto(w, p)), 0.004, 0.05):
            Pt, pamp, e_res = n2_time_domain(w, cp, p)
            Pf = float(o.power(w, cp, p))
            pf = float(abs(o.pressure(w, cp, p)))
            rows.append({"T_s": 2 * np.pi / w, "c_pto": cp, "P_time_kW": Pt / 1e3, "P_freq_kW": Pf / 1e3,
                         "rel_err_P": abs(Pt - Pf) / Pf, "rel_err_p": abs(pamp - pf) / pf,
                         "energy_residual": e_res})
    return rows


# ---------------------------------------------------------------- P: physical plausibility
def p1_zeta_estimate(p=o.Params()):
    """Independent estimate of the column's radiation damping at the toy's PTO resonance.

    Haskind relation for an axisymmetric absorber in heave: B = k |F_e|^2 / (8 J), J = Pin per metre
    (equivalently: maximum capture width 1/k). F_e estimated by Froude-Krylov on a surface disk of
    radius a: F_FK = rho g A S * 2 J1(ka)/(ka) (incident-wave pressure averaged over the disk;
    diffraction neglected, so this is an estimate, not a solution).
    Returns the damping ratio zeta that would make the toy consistent with that force.
    """
    w = o.resonance_frequency_with_pto(p)
    k = float(o.wavenumber(w, p.h))
    J = float(o.incident_power(w, p))
    ka = k * p.r_in
    F_fk = p.rho * o.G * p.A * p.S * 2 * j1(ka) / ka
    B_hask = k * F_fk**2 / (8 * J)
    m, K = p.rho * p.S * p.L, p.rho * o.G * p.S
    zeta_eq = B_hask / (2 * np.sqrt(K * m))
    Fe_toy, *_ = _qe_force(w, p)
    return {"w": w, "ka": ka, "F_FK_over_rhogAS": 2 * j1(ka) / ka, "zeta_toy": p.zeta,
            "zeta_consistent_with_FK": zeta_eq, "Fe_toy_over_F_FK": Fe_toy / F_fk}


def main():
    s1_piston_admittance(); s2_air_chamber(); s3_chamber_equation(); s4_power_optimum(); s5_energy_balance()
    sw = s6_waves()
    print("S1-S6 symbolic derivations: all identities hold (sympy).")
    print(f"     0.49 rule coefficient rho g^2/(64 pi) = {sw['rule_coefficient_kW']:.4f} kW/(m^2 s m)")
    print(f"N1 dispersion: max rel. difference Newton vs brentq = {n1_dispersion():.2e}")
    print("N2 time-domain ODE vs frequency domain (default Params):")
    print(f"   {'T [s]':>6} {'cPTO':>9} {'P_time kW':>10} {'P_freq kW':>10} {'err P':>9} {'err |p|':>9} {'energy res':>10}")
    for r in n2_compare():
        print(f"   {r['T_s']:6.3f} {r['c_pto']:9.4g} {r['P_time_kW']:10.4f} {r['P_freq_kW']:10.4f} "
              f"{r['rel_err_P']:9.1e} {r['rel_err_p']:9.1e} {r['energy_residual']:10.1e}")
    z = p1_zeta_estimate()
    print(f"P1 at the PTO resonance (ka = {z['ka']:.3f}): Froude-Krylov factor 2J1(ka)/ka = {z['F_FK_over_rhogAS']:.3f}")
    print(f"   toy zeta = {z['zeta_toy']}, zeta consistent with Froude-Krylov + Haskind = {z['zeta_consistent_with_FK']:.3f}")
    print(f"   toy's implied excitation force / Froude-Krylov force = {z['Fe_toy_over_F_FK']:.3f}")


if __name__ == "__main__":
    main()
