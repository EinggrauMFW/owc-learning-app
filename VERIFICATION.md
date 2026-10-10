# Physics verification of the toy OWC model

Are the toy model's calculations verified against physics? Yes: every formula in `owc_toy.py` was derived from governing equations with sympy, and the numbers were reproduced by an independent time-domain simulation. One free parameter (zeta) turned out to be physically low, and that is reported below.

- Script: [verification/verify_toy.py](verification/verify_toy.py) (`python verification/verify_toy.py`)
- Tests: [tests/test_physics.py](tests/test_physics.py)

## 1. The model as physics

The toy is a **water column moving like a piston**, coupled to a **compressible air chamber** and a **linear turbine**. Linear theory applies, with time factor exp(-i w t). The governing equations are:

| Part | Equation | Assumption |
| --- | --- | --- |
| Water column (area S = pi r_in^2, mass m = rho S L) | m x'' + B x' + K x = F_e(t) - S p,  with K = rho g S (hydrostatic spring) | rigid piston, linear damping B = 2 zeta sqrt(K m) |
| Air chamber (volume V0 = S H_air) | p' = (rho0 v^2 / V0)(S x' - cPTO p) | linearised isentropic compression; rho0 v^2 = gamma p_atm is the adiabatic bulk modulus |
| Turbine | outflow = cPTO p | linear Wells turbine, no losses |

Only one choice in this table is not physics: **B (through zeta) and L are chosen, not derived.** Section 4 tests whether zeta is physically sensible.

## 2. Symbolic derivations (sympy, exact; all pass)

| # | Derived from the equations above | Matches code |
| --- | --- | --- |
| S1 | Column admittance Y = S^2/(B - iX), X = w m - K/w. So c = S^2 B/(B^2 + X^2), a = -S^2 X/(B^2 + X^2), with Q_R = -(c - i a) p (paper Eq. 4). Natural frequency (a = 0) is sqrt(K/m) = sqrt(g/L). The peak value of c is S^2/B. | `radiation_coefficients`, `natural_frequency` |
| S2 | Air chamber gives S U = (cPTO - i aPTO) p, with aPTO = w V0/(v^2 rho0) | `a_pto` |
| S3 | Superposition, S U = Qe - (c - i a) p, gives the paper's Eq. 2: [(c + cPTO) - i(a + aPTO)] p = Qe | `pressure` |
| S4 | dP/dcPTO = 0 gives cPTO = sqrt(c^2 + (a + aPTO)^2), a maximum (second derivative < 0). At a + aPTO = 0, P_max = \|Qe\|^2/(8c). | `optimal_c_pto`, `optimal_power` |
| S5 | Energy balance: Re(Qe p*)/2 = c\|p\|^2/2 (radiated) + cPTO\|p\|^2/2 (absorbed). The air spring stores energy and returns it each cycle. | (used to read power) |
| S6 | cg = dw/dk from w^2 = g k tanh(kh). The deep-water limit gives Pin = rho g^2 A^2 T/(8 pi). The coefficient rho g^2/(64 pi) is **0.4906** kW/(m^3 s), the 0.49 Hs^2 Te rule. | `group_velocity`, `incident_power` |

## 3. Independent numerical check (time domain)

The ODEs in section 1 were integrated with `scipy.integrate.solve_ivp` (DOP853, rtol 1e-10) for 80 wave periods, and the last 20 periods were averaged. No frequency-domain code is used in the integration. The excitation force amplitude comes from the toy's own |Qe| through the column equation.

| T [s] | cPTO [m^3/s/Pa] | P, time domain [kW] | P, frequency domain [kW] | rel. error in P | rel. error in \|p\| | energy residual |
| --- | --- | --- | --- | --- | --- | --- |
| 4.240 | 0.01321 (opt) | 76.2077 | 76.2077 | 2.5e-13 | 6.1e-6 | 1.3e-13 |
| 4.240 | 0.004 | 54.0073 | 54.0073 | 1.2e-13 | 2.6e-5 | -4.7e-13 |
| 4.240 | 0.05 | 49.9975 | 49.9975 | 1.5e-12 | 2.7e-5 | -3.2e-13 |
| **3.816 (PTO resonance)** | **0.01199 (opt)** | **55.6315** | **55.6315** | 4.9e-13 | 2.8e-5 | 2.4e-13 |
| 3.816 | 0.004 | 41.7394 | 41.7394 | 4.1e-13 | 2.8e-5 | -7.8e-13 |
| 3.816 | 0.05 | 34.7174 | 34.7174 | 6.7e-15 | 2.8e-5 | 2.6e-15 |
| 2.935 | 0.006025 (opt) | 23.5990 | 23.5990 | 9.5e-13 | 4.9e-7 | 4.2e-13 |
| 2.935 | 0.004 | 22.5955 | 22.5955 | 2.8e-12 | 1.6e-5 | -2.0e-12 |
| 2.935 | 0.05 | 8.8182 | 8.8182 | 1.8e-13 | 3.0e-5 | 4.0e-14 |

