import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import owc_toy as o  # noqa: E402

P = o.Params()
W = np.linspace(0.6, 3.0, 25)  # rad/s, T = 2.1 .. 10.5 s


def test_dispersion_relation():
    k = o.wavenumber(W, P.h)
    assert np.allclose(o.G * k * np.tanh(k * P.h), W**2, rtol=1e-10)


def test_deep_water_power_matches_0p49_rule():
    # Regular wave, deep water: Pin = rho g^2 A^2 T / (8 pi).
    # With Hs = 2A and Te -> T this is 2 x the irregular-sea rule 0.49 Hs^2 Te kW/m
    # (rho g^2 / (64 pi) = 490.6 W/m^3/s). Check both the regular-wave formula and that factor.
    p = o.Params(h=500.0)
    T = 8.0
    w = 2 * np.pi / T
    pin = o.incident_power(w, p)
    assert pin == pytest.approx(p.rho * o.G**2 * p.A**2 * T / (8 * np.pi), rel=1e-6)
    hs = 2 * p.A
    rule = p.rho * o.G**2 / (64 * np.pi) * hs**2 * T  # W/m, 0.49 Hs^2 Te kW/m form
    assert rule / 1e3 == pytest.approx(0.49 * hs**2 * T, rel=0.01)
    assert pin == pytest.approx(2 * rule, rel=1e-6)


def test_radiation_signs_and_resonance():
    w0 = o.natural_frequency(P)
    c, a = o.radiation_coefficients(np.array([0.7 * w0, w0, 1.4 * w0]), P)
    assert a[0] > 0 and abs(a[1]) < 1e-12 and a[2] < 0   # N-shaped a(w)
    assert np.all(c > 0)
    ws = np.linspace(0.5 * w0, 1.5 * w0, 2001)
    cs, _ = o.radiation_coefficients(ws, P)
    assert ws[np.argmax(cs)] == pytest.approx(w0, rel=2e-3)  # c peaks at X = 0


def test_pto_resonance_is_above_natural_frequency():
    # aPTO > 0 pushes the PTO resonance (a + aPTO = 0) to higher frequency (cf. paper Fig. 5c)
    assert o.resonance_frequency_with_pto(P) > o.natural_frequency(P)


def test_haskind_gives_eta_one_at_matched_condition():
    wr = o.resonance_frequency_with_pto(P)
    c, a = o.radiation_coefficients(wr, P)
    assert a + o.a_pto(wr, P) == pytest.approx(0.0, abs=1e-9)
    assert o.capture_width_ratio(wr, c, P) == pytest.approx(1.0, abs=1e-6)


def test_eta_never_exceeds_one():
    cp = np.geomspace(1e-5, 1.0, 200)
    for w in W:
        assert np.all(o.capture_width_ratio(w, cp, P) <= 1.0 + 1e-9)


def test_optimal_cpto_matches_numeric_maximum():
    cp = np.geomspace(1e-5, 1.0, 400001)
    for w in (1.0, 1.5, 2.0, 2.5):
        best = cp[np.argmax(o.power(w, cp, P))]
        assert best == pytest.approx(float(o.optimal_c_pto(w, P)), rel=2e-3)


def test_closed_form_optimal_power():
    for w in W:
        cpo = o.optimal_c_pto(w, P)
        assert o.power(w, cpo, P) == pytest.approx(o.optimal_power(w, P), rel=1e-10)


def test_optimal_eta_is_bounded_and_below_one_off_resonance():
    eta = o.capture_width_ratio(W, o.optimal_c_pto(W, P), P)
    assert np.all(eta <= 1.0 + 1e-9)
    assert eta.max() > 0.9           # reaches ~1 near PTO resonance
    assert eta.min() < 0.5           # and is poor far from it


def test_power_scales_with_amplitude_squared():
    p2 = o.Params(A=2.0)
    w, cp = 1.8, 0.01
    assert o.power(w, cp, p2) == pytest.approx(4 * o.power(w, cp, P), rel=1e-9)
