"""Zheng, Zhang & Iglesias (2019) wall-mounted OWC, eigenfunction matching.

Equations: docs/zheng2019_equations.md (the only source). Time factor exp(-i w t).
Plugs into owc_toy through the Backend protocol (ZhengWallBackend).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.integrate import quad
from scipy.linalg import lu_factor, lu_solve
from scipy.optimize import brentq
from scipy.special import h1vp, ive, jv, jvp, kve, yv

import owc_toy
from owc_toy import G


@dataclass(frozen=True)
class ZhengParams:
    h: float = 10.0          # water depth [m]
    R: float = 5.0           # outer radius [m]
    Ri: float = 4.0          # inner radius [m]
    d: float = 2.0           # chamber submergence (draft) [m]
    beta: float = np.pi / 2  # incident wave direction [rad]
    M: int = 12              # circumferential truncation
    L: int = 20              # vertical truncation
    rho: float = 1025.0      # water density [kg/m^3]
    rho0: float = 1.025      # air density [kg/m^3]
    v: float = 340.0         # speed of sound [m/s]
    A: float = 1.0           # incident amplitude [m]
    V0_uses: str = "R"       # "R": V0 = pi R^2 h (paper); "Ri": V0 = pi Ri^2 h

    @property
    def V0(self) -> float:
        return np.pi * (self.R if self.V0_uses == "R" else self.Ri) ** 2 * self.h

    @property
    def S(self) -> float:
        return np.pi * self.Ri**2


def w_from_kh(kh, h=10.0):
    """Angular frequency for a given k0*h."""
    kh = np.asarray(kh, dtype=float)
    return np.sqrt(G * (kh / h) * np.tanh(kh))


def _eps(n):
    return np.where(np.asarray(n) == 0, 1.0, 2.0)


def _wavenumbers(w, p):
    """k_l, l = 0..L (k_0 propagating, k_l evanescent roots of w^2 = -g k tan(k h))."""
    h = p.h
    k = np.empty(p.L + 1)
    k[0] = float(owc_toy.wavenumber(w, h))
    tiny = 1e-12
    for l in range(1, p.L + 1):
        lo, hi = (l - 0.5) * np.pi / h + tiny, l * np.pi / h - tiny
        k[l] = brentq(lambda x: w**2 + G * x * np.tan(x * h), lo, hi, xtol=1e-15, rtol=1e-14)
    return k


def _overlap(k, p):
    """Lm[l, zeta] = int_{-h}^{-d} cos(beta_l (z+h)) Z_zeta(z) dz (sheet 1, A.3). Also returns Z_zeta(0)."""
    h, d, L = p.h, p.d, p.L
    H = h - d
    N = np.empty(L + 1)
    N[0] = 0.5 * (1 + np.sinh(2 * k[0] * h) / (2 * k[0] * h))
    N[1:] = 0.5 * (1 + np.sin(2 * k[1:] * h) / (2 * k[1:] * h))
    Z0 = np.empty(L + 1)
    Z0[0] = np.cosh(k[0] * h) / np.sqrt(N[0])
    Z0[1:] = np.cos(k[1:] * h) / np.sqrt(N[1:])
    Lm = np.empty((L + 1, L + 1))
    for l in range(L + 1):
        sg = (-1.0) ** l
        Lm[l, 0] = sg * H**2 * k[0] * np.sinh(k[0] * H) / np.sqrt(N[0]) / (H**2 * k[0] ** 2 + (l * np.pi) ** 2)
        for z in range(1, L + 1):
            if abs(H * k[z] - l * np.pi) < 1e-9:  # closed form is 0/0
                Lm[l, z] = quad(lambda s: np.cos(l * np.pi * s / H) * np.cos(k[z] * s), 0, H)[0] / np.sqrt(N[z])
            else:
                Lm[l, z] = sg * H**2 * k[z] * np.sin(k[z] * H) / np.sqrt(N[z]) / (H**2 * k[z] ** 2 - (l * np.pi) ** 2)
    return Lm, Z0


def _ring_factors(p):
    """X1,Y1,X2,Y2,X3,Y3 of sheet 3, arrays (M+1, L+1)."""
    M, L, R, Ri = p.M, p.L, p.R, p.Ri
    m = np.arange(M + 1, dtype=float)
    X1, Y1, X2, Y2, X3, Y3 = (np.zeros((M + 1, L + 1)) for _ in range(6))
    # l = 0
    X1[0, 0], Y1[0, 0], X2[0, 0], Y2[0, 0], X3[0, 0], Y3[0, 0] = 0.0, 1 / Ri, 0.0, 1 / R, 1.0, 1 + np.log(Ri / R)
    mm = m[1:]
    X1[1:, 0] = (mm / R) * (Ri / R) ** (mm - 1)
    Y1[1:, 0] = -(mm / R) * (R / Ri) ** (mm + 1)
    X2[1:, 0] = mm / R
    Y2[1:, 0] = -mm / R
    X3[1:, 0] = (Ri / R) ** mm
    Y3[1:, 0] = (R / Ri) ** mm
    if L >= 1:
        mi = m[:, None].astype(int)
        b = (np.arange(1, L + 1) * np.pi / (p.h - p.d))[None, :]
        xi, xR = b * Ri, b * R

        def ldI(x):
            return (ive(abs(mi - 1), x) + ive(mi + 1, x)) / (2 * ive(mi, x))

        def ldK(x):
            return -(kve(abs(mi - 1), x) + kve(mi + 1, x)) / (2 * kve(mi, x))

        rI = ive(mi, xi) / ive(mi, xR) * np.exp(xi - xR)   # I_m(b Ri)/I_m(b R)
        rK = kve(mi, xi) / kve(mi, xR) * np.exp(xR - xi)   # K_m(b Ri)/K_m(b R)
        X1[:, 1:], Y1[:, 1:] = b * ldI(xi) * rI, b * ldK(xi) * rK
        X2[:, 1:], Y2[:, 1:] = b * ldI(xR), b * ldK(xR)
        X3[:, 1:], Y3[:, 1:] = rI, rK
    return X1, Y1, X2, Y2, X3, Y3


@lru_cache(maxsize=16)
def _factor(w: float, p: ZhengParams):
    """Build and LU-factorise the sheet-3 matrix for (w, p).

    Unknown/equation ordering (same for both): blocks [A | C | D | E]; A has index
    (tau + M) * (L+1) + l for tau = -M..M, and C, D, E have index m * (L+1) + l for m = 0..M.
    Equation blocks: A.1 (rows of A), A.4, A.8, A.11 (rows of C, D, E positions respectively).
    """
    M, L, h, d, R, Ri = p.M, p.L, p.h, p.d, p.R, p.Ri
    nl, H = L + 1, p.h - p.d
    k = _wavenumbers(w, p)
    Lm, Zs = _overlap(k, p)
    X1, Y1, X2, Y2, X3, Y3 = _ring_factors(p)
    # outer factor Z2 and inner factor G, (M+1, L+1)
    mi = np.arange(M + 1)[:, None]
    Z2 = np.empty((M + 1, nl), complex)
    Gf = np.empty((M + 1, nl))
    x0 = k[0] * R
    Z2[:, 0] = k[0] * h1vp(np.arange(M + 1), x0) / (jv(np.arange(M + 1), x0) + 1j * yv(np.arange(M + 1), x0))
    xi0 = k[0] * Ri
    Gf[:, 0] = jv(np.arange(M + 1), xi0) / (k[0] * jvp(np.arange(M + 1), xi0))
    if L >= 1:
        kl = k[None, 1:]
        xK = kl * R
        Z2[:, 1:] = -kl * (kve(abs(mi - 1), xK) + kve(mi + 1, xK)) / (2 * kve(mi, xK))
        xI = kl * Ri
        Gf[:, 1:] = 2 * ive(mi, xI) / (kl * (ive(abs(mi - 1), xI) + ive(mi + 1, xI)))
    # coupling coefficients
    T1 = np.zeros((2 * M + 1, M + 1), complex)
    for ti, t in enumerate(range(-M, M + 1)):
        for m in range(M + 1):
            T1[ti, m] = (np.pi / _eps(abs(t))) if m == abs(t) else 1j * t * ((-1.0) ** abs(t - m) - 1) / (t * t - m * m)
    T8 = np.zeros((M + 1, 2 * M + 1), complex)
    for t in range(M + 1):
        for mi_, m in enumerate(range(-M, M + 1)):
            if abs(m) == t:
                T8[t, mi_] = np.pi if t == 0 else np.pi / 2
            else:
                T8[t, mi_] = -1j * m * ((-1.0) ** abs(m - t) - 1) / (m * m - t * t)
    Gfull = np.vstack([Gf[abs(m)] for m in range(-M, M + 1)])  # (2M+1, nl)

    nA, nC = (2 * M + 1) * nl, (M + 1) * nl
    N = nA + 3 * nC
    mat = np.zeros((N, N), complex)
    r1, r8 = slice(0, nA), slice(nA + nC, nA + 2 * nC)
    cA, cC, cD, cE = slice(0, nA), slice(nA, nA + nC), slice(nA + nC, nA + 2 * nC), slice(nA + 2 * nC, N)
    # A.1
    mat[r1, cA] = 2 * np.pi * h * np.eye(nA)
    mat[r1, cC] = -np.einsum("tm,ml,lz->tzml", T1, X1, Lm).reshape(nA, nC)
    mat[r1, cD] = -np.einsum("tm,ml,lz->tzml", T1, Y1, Lm).reshape(nA, nC)
    # A.4
    for t in range(M + 1):
        rows = np.arange(nA + t * nl, nA + (t + 1) * nl)
        cols = np.arange(t * nl, (t + 1) * nl)
        mat[np.ix_(rows, nA + cols)] = Lm.T * X2[t][None, :]
        mat[np.ix_(rows, nA + nC + cols)] = Lm.T * Y2[t][None, :]
        mat[np.ix_(rows, nA + 2 * nC + cols)] = -h * np.diag(Z2[t])
    # A.8
    mat[r8, cA] = np.einsum("tm,ml,zl->tzml", T8, Gfull, Lm).reshape(nC, nA)
    eps_z = _eps(np.arange(nl))
    pre = np.pi * H / (_eps(np.arange(M + 1))[:, None] * eps_z[None, :])
    idx = np.arange(nC)
    mat[nA + nC + idx, nA + idx] = -(pre * X3).ravel()
    mat[nA + nC + idx, nA + nC + idx] = -(pre * Y3).ravel()
    # A.11
    dg = np.tile(H / eps_z, M + 1)
    mat[nA + 2 * nC + idx, nA + idx] = dg
    mat[nA + 2 * nC + idx, nA + nC + idx] = dg
    for t in range(M + 1):
        sl = slice(nA + 2 * nC + t * nl, nA + 2 * nC + (t + 1) * nl)
        mat[sl, nA + 2 * nC + t * nl: nA + 2 * nC + (t + 1) * nl] = -Lm
    return dict(lu=lu_factor(mat), k=k, Lm=Lm, Zs=Zs, N=N, nA=nA, nC=nC, nl=nl)


def _rhs_R(f, p, w):
    b = np.zeros(f["N"], complex)
    b[f["nA"] + f["nC"]] = 1j * np.pi * (p.h - p.d) / (p.rho * w)  # f3, tau = zeta = 0
    return b


def _rhs_S(f, p, w, beta):
    M, nl, nA, nC = p.M, f["nl"], f["nA"], f["nC"]
    k0, Z00, Lm = f["k"][0], f["Zs"][0], f["Lm"]
    t = np.arange(M + 1)
    ph = _eps(t) * (-1j) ** t * np.cos(t * beta)
    b = np.zeros(f["N"], complex)
    pref = -2j * G * p.A / (w * Z00)
    b[nA + t * nl] = pref * k0 * p.h * ph * jvp(t, k0 * p.R)                                  # f2
    b[nA + 2 * nC + (t[:, None] * nl + np.arange(nl)[None, :])] = pref * Lm[:, 0][None, :] * (ph * jv(t, k0 * p.R))[:, None]  # f4
    return b


def solve(w, p: ZhengParams, betas=()):
    """Solve R and S(beta) for scalar w. Returns dict with k (k_0..k_L), Z0 (Z_l(0)), x_R and x_S (rows per beta).

    Coefficient vector layout: see _factor.
    """
    w = float(w)
    f = _factor(w, p)
    betas = np.atleast_1d(np.asarray(betas, dtype=float))
    cols = [_rhs_R(f, p, w)] + [_rhs_S(f, p, w, b) for b in betas]
    X = lu_solve(f["lu"], np.array(cols).T)
    return dict(w=w, k=f["k"], Z0=f["Zs"], nl=f["nl"], nA=f["nA"], nC=f["nC"], M=p.M, betas=betas,
                x_R=X[:, 0], x_S=X[:, 1:].T)


def _Q(sol, x, p):
    """Eq. 33/34 flow from a coefficient vector x (the A_{0,l} block)."""
    l0 = p.M * sol["nl"]
    A0 = x[l0:l0 + sol["nl"]]
    k, Z = sol["k"], sol["Z0"]
    s = -A0[0] * Z[0] / k[0] ** 2 + np.sum(A0[1:] * Z[1:] / k[1:] ** 2)
    return 2 * np.pi * sol["w"] ** 2 * p.Ri / G * s


def excitation_flow_complex(w, p, beta):
    return _Q(s := solve(w, p, [beta]), s["x_S"][0], p)


def c_a_direct(w, p):
    q = _Q(s := solve(w, p), s["x_R"], p)
    return -q.real, q.imag


def c_far_field(w, p):
    s = solve(w, p)
    m = np.arange(p.M + 1)
    E0 = s["x_R"][s["nA"] + 2 * s["nC"]:][m * s["nl"]]
    x = s["k"][0] * p.R
    H2 = jv(m, x) ** 2 + yv(m, x) ** 2
    return 2 * p.rho * s["w"] * p.h * np.sum(np.abs(E0) ** 2 / (_eps(m) * H2))


def c_haskind(w, p, n_beta=64):
    xg, wg = np.polynomial.legendre.leggauss(n_beta)
    betas = 0.5 * np.pi * (xg + 1)
    s = solve(w, p, betas)
    q2 = np.array([abs(_Q(s, x, p) / p.A) ** 2 for x in s["x_S"]])
    integral = 0.5 * np.pi * np.sum(wg * q2)
    return s["w"] * s["Z0"][0] ** 2 / (8 * np.pi * p.rho * G**2 * p.h) * integral


class ZhengWallBackend:
    name = "Zheng et al. 2019 wall OWC"

    def coefficients(self, w, p):
        w = np.asarray(w, dtype=float)
        out = np.array([c_a_direct(x, p) for x in w.ravel()]).reshape(w.shape + (2,))
        return out[..., 0], out[..., 1]

    def excitation(self, w, p, beta=None):
        w = np.asarray(w, dtype=float)
        b = p.beta if beta is None else beta
        return np.array([abs(excitation_flow_complex(x, p, b)) for x in w.ravel()]).reshape(w.shape)

    def validity(self, w, p):
        w = np.asarray(w, dtype=float)
        k0 = owc_toy.wavenumber(w, p.h)
        # relative to the Bessel scale, so small high-order J'_m (no zero there) do not trigger
        x = k0 * p.Ri
        dj = np.min([np.abs(jvp(m, x)) / (0.5 * (np.abs(jv(abs(m - 1), x)) + np.abs(jv(m + 1, x)))) for m in range(p.M + 1)], axis=0)
        return {"near_sloshing_singularity": {
            "mask": dj < 1e-8,
            "message": "Near a closed-cylinder sloshing frequency: the inner-region normalisation is singular here.",
        }}


ZHENG = ZhengWallBackend()