- **Power agrees to about 1e-12**, and wave work equals radiated plus absorbed power to about 1e-12.
- The \|p\| error of about 3e-5 comes from reading the amplitude off 400 samples per period. It is not a model error.
- **The dispersion relation** solved by the code's Newton iteration matches an independent bracketing solver (brentq) to 7e-14.
- **Units:** every public function passes a pint dimensional check (`tests/test_app.py`).

## 4. Physical plausibility of the toy's free parameter zeta

The radiation damping B is the one number the toy does not derive. An independent estimate at the PTO resonance (kh = 2.79, k r_in = 1.11):
- **Excitation force:** Froude-Krylov force on a surface disk of radius r_in, F_FK = rho g A S · 2J1(ka)/(ka) = 0.853 rho g A S. This neglects diffraction, so it is an estimate.
- **Haskind relation for an axisymmetric heaving absorber:** B = k\|F_e\|^2/(8 Pin). This is the statement that its maximum capture width is 1/k = lambda/(2 pi). Sources: Newman (1962) J. Ship Res. 6:10 (Haskind relations); Budal & Falnes (1975) Nature 256:478; Evans (1976) J. Fluid Mech. 77:1; Porter, Zheng & Greaves (2021) J. Fluid Mech. 924. All DOIs were checked; see LITERATURE.md.

| Quantity | Toy | Estimate |
| --- | --- | --- |
| damping ratio zeta | 0.30 | **0.63** |
| excitation force at resonance / Froude-Krylov force | 0.69 | 1 by definition |

**Finding:** the toy's zeta = 0.3 is about **half** the value consistent with Froude-Krylov plus Haskind, and its implied excitation force is about 69% of the Froude-Krylov force.

The estimate depends on the frequency it is evaluated at, because real damping varies with frequency and the toy's is constant: **0.63** at the toy's PTO resonance (w = 1.647 rad/s), **0.54** at the natural frequency sqrt(g/L) (w = 1.528 rad/s). The 0.54-0.63 spread is itself a measure of the constant-damping simplification.

What changes when zeta is raised from 0.30 to 0.63, all else at the defaults (computed, `owc_toy`):

| Quantity | zeta = 0.30 | zeta = 0.63 |
| --- | --- | --- |
| peak of c [m^3/s/Pa] | 0.01273 | 0.00606 (c_peak = S^2/B) |
| minimum of a [m^3/s/Pa] | -0.00637 | -0.00290 |
| PTO resonance (a + aPTO = 0) | yes, kh 2.79 | **none**: -aPTO never meets the flatter a curve |
| critical air height for a PTO resonance (Exercise 2) | 8.84 m | **3.36 m** |
| maximum eta (optimal cPTO) | 1.000 at kh 2.79 | 0.982 at kh 4.21 (inside the k r_in > 1 zone) |
| kh width where eta_opt > 0.5 | 4.92 | 5.23 |

The natural frequency (a = 0, X = 0) does not depend on zeta. The **PTO resonance does**, because a = -S^2 X/(B^2 + X^2) shrinks as B grows. An earlier version of this note wrongly said the resonance frequencies would not change; the table above corrects it.

**In the app:** the default stays 0.3 (regression anchors). The sidebar has two buttons:
- **"Physical (≈0.54)"** sets zeta from this estimate for the current inputs, evaluated at the natural frequency (`owc_toy.zeta_froude_krylov`). Because the natural frequency does not depend on zeta, pressing it twice gives the same value.
- **"Toy default (0.30)"** goes back.

## 5. What is verified, and what is not

**Verified:** the algebra of every formula; the frequency-domain solution (against an independent time integration); energy conservation; the units; the wave formulas; and the 1/k capture-width limit (literature).

**Not verified, because they are assumptions of the toy:**
- The column is a rigid piston. This is weak for k r_in > 1, and the default operating point is at 1.11.
- B is constant with frequency. Real radiation damping goes to 0 as k → 0.
- L includes an added mass that is chosen, not computed.
- The phase of Qe is not modelled.

The Zheng backend (REPORT_B.md) replaces all of these with a 3D potential-flow solution for the wall case.

**Literature checked for this note** (bibliographic details confirmed by search; full texts are behind paywalls and were not read):
- Evans, D. V. (1982), J. Fluid Mech. 114, 481-499 (oscillating surface-pressure distributions: the OWC form of absorption theory).
- Evans, D. V. (1976), J. Fluid Mech. 77, 1-25 (absorption by oscillating bodies).
- Sarmento, A. J. N. A. & Falcão, A. F. de O. (1985), J. Fluid Mech. 150, 467-485 (OWC with air compressibility, linearised; this is Zheng et al.'s ref. [34]).

Verification code uses SymPy 1.14.0 through the Scientific Agent Skills `sympy` skill (Kassis et al. 2026, arXiv:2609.00065).
