"""Physics verification of the toy model (see VERIFICATION.md). Symbolic: sympy; numeric: time-domain ODE."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "verification"))
pytest.importorskip("sympy")
import verify_toy as v  # noqa: E402
import owc_toy as o  # noqa: E402


def test_symbolic_derivations():
    v.s1_piston_admittance()
    v.s2_air_chamber()
    v.s3_chamber_equation()
    v.s4_power_optimum()
    v.s5_energy_balance()
    assert abs(v.s6_waves()["rule_coefficient_kW"] - 0.4906) < 1e-3


def test_dispersion_independent_solver():
    assert v.n1_dispersion() < 1e-12


@pytest.mark.parametrize("factor", [1.0, 1.3])
def test_time_domain_matches_frequency_domain(factor):
    p = o.Params()
    w = factor * o.resonance_frequency_with_pto(p)
    cp = float(o.optimal_c_pto(w, p))
    P_t, p_amp, e_res = v.n2_time_domain(w, cp, p, periods=60, keep=10)
    assert abs(P_t - float(o.power(w, cp, p))) / float(o.power(w, cp, p)) < 1e-8
    assert abs(p_amp - float(abs(o.pressure(w, cp, p)))) / float(abs(o.pressure(w, cp, p))) < 1e-4
    assert abs(e_res) < 1e-8


def test_zeta_plausibility_numbers():
    z = v.p1_zeta_estimate()
    assert 0.5 < z["zeta_consistent_with_FK"] < 0.8  # documented finding: toy zeta 0.3 is about half


def test_zeta_estimate_is_stable_and_resonance_depends_on_zeta():
    from dataclasses import replace
    z0, w0 = o.zeta_froude_krylov(o.Params())
    z1, _ = o.zeta_froude_krylov(replace(o.Params(), zeta=round(z0, 2)))
    assert z1 == z0 and abs(w0 - o.natural_frequency(o.Params())) < 1e-12  # independent of zeta itself
    assert abs(z0 - 0.538) < 2e-3
    assert o.has_pto_resonance(o.Params()) and not o.has_pto_resonance(replace(o.Params(), zeta=0.63))


def test_zheng_long_wave_limit_and_scaling():
    """Independent physical limit (verification/validate_limits.py): wall doubling + Haskind, kR -> 0."""
    import validate_limits as vl
    rows = vl.l1_long_wave(khs=(0.1, 0.05))
    assert abs(rows[1]["Qe_ratio"] - 1) < 1e-3 and abs(rows[1]["c_ratio"] - 1) < 2e-3
    # error shrinks like (kR)^2: halving kh cuts it by about 4
    assert 3 < (rows[0]["c_ratio"] - 1) / (rows[1]["c_ratio"] - 1) < 5
    s = vl.l2_scaling()
    assert abs(s["zheng"] - 3) < 0.05 and abs(s["toy"] - 2) < 0.05


def test_frequency_dependent_damping_mode():
    """Optional "froude_krylov" damping: physical w^3 long-wave scaling, Haskind consistency (eta_max = 1),
    equal to the zeta estimate at the natural frequency, and the default mode unchanged."""
    import numpy as np
    from dataclasses import replace
    p = replace(o.Params(), damping="froude_krylov")
    w = np.array([0.05, 0.1])
    c, _ = o.radiation_coefficients(w, p)
    assert abs(np.log(c[1] / c[0]) / np.log(2) - 3) < 0.05
    wn = o.natural_frequency(p)
    m, K = p.rho * p.S * p.L, p.rho * o.G * p.S
    assert abs(o.damping_coefficient(wn, p) / (2 * np.sqrt(K * m)) - o.zeta_froude_krylov(o.Params())[0]) < 1e-12
    wg = np.linspace(0.3, 4, 4000)
    eta = o.capture_width_ratio(wg, o.optimal_c_pto(wg, p), p)
    assert eta.max() <= 1 + 1e-9 and eta.max() > 0.999
    assert o.Params().damping == "constant"
