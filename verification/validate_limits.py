"""Validation of both backends against physical limits that do not come from either model.

L1  Long-wave limit of the wall OWC (Zheng backend). For k R -> 0 the chamber is small and the inner
    surface follows the standing wave at the wall, whose elevation at the wall is 2A for any direction
    (incident + perfectly reflected; Zheng Eq. 27 at r = 0). Hence
        |Qe| -> 2 w A pi Ri^2,
    and the Haskind relation (Zheng Eq. 36, integral over beta of a beta-independent |Qe|^2) gives
        c -> pi^2 w^3 Ri^4 Z0(0)^2 / (2 rho g^2 h)     (per A = 1 m).
    The solver's direct-method c (radiation problem) and Qe (scattering problem) must tend to these.
L2  Low-frequency scaling of the radiation conductance. Physical 3D radiation from a small source:
    c ~ w^3 as w -> 0 (from L1). The piston toy has a constant damping B, so c = S^2 B / (B^2 + X^2)
    ~ S^2 B w^2 / K^2: it scales as w^2, a known consequence of the constant-B simplification.
Run:  python verification/validate_limits.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import owc_toy as o  # noqa: E402
import owc_zheng as z  # noqa: E402

G = o.G


def l1_long_wave(khs=(0.4, 0.2, 0.1, 0.05, 0.025), p=None):
    p = p or z.ZhengParams()
    rows = []
    for kh in khs:
        w = float(z.w_from_kh(kh, p.h))
        k0 = kh / p.h
        Z0sq = np.cosh(kh) ** 2 / (0.5 * (1 + np.sinh(2 * kh) / (2 * kh)))
        q_lim = 2 * w * p.A * np.pi * p.Ri**2
        c_lim = np.pi**2 * w**3 * p.Ri**4 * Z0sq / (2 * p.rho * G**2 * p.h) * p.A**0
        c_dm, _ = z.c_a_direct(w, p)
        q = abs(z.excitation_flow_complex(w, p, p.beta))
        rows.append({"kh": kh, "kR": k0 * p.R, "Qe_ratio": q / q_lim, "c_ratio": c_dm / c_lim})
    return rows


def l2_scaling(khs=(0.05, 0.1)):
    """Log-slope d ln c / d ln w at low frequency for both backends."""
    pz, pt = z.ZhengParams(), o.Params()
    out = {}
    wz = z.w_from_kh(np.array(khs), pz.h)
    cz = np.array([z.c_a_direct(float(w), pz)[0] for w in wz])
    out["zheng"] = float(np.log(cz[1] / cz[0]) / np.log(wz[1] / wz[0]))
    wt = np.array([0.05, 0.1])
    ct, _ = o.radiation_coefficients(wt, pt)
    out["toy"] = float(np.log(ct[1] / ct[0]) / np.log(wt[1] / wt[0]))
    return out


def main():
    print("L1 long-wave limit, Zheng backend (default geometry, R/h 0.5, Ri/h 0.4, d/h 0.2):")
    print(f"   {'kh':>6} {'kR':>6} {'|Qe| / 2wA pi Ri^2':>20} {'c_DM / c_limit':>16}")
    for r in l1_long_wave():
        print(f"   {r['kh']:6.3f} {r['kR']:6.3f} {r['Qe_ratio']:20.5f} {r['c_ratio']:16.5f}")
    s = l2_scaling()
    print(f"L2 low-frequency slope d ln c / d ln w: Zheng {s['zheng']:.3f} (physics: 3), toy {s['toy']:.3f} (constant B: 2)")


if __name__ == "__main__":
    main()
