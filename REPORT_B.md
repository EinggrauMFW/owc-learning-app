# Report: Prompt B, paper-faithful backend (Zheng, Zhang and Iglesias 2019)

Date: 2026-10-10. Backend: `owc_zheng.ZhengWallBackend`. Equation source: [docs/zheng2019_equations.md](docs/zheng2019_equations.md), transcribed from page images of the published PDF (not included in this repository). Raw rung outputs: [docs/rungs/](docs/rungs/). Prompt A tests still pass.

Default case throughout: R/h = 0.5, (R - Ri)/h = 0.1, d/h = 0.2, beta = pi/2, h = 10 m, rho/rho0 = 1000, v = 340 m/s, V0 = pi R^2 h.

## Rung results

| Rung | Result | Key numbers |
| --- | --- | --- |
| 1. DM, FFC and HR agree | **Pass** (criterion agreed with the project owner on 2026-10-09: gap <= 2e-3 at (12, 20), and at least 3x smaller at (24, 40)) | Maximum gap 1.2e-3 over kh 0.1 to 7. At kh 1.86: 1.4e-4 at (12, 20), 2.2e-5 at (24, 40). At kh 4.7: 1.1e-3, then 1.9e-4. FFC and HR agree with each other much more closely than either agrees with DM, so the inner-flux (DM) value carries most of the truncation error. No constant factor appears, which also confirms reading Eq. 36 with Qe per unit amplitude. |
| 2. Convergence in M and L | **Converges, but the 1e-4 target is not reached** at any truncation tried | Relative change between (12, 20) and (16, 30): at kh 1.73, \|Qe\| 7e-4, c 1.7e-3, a 2.1e-2, eta 4e-4; at kh 2.9, 2.6e-3, 4.6e-3, 1.4e-3, 5e-4; at kh 4.82 (sloshing), 1.8e-2, 3.5e-2, 6.8e-3, 1.4e-2. a and the sloshing peak converge slowest, and convergence is not monotone at small M. |
| 3. Thin wall against Martins-Rivas and Mei (2009) | **Indirect pass for the main mode** (2026-10-10) | Reference values read by eye from Zheng et al. (2019) JFM 878 Fig. 4, Martins-Rivas & Mei's results as replotted there (open copy at TU Delft). Main mode: c̄ peak 7.96 against 7.89, ā extremes within 0.11 and 0.035 in kh. Sloshing spike: 0.4-0.8 higher and +0.07 in kh, following Zheng's own line. See [docs/rungs/rung3_indirect.md](docs/rungs/rung3_indirect.md). The direct comparison still needs the original paper. |
| 4. The paper's reported features | **Mostly reproduced** (table below) | Resonances within 0.011 in kh; the main Qe peak within 0.012; Δkh within 0.05. The sloshing peak of eta is higher than the paper's figure (3.21 against about 2.9). |
| 5. Energy bound with a wall | **Pass** | eta_opt / bound <= 0.99986 everywhere. The mean of eta_max over beta is between 1.9978 and 2.0000. Every eta > 2 point is within its per-beta bound, e.g. kh 4.85: eta 2.72 against a bound of 3.07. |
| 6. Symmetry and limits | **Reported** | \|Qe\| max/min over beta from 0 to pi/2: 1.06 (kh 1.73), 1.11 (2.9), 1.55 (4.82). Weak dependence at the main peak, as the paper says; strong at sloshing. As d/h falls from 0.3 to 0.02, the first resonance rises from kh 1.58 to 2.66, the paper's trend. The thin-wall limit is not fully settled at (R - Ri)/h = 0.01 (details below). |

### Rung 4 in detail (differences only; nothing was tuned)

| Feature | Paper | Solver | Difference |
| --- | --- | --- | --- |
| Qe peak 1 (kh) | 1.73 | 1.742 | +0.012 |
| Qe peak 2 (kh) | 4.82 | 4.829 | +0.009 |
| PTO resonance 1 | 1.86 | 1.861 | +0.001 |
| PTO resonance 2 | 2.90 | 2.911 | +0.011 |
| PTO resonance near 4.9 | 4.90 (one) | **two**: 4.832 and 4.891 | the second is within 0.009 |
| eta on 1.6 < kh < 3.1 | "about 2" (2.0 to 2.3 read off Fig. 5e) | 1.77 (at kh 1.6, the band edge) to 2.23 | the band edge is below 2; the interior is about 1.95 to 2.23 |
| peak c̄ (Fig. 5b) | about 3.3 at kh about 1.8 | 3.40 at kh 1.789 | +0.10 |
| peak eta in [4.6, 5.2] | about 2.9 (Fig. 5e, beta = pi/2) | 3.21 at kh 4.831 | +0.31 |
| Δkh, R/h = 0.3 | 1.19 | 1.232 | +0.042 |
| Δkh, R/h = 0.7 | 0.56 | 0.609 | +0.049 |

**V0 switch.** Changing V0 from pi R^2 h to pi Ri^2 h moves the resonances from 1.861, 2.911 and 4.832 to 1.828, **3.553** and 4.831. The second resonance moves by +0.64 in kh, and eta on [1.6, 3.1] drops from 1.77-2.23 to 1.55-2.12. **This choice, which the paper does not test, moves the band about as much as the geometry changes the paper studies.**

### Explaining the discrepancies (my reading, not proven)

