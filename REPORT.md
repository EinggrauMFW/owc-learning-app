# Report: Prompt A, interactive app for the toy OWC model

Date: 2026-10-09. Repository: `owc-app` (git). Python 3.13.14; exact versions in `requirements.txt`.

## What changed

| Commit | Change |
| --- | --- |
| Baseline | the original `owc-toy` learning module, unchanged |
| B0 | pinned environment (`pip freeze`) |
| B1 | `Backend` Protocol and `PistonBackend` in `owc_toy.py`. The backend-independent functions take `backend=` (default: piston), so the 10 original tests are unchanged. Validity masks: k r_in > 1, kh < 0.5, no PTO resonance. `has_pto_resonance` and `critical_H_air` (bisection) |
| B2 | `config/defaults.json`; `owc_views.py` (state, `curves`, export and load of `run.json`); pint dimension tests |
| B3+B4 | `make_figure` shared by the demo, the app and the export; Streamlit `app.py` with views 1 to 6, Exercises tab, export and restore; headless smoke test |
| B5 | README, this report |

One core change is not purely additive. I removed `np.asarray(w, dtype=float)` in `wavenumber`, `radiation_coefficients` and `a_pto`. Those casts stripped pint units, so the dimensional test could not run. The numbers are unchanged (see below), and every caller passes arrays or floats.

## Regression anchors (default inputs)

| Anchor | Original run | Now | Fresh clone |
| --- | --- | --- | --- |
| natural frequency | w 1.528 rad/s, T 4.11 s, kh 2.42 | same | same |
| PTO resonance | w 1.647 rad/s, T 3.82 s, kh 2.79 | same | same |
| c at resonance | 1.199e-2 m^3/s/Pa | 1.1991e-2 | same |
| eta at resonance | 1.000 | 1.000 | same |
| Pin | 15.5 kW/m | 15.5 (app: 15.49) | same |
| P_opt | 55.6 kW | 55.6 (app: 55.59) | same |
| P/Pin vs 1/k | 3.59 m = 1/k | 3.589 = 3.589 | same |

**App against the original `run_demo.py` arrays** (same grid of 1500 points, w 0.6 to 2.4 rad/s):

| Array | Maximum absolute difference |
| --- | --- |
| kh, c, a, aPTO, eta_opt, cPTO sweep | 0 (bit-identical) |
| eta_fixed | 5.9e-10 (relative 1.1e-9) |

The eta_fixed difference comes from the PTO resonance now being located on a finer grid (w_res moves by 1.7e-9 rad/s).

**Other acceptance checks:**
- Tests: 34 passed (10 original plus 24 new) in the repository and in a fresh clone with a fresh venv built from `requirements.txt`.
- Round trip: export, load, recompute agrees to 1e-12 (test). A figure rebuilt from `run.json` alone with `run_demo.py run.json` is pixel-identical to the exported PNG.
- The app was checked in the browser: all views render, there are no server or console errors, and Exercise 2 stays hidden until Run is pressed.

## VERIFY items

| Item | Status |
| --- | --- |
| k r_in < about 1 as the piston validity limit | **Unresolved as a literature criterion.** Stated everywhere in the UI as "the toy model's own assumption, not a literature criterion". No citation was found or used. |
| pint overhead on the core | **Resolved.** The core does not import pint (`grep` finds none), so the overhead is zero. pint is used only in `tests/test_app.py`, where all 13 public functions pass the dimensional check. |
| Regular-wave Pin = rho g^2 A^2 T / (8 pi) and the 0.49 Hs^2 Te relation | **Resolved** by original test 2 and by the sanity panel, where Pin_deep / rule = 2.00. The explanation is on screen: a regular wave of height H = 2A has twice the energy of an irregular sea with Hs = 2A. |
| Exercise 2 threshold | H_crit = 8.8435 m, bisection tolerance 1e-4 m. Confirmed independently by the closed form max over w of (-a v^2 rho0 / (S w)), which agrees within 2e-4 m (test). |

## Physically questionable findings (reported, not fixed)

1. **The default operating point is outside the model's own validity.** At the PTO resonance k r_in = 1.11, and the app shows the warning there by default.
2. **The damping is frozen.** The piston damping B = 2 zeta sqrt(k m) does not change with frequency, but real radiation damping goes to 0 as k goes to 0. So c(w), and through Haskind also Qe, has an arbitrary shape away from resonance.
3. **eta_max = 1 is built in.** It comes from the Haskind relation for an isolated axisymmetric absorber. The test that confirms it checks the algebra, not the physics.
4. **r_in does not move the resonance.** The natural frequency sqrt(g / L) depends on neither r_in nor h, so changing r_in changes c but not the resonance.
5. **Exercise 4 finds two crossings of a and -aPTO, at kh 2.785 and 7.71.** The second is at k r_in of about 3.1, far outside validity, so it is an artefact of the piston formula and should not be read as a second resonance.
6. **The fixed cPTO default has a fallback I chose.** The fixed cPTO defaults to c at the PTO resonance. When there is no resonance it falls back to c at the natural frequency, and the legend shows the value used.
7. **The original resonance finder only scanned 0.3 to 4 rad/s.** The app now scans 0.1 to 10 rad/s and decides "no resonance" from the sign of the minimum of a + aPTO, refined with a scalar minimiser, instead of from a failed scan.

## Three strongest objections a reviewer would raise

1. **The hydrodynamics are invented, so the efficiency numbers are circular.** c, a and Qe come from a one-degree-of-freedom piston whose damping ratio and column length were tuned to put the resonance near kh 2.4. Qe is then derived from c by a Haskind relation that guarantees eta_max = 1. The app can teach the *structure* of Eq. (2), such as phase, tuning and the role of aPTO. It cannot say how much energy a real chamber absorbs or over what bandwidth.
2. **The interesting region lies where the model admits it is invalid.** The PTO resonance, the peak of eta and most of the curve shape sit at k r_in > 1, where a uniform-piston free surface is a poor description. The model also omits sloshing modes, 3D diffraction and wall reflection, which the paper shows dominate the peak positions and can double eta.
3. **The idealisations overstate yield.** The model is linear and lossless, with regular waves only and a cPTO retuned at every frequency. Real output is set by irregular seas, turbine losses and nonlinearity, viscous losses at the front wall lip and nonlinear air compression. Even the fixed-cPTO curve is an upper bound, and nothing here gives annual energy.

## Next steps (non-goals for this prompt)

- Irregular waves, spectra, scatter tables and annual energy (needs the Sipora material).
- Wall and reflection effects with 3D diffraction (Prompt B, `ZhengWallBackend`, behind the same `Backend` interface).
- A nonlinear turbine, or a time-domain model.

No cloud deployment.

## How it was built

- Haiku 5.5 subagents wrote B1 to B4. Opus wrote the plan, the config and every physics text, and gated each batch with a diff review, the tests, the anchors and the measurement against `run_demo`.
- One batch was sent back. B2 marked 12 pint checks as expected failures instead of making them run, and Opus fixed the root cause.
- Opus also corrected label overlaps in the figure and moved the last number hard-coded in `app.py` into the config.
