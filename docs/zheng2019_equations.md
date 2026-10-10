# Zheng, Zhang and Iglesias (2019): equations used by `owc_zheng.py`

Source: Marine Structures 66 (2019) 121-135, doi 10.1016/j.marstruc.2019.04.001. Transcribed by Opus from page images of the published PDF (pp. 123-126, 128, 133-134; the PDF is not included in this repository). This file is the **only** source of equations for the implementation. If code disagrees with it, the code is wrong. If this file seems wrong, stop and report; do not "fix" a sign to make results look better.

Every item is tagged:
- `[paper]`: transcribed as printed.
- `[paper, typo fixed]`: the printed form contradicts its own derivation; the fix and its reason are given.
- `[derived]`: not printed in the paper; derived here from the boundary-value problem.

## 0. Conventions

- Time factor exp(-i w t). Real quantity = Re(X exp(-i w t)). `[paper, p. 123]`
- z up, z = 0 still water level, z = -h seabed.
- Polar (r, theta) about the cylinder axis. The wall lies along theta = 0 and theta = pi, and the sea is 0 < theta < pi.
- Incident wave direction beta, as in Fig. 1b. `[paper]`
- Geometry: outer radius R, inner radius Ri, chamber open from z = -d down to the seabed. The wall is the ring Ri <= r <= R for -d <= z <= 0 on the sea side. The water column is the full disk r <= Ri; its landward half (pi < theta < 2 pi) is a cavity in the wall, closed at r = Ri over the full depth. `[paper, Eqs. 8-15, Fig. 1]`
- eps_0 = 1 and eps_m = 2 for m != 0. `[paper]`

## 1. Vertical eigenfunctions `[paper, Eqs. 19-21]`

- k0 > 0 solves w^2 = g k0 tanh(k0 h).
- k_l for l = 1, 2, ... solves w^2 = -g k_l tan(k_l h), with the root in ((l - 1/2) pi / h, l pi / h).
- Z_0(z) = N0^-1/2 cosh k0(z + h), with N0 = 1/2 [1 + sinh(2 k0 h) / (2 k0 h)].
- Z_l(z) = N_l^-1/2 cos k_l(z + h), with N_l = 1/2 [1 + sin(2 k_l h) / (2 k_l h)].
- Property `[derived]`: the integral from -h to 0 of Z_l Z_n dz equals h delta_ln, and Z_l'(0) = (w^2 / g) Z_l(0) for every l.

Ring vertical modes: beta_l = l pi / (h - d), l = 0, 1, ... `[paper, Eq. 24]` (the name beta_l is unrelated to the wave direction beta).

Overlap integral, ring mode l against eigenfunction ζ, L_{l,ζ} = integral from -h to -d of cos[beta_l (z + h)] Z_ζ(z) dz `[paper, Eq. A.3]`:
- ζ = 0: (-1)^l (h-d)^2 k0 Z0(0) sinh[k0 (h-d)] / ( [(h-d)^2 k0^2 + l^2 pi^2] cosh(k0 h) )
- ζ >= 1: (-1)^l (h-d)^2 k_ζ Z_ζ(0) sin[k_ζ (h-d)] / ( [(h-d)^2 k_ζ^2 - l^2 pi^2] cos(k_ζ h) )

Both closed forms were re-derived by direct integration `[derived, agrees]`. Guard: if (h-d) k_ζ is within 1e-9 of l pi, evaluate the integral numerically instead (the closed form is 0/0 there).

**Index rule used below:** L[ring index, eigenfunction index]. A.1 and A.4 use L_{l,ζ} (l ring, ζ eigenfunction). A.8 and A.11 use L_{ζ,l} (ζ ring, l eigenfunction). It is the same function.

## 2. Potentials in the three regions

Truncation: inner m from -M to M; ring and outer m from 0 to M; every vertical sum l from 0 to L. `[paper, after A.12]`

**Region I (inner), r <= Ri.** `[paper, Eqs. 16-18]`

