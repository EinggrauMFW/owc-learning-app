"""Toy single-chamber OWC in the frequency domain (regular waves, SI units).

Purpose: learn the one equation behind OWC papers (Zheng et al. 2019, Eq. 2):

    [ (c + cPTO) - i (a + aPTO) ] p = Qe

    p     air-pressure amplitude in the chamber           [Pa]
    Qe    excitation volume flow (pressure held at zero)  [m^3/s]
    c     radiation conductance ("radiation damping")     [m^3/s/Pa]
    a     radiation susceptance ("added-mass-like")       [m^3/s/Pa]
    cPTO  turbine conductance (the PTO "damping")         [m^3/s/Pa]
    aPTO  air-compressibility susceptance = w*V0/(v^2*rho0) [m^3/s/Pa]

Time convention exp(-i w t), as in the paper.

IMPORTANT: this is NOT the paper's model. In the paper c, a and Qe come from a
3D potential-flow solution (eigen-function matching). Here they come from a
one-degree-of-freedom piston: a water column of effective length L with a fixed
damping ratio. It is a learning model, tuned only so that the resonance falls near
kh ~ 2.4 for h = 10 m. Qe is obtained from c by the Haskind relation for an
isolated axisymmetric absorber, which makes eta_max = 1 by construction. The
wall-reflection effect (eta up to ~2 in the paper) is NOT modelled.

Wave period T, angular frequency w = 2 pi / T, wave number k from the finite-depth
dispersion relation w^2 = g k tanh(k h). Wave power per metre of crest for a
regular wave of amplitude A: Pin = 0.5 rho g A^2 cg.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol, runtime_checkable

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import j1

G = 9.81  # m/s^2


@dataclass(frozen=True)
class Params:
    h: float = 10.0        # water depth [m]
    r_in: float = 4.0      # inner chamber radius [m] (piston area S = pi r_in^2)
    L: float = 4.2         # effective water-column length (incl. added mass) [m]
    zeta: float = 0.3      # radiation damping ratio of the piston (toy value)
    H_air: float = 5.0     # air-chamber height, V0 = S * H_air [m] (paper uses V0 = pi R^2 h, i.e. 10 m here)
    rho: float = 1025.0    # seawater density [kg/m^3]
    rho0: float = 1.2      # air density [kg/m^3] (my choice; not from the paper)
    v: float = 340.0       # speed of sound in air [m/s] (paper value)
    A: float = 1.0         # incident wave amplitude [m] (results scale with A^2)
    damping: str = "constant"  # "constant": B = 2 zeta sqrt(K m); "froude_krylov": B(w) from F-K + Haskind

    @property
    def S(self) -> float:
        return np.pi * self.r_in**2

    @property
    def V0(self) -> float:
        return self.S * self.H_air


@runtime_checkable
class Backend(Protocol):
    """Source of c, a [m^3/s/Pa] and |Qe| [m^3/s]. Everything else is backend-independent."""
    name: str
    def coefficients(self, w, p) -> tuple[np.ndarray, np.ndarray]: ...
    def excitation(self, w, p, beta: float | None = None) -> np.ndarray: ...
    def validity(self, w, p) -> dict: ...


def wavenumber(w, h):
    """Solve w^2 = g k tanh(k h) for k (Newton iterations), w in rad/s."""
    k = w**2 / G                      # deep-water first guess
    with np.errstate(over="ignore"):  # cosh(kh) overflows to inf in very deep water: that term is then 0
        return _newton_k(k, w, h)


def _newton_k(k, w, h):
    for _ in range(60):
        f = G * k * np.tanh(k * h) - w**2
        df = G * np.tanh(k * h) + G * k * h / np.cosh(k * h) ** 2
        k = k - f / df
    return k


def group_velocity(w, h):
    k = wavenumber(w, h)
    with np.errstate(over="ignore"):  # sinh overflow in deep water: the correction term is 0
        return 0.5 * (w / k) * (1.0 + 2.0 * k * h / np.sinh(2.0 * k * h))


def incident_power(w, p: Params):
    """Wave power per metre of crest, regular wave [W/m]."""
    return 0.5 * p.rho * G * p.A**2 * group_velocity(w, p.h)


def radiation_coefficients(w, p: Params):
    """Toy c(w), a(w) from a damped piston of area S and water-column mass m.

    Piston admittance  Y = S^2 / (B - i X),  X = w m - rho g S / w, B = 2 zeta sqrt(k m)
    -> Y = c - i a  with  c = S^2 B/(B^2+X^2),  a = -S^2 X/(B^2+X^2).
    a > 0 below the water-column natural frequency, a < 0 above (as in the paper's Fig. 5c).
    """
    m = p.rho * p.S * p.L
    kspring = p.rho * G * p.S
    B = damping_coefficient(w, p) if p.damping == "froude_krylov" else 2.0 * p.zeta * np.sqrt(kspring * m)
    X = w * m - kspring / w
    den = B**2 + X**2
    return p.S**2 * B / den, -p.S**2 * X / den


def damping_coefficient(w, p: Params):
    """Frequency-dependent radiation damping B(w) [kg/s] (used when p.damping == "froude_krylov").

    Haskind relation for an axisymmetric heaving absorber, B = k |F_e|^2 / (8 J), with the
    Froude-Krylov force on a surface disk of radius r_in, F_e = rho g A S 2 J1(k r_in)/(k r_in),
    and J = rho g A^2 cg / 2:  B = k rho g S^2 (2 J1(ka)/ka)^2 / (4 cg)   (A cancels).
    Diffraction is neglected (an estimate). Long waves: B ~ w, so c ~ w^3 as in 3D radiation.
    See VERIFICATION.md section 4.
    """
    k = wavenumber(w, p.h)
    ka = k * p.r_in
    return k * p.rho * G * p.S**2 * (2 * j1(ka) / ka) ** 2 / (4 * group_velocity(w, p.h))


def natural_frequency(p: Params):
    """Water-column natural frequency without PTO [rad/s]: sqrt(g / L)."""
    return np.sqrt(G / p.L)


def a_pto(w, p: Params):
    """Air-compressibility susceptance aPTO = w V0 / (v^2 rho0)  [m^3/s/Pa]."""
    return w * p.V0 / (p.v**2 * p.rho0)


def excitation_flow(w, p: Params):
    """|Qe| from the Haskind relation for an isolated axisymmetric absorber.

    Max power = |Qe|^2 / (8 c) must equal Pin / k  (capture width 1/k)  =>
    |Qe|^2 = 8 c Pin / k.   Returns the amplitude [m^3/s] (phase taken as 0).
    """
    c, _ = radiation_coefficients(w, p)
    k = wavenumber(w, p.h)
    return np.sqrt(8.0 * c * incident_power(w, p) / k)


class PistonBackend:
    """The toy damped-piston model behind the Backend interface."""
    name = "piston (toy)"

    def coefficients(self, w, p):
        return radiation_coefficients(w, p)

    def excitation(self, w, p, beta=None):
        return excitation_flow(w, p)  # isolated axisymmetric absorber: no beta dependence

    def validity(self, w, p):
        """Named boolean masks (same shape as w) with a message each."""
        w = np.asarray(w, dtype=float)
        k = wavenumber(w, p.h)
        return {
            "k_rin_gt_1": {
                "mask": k * p.r_in > 1,
                "message": "k r_in > 1: the chamber is not small compared with the wavelength. "
                           "The piston idea is weak here (this is the toy model's own assumption, "
                           "not a literature criterion).",
            },
            "kh_lt_0p5": {
                "mask": k * p.h < 0.5,
                "message": "kh < 0.5: very long waves; this toy model is not meaningful here.",
            },
            "no_pto_resonance": {
                "mask": np.full(np.shape(w), not has_pto_resonance(p, self)),
                "message": "No PTO resonance: a + aPTO > 0 at every frequency for these inputs. "
                           "This is a result, not an error.",
            },
        }


PISTON = PistonBackend()


def pressure(w, c_pto, p: Params, backend: Backend = PISTON):
    """Complex chamber-pressure amplitude from Eq. (2) [Pa]."""
    c, a = backend.coefficients(w, p)
    return backend.excitation(w, p) / ((c + c_pto) - 1j * (a + a_pto(w, p)))


def power(w, c_pto, p: Params, backend: Backend = PISTON):
    """Time-averaged turbine power P = 0.5 cPTO |p|^2 [W]."""
    return 0.5 * c_pto * np.abs(pressure(w, c_pto, p, backend=backend)) ** 2


def capture_width_ratio(w, c_pto, p: Params, backend: Backend = PISTON):
    """eta = k P / Pin (paper Eq. 6). Dimensionless; eta <= 1 for this isolated model."""
    return wavenumber(w, p.h) * power(w, c_pto, p, backend=backend) / incident_power(w, p)


def optimal_c_pto(w, p: Params, backend: Backend = PISTON):
    """cPTO that maximises P at each frequency: sqrt(c^2 + (a + aPTO)^2) (paper Eq. 39)."""
    c, a = backend.coefficients(w, p)
    return np.sqrt(c**2 + (a + a_pto(w, p)) ** 2)


def optimal_power(w, p: Params, backend: Backend = PISTON):
    """Closed form P_opt = |Qe|^2 / (4 (c + cPTO_opt)) [W]."""
    c, _ = backend.coefficients(w, p)
    return backend.excitation(w, p) ** 2 / (4.0 * (c + optimal_c_pto(w, p, backend=backend)))


def resonance_frequency_with_pto(p: Params, w_lo=0.3, w_hi=4.0, n=40001, backend: Backend = PISTON):
    """Frequency where a + aPTO = 0 (pressure in phase with Qe) [rad/s]."""
    w = np.linspace(w_lo, w_hi, n)
    _, a = backend.coefficients(w, p)
    s = a + a_pto(w, p)
    i = np.where(np.sign(s[:-1]) != np.sign(s[1:]))[0]
    if len(i) == 0:
        raise ValueError("no zero crossing of a + aPTO in range")
    j = i[0]
    return w[j] - s[j] * (w[j + 1] - w[j]) / (s[j + 1] - s[j])


def has_pto_resonance(p: Params, backend: Backend = PISTON, w_lo=0.1, w_hi=10.0) -> bool:
    """True if a + aPTO < 0 somewhere in [w_lo, w_hi] (then it crosses zero: a PTO resonance exists).

    For the piston a + aPTO > 0 at both ends, so a negative minimum <=> a crossing.
    Grid minimum refined with a bounded scalar minimiser so thin dips near the threshold are not missed.
    """
    w = np.linspace(w_lo, w_hi, 20001)

    def s(x):
        _, a = backend.coefficients(x, p)
        return a + a_pto(x, p)

    sw = s(w)
    i = int(np.argmin(sw))
    res = minimize_scalar(lambda x: float(s(x)), bounds=(w[max(i - 1, 0)], w[min(i + 1, len(w) - 1)]),
                          method="bounded", options={"xatol": 1e-12})
    return bool(min(sw[i], res.fun) < 0)


def critical_H_air(p: Params, lo=0.5, hi=20.0, tol=1e-4, backend: Backend = PISTON):
    """Air-chamber height [m] above which the PTO resonance disappears, by bisection.

    Returns (H_crit, tol): a resonance exists at H_crit - tol and not at H_crit + tol.
    """
    if not has_pto_resonance(replace(p, H_air=lo), backend):
        raise ValueError("no PTO resonance at lo: lower lo")
    if has_pto_resonance(replace(p, H_air=hi), backend):
        raise ValueError("PTO resonance still present at hi: raise hi")
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if has_pto_resonance(replace(p, H_air=mid), backend):
            lo = mid
        else:
            hi = mid
    return ((lo + hi) / 2, tol)


def zeta_froude_krylov(p: Params, w: float | None = None) -> tuple[float, float]:
    """Damping ratio that makes the piston consistent with an independent force estimate [-].

    Haskind relation for an axisymmetric heaving absorber (maximum capture width 1/k):
    B = k |F_e|^2 / (8 Pin), with F_e from Froude-Krylov on a surface disk of radius r_in,
    F_FK = rho g A S 2 J1(k r_in)/(k r_in) (diffraction neglected: an estimate, not a solution).
    Evaluated at w (default: the natural frequency sqrt(g/L), which does not depend on zeta, so the
    result does not change when zeta is set to it). Real damping varies with frequency and the toy's
    is constant, so the answer depends on w: 0.54 at the natural frequency, 0.63 at the toy-default
    PTO resonance for the default inputs. Returns (zeta, w_used). See VERIFICATION.md section 4.
    """
    w = natural_frequency(p) if w is None else w
    k = float(wavenumber(w, p.h))
    ka = k * p.r_in
    F = p.rho * G * p.A * p.S * 2 * j1(ka) / ka
    B = k * F**2 / (8 * float(incident_power(w, p)))
    return B / (2 * np.sqrt(p.rho * G * p.S * p.rho * p.S * p.L)), float(w)
