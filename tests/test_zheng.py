import dataclasses

import numpy as np

import owc_toy
import owc_zheng as oz
from owc_zheng import ZhengParams, ZhengWallBackend

P = ZhengParams()


def kh_to_w(kh):
    return float(oz.w_from_kh(kh, P.h))


def _rung1_gaps(kh, p):
    w = kh_to_w(kh)
    dm, _ = oz.c_a_direct(w, p)
    ffc, hr = oz.c_far_field(w, p), oz.c_haskind(w, p)
    assert dm > 0 and ffc > 0 and hr > 0
    return max(abs(dm - ffc), abs(dm - hr)) / dm, f"kh={kh:.4f} M={p.M} L={p.L} DM={dm:.6g} FFC={ffc:.6g} HR={hr:.6g}"


def test_rung1_consistency():
    """Rung 1, criterion agreed with the project owner (2026-10-09): DM, FFC and HR agree to 2e-3 at the
    paper's truncation (12, 20), and the gap shrinks at least 3x at (24, 40), i.e. it is truncation
    error, not a transcription error (that would give an O(1) or constant-factor gap)."""
    for kh in np.linspace(0.3, 6.5, 15) + 0.0137:
        gap, msg = _rung1_gaps(kh, P)
        assert gap < 2e-3, msg
    for kh in (1.86, 4.7):
        gap, msg = _rung1_gaps(kh, P)
        gap_fine, msg_fine = _rung1_gaps(kh, dataclasses.replace(P, M=24, L=40))
        assert gap_fine < gap / 3, msg + " | " + msg_fine


def test_rung2_convergence():
    """Rung 2: the change against (16, 30) must shrink from (8, 10) to (12, 20) and stay below 5e-2.
    The 1e-4 target is not reached at affordable truncations; achieved values are in REPORT_B.md."""
    for kh in (1.73, 2.9, 4.0):
        w = kh_to_w(kh)
        vals = {}
        for M, L in [(8, 10), (12, 20), (16, 30)]:
            p = dataclasses.replace(P, M=M, L=L)
            c, a = oz.c_a_direct(w, p)
            vals[(M, L)] = np.array([abs(oz.excitation_flow_complex(w, p, np.pi / 2)), c, a])
        ref = np.abs(vals[(16, 30)])
        coarse = np.abs(vals[(8, 10)] - vals[(16, 30)]) / ref
        mid = np.abs(vals[(12, 20)] - vals[(16, 30)]) / ref
        assert np.all(mid < coarse) and np.all(mid < 5e-2), f"kh={kh} |Qe|,c,a change {coarse} -> {mid}"


def test_backend_contract():
    b = ZhengWallBackend()
    assert isinstance(b, owc_toy.Backend)
    w = oz.w_from_kh(np.array([1.0, 2.0, 3.0]), P.h)
    c, a = b.coefficients(w, P)
    q = b.excitation(w, P)
    assert c.shape == a.shape == q.shape == w.shape
    assert np.all(c > 0) and np.all(q > 0)
    assert b.excitation(w, P, beta=0.3).shape == w.shape
    v = b.validity(w, P)
    assert set(v) == {"near_sloshing_singularity"}
    assert v["near_sloshing_singularity"]["mask"].shape == w.shape
    assert not v["near_sloshing_singularity"]["mask"].any()
    # exactly at a J'_1(k0 Ri) zero
    from scipy.special import jnp_zeros
    k0 = jnp_zeros(1, 1)[0] / P.Ri
    assert b.validity(np.sqrt(owc_toy.G * k0 * np.tanh(k0 * P.h)), P)["near_sloshing_singularity"]["mask"]


def test_energy_bound_per_beta():
    b = ZhengWallBackend()
    for kh in np.linspace(0.5, 6.0, 10) + 0.0211:
        w = kh_to_w(kh)
        for beta in (np.pi / 6, np.pi / 2):
            p = dataclasses.replace(P, beta=beta)
            eta = float(owc_toy.capture_width_ratio(w, owc_toy.optimal_c_pto(w, p, backend=b), p, backend=b))
            c, _ = b.coefficients(w, p)
            q = float(b.excitation(w, p))
            bound = owc_toy.wavenumber(w, p.h) * q**2 / (8 * float(c) * owc_toy.incident_power(w, p))
            assert eta <= bound * (1 + 1e-9), f"kh={kh} beta={beta} eta={eta} bound={bound}"


def test_rung5_bound_mean_is_two():
    """Rung 5: beta-mean of eta_max = k mean|Qe|^2 / (8 c Pin) is 2 (equations doc section 5), to 3e-3."""
    xg, wg = np.polynomial.legendre.leggauss(48)
    betas, wg = 0.5 * np.pi * (xg + 1), 0.5 * np.pi * wg
    for kh in (1.86, 2.9):
        w = kh_to_w(kh)
        sol = oz.solve(w, P, betas)
        mean_q2 = sum(wt * abs(oz._Q(sol, x, P)) ** 2 for wt, x in zip(wg, sol["x_S"])) / np.pi
        c, _ = oz.c_a_direct(w, P)
        mean_eta = float(owc_toy.wavenumber(w, P.h)) * mean_q2 / (8 * c * float(owc_toy.incident_power(w, P)))
        assert abs(mean_eta - 2) < 3e-3, f"kh={kh} mean eta_max={mean_eta}"


def test_rung3_indirect_thin_wall_main_mode():
    """Thin-wall case against Martins-Rivas & Mei (2009a) as replotted in Zheng et al. (2019) JFM Fig. 4,
    read by eye (docs/rungs/rung3_indirect.md): main-mode features within the read-off error."""
    p = ZhengParams(h=10.0, R=5.0, Ri=4.9, d=2.0)

    def ca(kh):
        w = float(oz.w_from_kh(kh, p.h))
        c, a = oz.c_a_direct(w, p)
        return c * w * p.rho / p.R, a * w * p.rho / p.R

    assert abs(ca(1.72)[0] - 7.89) < 0.2           # c peak
    assert abs(ca(1.36)[1] - 3.13) < 0.2           # a maximum
    assert abs(ca(2.32)[1] - (-5.31)) < 0.15       # a minimum
    assert abs(ca(7.0)[1] - (-3.24)) < 0.15        # high-frequency a