- **The two resonances near kh 4.9.** The ā spike of the sloshing mode crosses -āPTO going up and again coming down. The paper's Fig. 5c shows the same spike, but its text lists one intersection at about 4.90.
- **The sloshing eta peak, 3.21 against about 2.9.** The peak is about 0.05 wide in kh. A figure plotted on a coarse kh grid would cut its top. It is also the least converged quantity (1.4% change at (16, 30), still drifting). Both effects push the same way.
- **Δkh, about +0.04 to +0.05.** This is consistent with truncation: each resonance moves by about 0.01 per truncation step. It could also come from reading values off the paper's Fig. 7.

### Rung 6, thin wall in detail

| (R - Ri)/h | 0.1 | 0.05 | 0.02 | 0.01 |
| --- | --- | --- | --- | --- |
| resonance 1 | 1.861 | 1.812 | 1.801 | 1.805 |
| resonance 2 | 2.911 | 3.029 | 3.080 | 3.091 |
| peak c̄ | 3.40 | | | 3.15 |
| maximum eta on [1.6, 3.1] | 2.23 | | | 2.58 |

Resonance 1 settles; resonance 2 is still drifting slightly. The peak c̄ and the maximum eta were reported only at the two ends of the sweep, and both are still changing. The 0.02 and 0.01 rows come from a lighter scan, because the full run was cut short by CPU starvation.

I did not compute a matrix condition number, because the factor routine keeps only the LU factors. The ratio of the largest to the smallest diagonal of U at kh 2 is 39.5. That is weak evidence, but it shows no sign of ill-conditioning.

## Truncation and timing

- (M, L) used: **(12, 20)**, the paper's values, for the app and rungs 4 to 6. Rung 1 also uses (24, 40) to show convergence.
- 1344 complex unknowns at (12, 20).
- One frequency (one LU factorisation, solving R and S together): **0.19 s with 4 BLAS threads**. With the default BLAS thread count it was 0.55 s, because the default oversubscribed this machine. The app now defaults to 4 threads; override it with `OPENBLAS_NUM_THREADS`.
- A 200-point kh sweep takes about 40 s and is cached on disk (`cache/`, git-ignored).
- Rung 1 on 40 points, including Haskind with 64 beta: about 2 min under load.

## Equation log

| Item | Status |
| --- | --- |
| Eqs. 33 and 34 print Z_0(z) | Fixed to Z_0(0) by derivation (disk integral of ∂Φ/∂z at z = 0). The paper's superscript D in Eq. 33 is read as the scattering coefficients A^S. |
| Eq. 36 needs Qe per unit incident amplitude | Notation; now resolved, because rung 1 agrees to 1e-3 with no constant factor. |
| Eq. 35 | Re-derived from the radiated energy flux; agrees with the paper. |
| A.1, A.3, A.4, A.5, A.8, A.9, A.11, A.12 | Projections re-derived; agree as printed. |
| Validity mask near closed-cylinder sloshing zeros | Defined by |J'_m(k0 Ri)| relative to the neighbouring Bessel values, because the absolute 1e-8 test in the sheet fired at every high m. This is an implementation choice, not a physics change. |
| Paper p. 130 cites "[47], [48]" | Does not match its reference list. Not used. |
| **UNRESOLVED** | **Rung 3 against the original Martins-Rivas & Mei numbers** (only the indirect check through Zheng's replot exists). **The rung 5 bound is my own derivation**: the per-beta form, and the beta-mean of eta_max = 2 from Eq. 36 plus Pin. It is labelled as a derivation in the UI and is not a cited result. |

## Three strongest objections a reviewer would raise

1. **The doubling depends entirely on an ideal wall.** The infinite, rigid, perfectly reflecting straight wall creates a standing wave that the device sits in, which gives eta ≈ 2 and the beta-mean bound of 2. Real breakwaters (rubble mounds, caissons with toe scour, finite length, curved alignment) absorb or scatter part of the wave, so the gain over an isolated device is an upper limit that shrinks as reflection falls. The model has no parameter for partial reflection, so it cannot say by how much.
2. **The highest numbers come from the least trustworthy physics and numerics.**
   - **Physics:** the sloshing peak (eta ≈ 3.2 at kh 4.83) is a narrow, lossless, high-Q resonance. In a real chamber, vortex shedding at the lip and wall corners, viscous losses and nonlinear sloshing would flatten it. The linear solution is in fact singular at those corners.
   - **Numerics:** the same peak and the coefficient a converge slowest in M and L (changes of 1-4% between (12, 20) and (16, 30)), and the thin-wall limit is still drifting at (R - Ri)/h = 0.01.
3. **Modelling choices move the result as much as the design variables do.**
   - V0 = pi R^2 h against pi Ri^2 h shifts the second resonance by 0.64 in kh.
   - The air spring is linear and isentropic.
   - The optimal cPTO is retuned at every frequency (an upper bound).
   - Waves are regular only.

   Together these make eta an optimistic, assumption-sensitive bound, not a predicted performance for an irregular sea.

## Interpretation notes shown in the app (Prompt B §3)

These appear verbatim from `zheng_text.py`, always visible:
- The ideal-wall assumption.
- The optimal-cPTO upper bound.
- There is no isolated offshore case in this backend, and no like-for-like comparison with the piston toy.
- Results are dimensionless through h except for aPTO.
- eta can exceed 1 (and 2 at a single direction) under the derived bound.

## How it was built

- **Opus:** read the paper from page images, wrote the equation sheet with derivation checks, set the rung criteria, gated each batch and wrote this report and all physics text.
- **Sonnet subagents:**
  - Z1: the solver and rungs 1 and 2.
  - Z2: rungs 4 to 6.
  - Z3: the UI.
- **Opus fixes after review:**
  - A Compute button, so the app does not solve on every slider change.
  - The BLAS thread default.
  - Rung test criteria rewritten to the agreed definitions.