Phi_in = sum over m from -M to M and l from 0 to L of [ Ĩ_m(k_l r) / (k_l Ĩ'_m(k_l Ri)) ] A_{m,l} Z_l(z) e^{i m theta}, plus Phi_p,in.

- Ĩ_m = J_m for l = 0, and I_m for l >= 1. The prime is the derivative with respect to the argument.
- Phi_p,in = 0 for S, and -i / (rho w) for R.

**Region II (ring), Ri <= r <= R, 0 <= theta <= pi, -h <= z <= -d.** `[paper, Eqs. 22-23]`

Phi_ring = sum over m from 0 to M of [ F_m(r) + sum over l from 1 to L of ( C_{m,l} I_m(beta_l r) / I_m(beta_l R) + D_{m,l} K_m(beta_l r) / K_m(beta_l R) ) cos beta_l(z + h) ] cos m theta, where:
- F_0(r) = C_{0,0} + D_{0,0} [1 + ln(r / R)]
- F_m(r) = C_{m,0} (r/R)^m + D_{m,0} (r/R)^-m for m >= 1

**Region III (outer), r >= R, 0 <= theta <= pi.** `[paper, Eqs. 25-28]`

Phi_out = sum over m from 0 to M and l from 0 to L of E_{m,l} [ K̃_m(k_l r) / K̃_m(k_l R) ] cos(m theta) Z_l(z), plus Phi_p,out.
- K̃_m = H_m (Hankel, first kind) for l = 0, and K_m for l >= 1.
- Phi_p,out = Phi_I for S, and 0 for R.
- Phi_I = -(2 i g A / w) (Z_0(z) / Z_0(0)) times the sum over m >= 0 of eps_m (-i)^m J_m(k0 r) cos(m beta) cos(m theta). This is the incident plus wall-reflected wave. `[paper, Eq. 27]`

## 3. Linear system `[paper, Appendix A; each projection re-derived, agrees]`

Unknowns per problem (chi = S or R):
- A_{τ,l}: τ from -M to M, l from 0 to L.
- C_{τ,l}, D_{τ,l}, E_{τ,l}: τ from 0 to M, l from 0 to L.

That is (2M+1)(L+1) + 3(M+1)(L+1) unknowns, with the same number of equations. **The matrix does not depend on chi or beta; only the right-hand side does.** Factorise once per w and solve S for every beta, and R, as extra right-hand sides.

**Radial factor values** (ring functions at r = Ri and r = R) `[paper, Eqs. A.2, A.6, A.10]`:

| Factor | l = 0 | l >= 1 |
| --- | --- | --- |
| X1_{m,l} = d/dr of C-function at r = Ri | (m/R)(Ri/R)^(m-1) (equals 0 for m = 0) | beta_l I'_m(beta_l Ri) / I_m(beta_l R) |
| Y1_{m,l} = d/dr of D-function at r = Ri | m = 0: 1/Ri; m >= 1: -(m/R)(R/Ri)^(m+1) | beta_l K'_m(beta_l Ri) / K_m(beta_l R) |
| X2_{m,l} = d/dr of C-function at r = R | m/R | beta_l I'_m(beta_l R) / I_m(beta_l R) |
| Y2_{m,l} = d/dr of D-function at r = R | m = 0: 1/R; m >= 1: -m/R | beta_l K'_m(beta_l R) / K_m(beta_l R) |
| X3_{m,l} = C-function at r = Ri | (Ri/R)^m | I_m(beta_l Ri) / I_m(beta_l R) |
| Y3_{m,l} = D-function at r = Ri | m = 0: 1 + ln(Ri/R); m >= 1: (R/Ri)^m | K_m(beta_l Ri) / K_m(beta_l R) |

Outer-region factor `[paper, Eq. A.7]`:
- Z2_{m,0} = k0 H'_m(k0 R) / H_m(k0 R)
- Z2_{m,l} = k_l K'_m(k_l R) / K_m(k_l R) for l >= 1

Inner factor at r = Ri: G_{m,l} = Ĩ_m(k_l Ri) / (k_l Ĩ'_m(k_l Ri)). It depends on |m| only, because J_-m = (-1)^m J_m and I_-m = I_m. G is singular where J'_m(k0 Ri) = 0 (a closed-cylinder sloshing frequency); report any frequency within 1e-8 of such a zero rather than hiding it.

**(A.1) Normal velocity at r = Ri** (Eq. 29), projected on Z_ζ e^{-iτθ} over z in [-h, 0] and theta in [0, 2 pi]. For τ from -M to M and ζ from 0 to L:

2 pi h A_{τ,ζ} = sum over l from 0 to L of [ (pi / eps_|τ|)(X1_{|τ|,l} C_{|τ|,l} + Y1_{|τ|,l} D_{|τ|,l}) + i times the sum over m from 0 to M, m != |τ|, of τ [(-1)^(τ-m) - 1] / (τ^2 - m^2) (X1_{m,l} C_{m,l} + Y1_{m,l} D_{m,l}) ] L_{l,ζ}

There is no forcing term for either S or R. (The particular solution of region I is constant in r; Phi_I lives in region III.)

**(A.4) Normal velocity at r = R** (Eq. 30), projected on Z_ζ cos τθ over [-h, 0] and [0, pi], then divided by pi / eps_τ. For τ from 0 to M and ζ from 0 to L:

sum over l from 0 to L of (X2_{τ,l} C_{τ,l} + Y2_{τ,l} D_{τ,l}) L_{l,ζ} - h Z2_{τ,ζ} E_{τ,ζ} = f2

- f2 for S: -(2 delta_{ζ,0} i g A k0 h / (w Z0(0))) eps_τ (-i)^τ J'_τ(k0 R) cos(τ beta)
- f2 for R: 0

**(A.8) Potential at r = Ri** (Eq. 31), projected on cos beta_ζ(z+h) cos τθ over [-h, -d] and [0, pi]. For τ from 0 to M and ζ from 0 to L:

sum over l from 0 to L of ( (pi/2)[ G_{τ,l} A_{τ,l} + G_{-τ,l} A_{-τ,l} ] - i times the sum over m from -M to M, m != ±τ, of m [(-1)^(m-τ) - 1] / (m^2 - τ^2) G_{m,l} A_{m,l} ) L_{ζ,l}
  = (pi (h-d) / (eps_τ eps_ζ)) (X3_{τ,ζ} C_{τ,ζ} + Y3_{τ,ζ} D_{τ,ζ}) + f3

- For τ = 0 the bracket is (pi/2)(2 G A_{0,l}) = pi G_{0,l} A_{0,l}.
- f3 for S: 0
- f3 for R: delta_{τ,0} delta_{ζ,0} i pi (h - d) / (rho w)

**(A.11) Potential at r = R** (Eq. 32), projected on cos beta_ζ(z+h) cos τθ, then divided by pi / eps_τ. For τ from 0 to M and ζ from 0 to L:

((h - d) / eps_ζ)(C_{τ,ζ} + D_{τ,ζ}) - sum over l from 0 to L of E_{τ,l} L_{ζ,l} = f4

- f4 for S: -(2 eps_τ i g A L_{ζ,0} / (w Z0(0))) (-i)^τ J_τ(k0 R) cos(τ beta)
- f4 for R: 0

## 4. Outputs

**Excitation volume flow** `[paper, Eq. 33, typo fixed]`:

Qe = (2 pi w^2 Ri / g) ( -A^S_{0,0} Z_0(0) / k0^2 + sum over l from 1 to L of A^S_{0,l} Z_l(0) / k_l^2 )

- The paper prints Z_0(z) in the first term, and superscript D for the coefficients. Integrating ∂Phi_S/∂z = (w^2/g) Phi_S over the disk r <= Ri at z = 0 gives Z_0(0), and the coefficients are those of Phi_S in region I. `[derived]`
- The disk integrals used: the integral from 0 to Ri of J_0(k0 r) r dr is -Ri J_0'(k0 Ri)/k0, and the integral from 0 to Ri of I_0(k_l r) r dr is Ri I_0'(k_l Ri)/k_l.

**Radiation, direct method (DM)** `[paper, Eq. 34, same typo fixed]`:

-(c - i a) = Q_R = (2 pi w^2 Ri / g) ( -A^R_{0,0} Z_0(0) / k0^2 + sum over l from 1 to L of A^R_{0,l} Z_l(0) / k_l^2 )

The particular solution -i/(rho w) contributes nothing, because the free-surface condition Eq. 10 cancels it. `[derived]`

**Radiation, far-field coefficients (FFC)** `[paper, Eq. 35; re-derived from the radiated energy flux through a half-cylinder at infinity, agrees]`:

c = 2 rho w h times the sum over m from 0 to M of (1/eps_m) |E^R_{m,0}|^2 / |H_m(k0 R)|^2

**Radiation, Haskind relation (HR)** `[paper, Eq. 36]`:

c = (w Z_0(0)^2 / (8 pi rho g^2 h)) times the integral from 0 to pi of |Qe(beta)|^2 d beta

**UNRESOLVED (notation):** this is dimensionally consistent only if Qe is per unit incident amplitude, i.e. |Qe/A|^2 with A in metres. Implement it with |Qe(beta)/A|^2 and let rung 1 decide. If DM and HR then differ by a constant factor, report the factor; do not absorb it.

**Power and efficiency** `[paper, Eqs. 2, 5, 6, 39]` use the backend-independent functions in `owc_toy.py` (pressure, power, capture_width_ratio, optimal_c_pto) with c, a and |Qe| from this backend.
- aPTO = w V0 / (v^2 rho0).
- Paper inputs: rho/rho0 = 1000, v = 340 m/s, h = 10 m, V0 = pi R^2 h. The switch to pi Ri^2 h is ours (decision D3).

**Dimensionless groups for comparing with the paper's figures:**
- Figs. 5-9 `[paper, Eq. 37]`: Q̄e = sqrt(g/h) Qe / (A h g); (c̄, ā, c̄PTO, āPTO) = (rho sqrt(g/h) / h)(c, a, cPTO, aPTO).
- Section 5 and Figs. 3-4 (following Martins-Rivas and Mei) `[paper, p. 126]`: Q̄e = w Qe / (A R g); (c̄, ā) = (c, a) w rho / R.

## 5. Energy bound used in rung 5 `[derived by Opus, not a cited result; decision D2]`

With the optimal cPTO (Eq. 39) at a + aPTO = 0, P_max(beta) = |Qe(beta)|^2 / (8 c). Inserting Eq. 36 and Pin = rho g A^2 cg / 2:

eta_max(beta) = 2 |Qe(beta)|^2 / ( (1/pi) times the integral from 0 to pi of |Qe|^2 d beta )

This uses the identity 2 k g h / (w Z_0(0)^2 cg) = 2, checked algebraically. So the mean over beta of eta_max is 2 exactly, but one beta can exceed 2.

Rung 5 checks two things:
1. eta(beta) <= eta_max(beta) at every point. This is algebraic, and a failure means a coding error.
2. The beta-mean of eta_max equals 2. This holds exactly when Eq. 36 holds, i.e. it is rung 1 in another form.

## 6. Numerics (implementation notes, not physics)

- Use exponentially scaled Bessel functions (`scipy.special.ive`, `kve`) for every ratio. Examples:
  - I_m(x r/R) / I_m(x) = ive(m, x r/R) / ive(m, x) times exp(x (r/R - 1))
  - K ratios: K_m(a) / K_m(b) = kve(m, a) / kve(m, b) times exp(b - a)
  - Logarithmic derivatives: I'_m / I_m = (ive(m-1) + ive(m+1)) / (2 ive(m)), and K'_m / K_m = -(kve(m-1) + kve(m+1)) / (2 kve(m))
- Hankel H_m = jv + i yv; H'_m from `h1vp`.
- k_l: `brentq` on f(k) = w^2 + g k tan(k h) inside ((l - 1/2) pi / h + tiny, l pi / h - tiny).
- Solve with `scipy.linalg.lu_factor` and `lu_solve` (multiple right-hand sides).
