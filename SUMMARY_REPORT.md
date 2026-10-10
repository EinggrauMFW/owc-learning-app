# OWC learning app: summary report

Date: 2026-10-10. **66 tests passing.** Detailed reports, all in the repository:
- [REPORT.md](REPORT.md): Prompt A, the toy app.
- [REPORT_B.md](REPORT_B.md): Prompt B, the paper's model and its verification ladder.
- [VERIFICATION.md](VERIFICATION.md): physics checks of the toy.
- [LITERATURE.md](LITERATURE.md): literature support.

## 1. What exists now

An interactive local app (Streamlit) for learning oscillating water column (OWC) hydrodynamics. It has **two independent models, never mixed**:

| Model | What it is | Use it for |
| --- | --- | --- |
| **Piston toy** (`owc_toy.py`) | A water column moving like a piston, a compressible air chamber, a linear turbine; isolated device; regular waves | Learning the chamber equation and the roles of c, a, aPTO and cPTO. **Not** a design tool. |
| **Zheng et al. (2019) wall OWC** (`owc_zheng.py`) | A 3D linear potential-flow solution, by eigen-function matching, for an OWC half-embedded in an ideal vertical wall | Reproducing and exploring the paper; seeing what the wall does |

**App tabs:**
- **Learn step by step:** 8 steps with definitions, an animation of the chamber drawn to scale, a phasor diagram of Eq. 2 and a dispersion plot.
- **Model:** interactive charts, the operating-point table and an always-visible sanity panel.
- **Exercises:** your predictions are stored locally, and answers stay hidden until you press Run.
- **Glossary.**
- **Physics checks:** a live time-domain check, the verification and literature write-ups, and the validation of the paper's model.

All charts are interactive: hover tooltips, zoom, legend highlighting and a "Show data" table under each main chart.

**Run it:**
```bat
.venv\Scripts\python -m streamlit run app.py
```
Restart Streamlit after any code change, because it does not reload helper modules.

## 2. Prompt A: the toy app

- **Regression anchors** reproduce exactly in a fresh clone: natural frequency w = 1.528 rad/s; PTO resonance w = 1.647 rad/s (kh 2.79); c = 1.1991e-2 m³/s/Pa; eta = 1.000; Pin = 15.5 kW/m; P_opt = 55.6 kW; P/Pin = 3.59 m = 1/k.
- **The app against the original `run_demo.py`:** the arrays are bit-identical, except eta_fixed, which differs by at most 5.9e-10 because the resonance is now located on a finer grid.
- **Architecture:**
  - a `Backend` interface;
  - every default and range in `config/defaults.json`;
  - a pinned environment (`requirements.txt`);
  - export to `run.json`, CSV, PNG and SVG, with reload restoring the same state (round trip to 1e-12; a figure rebuilt from `run.json` is pixel-identical).
- **Exercise 2:** the PTO resonance disappears at **H_air = 8.8435 m** (bisection, tolerance 1e-4 m), confirmed by an independent closed form.
- **New ζ option:** buttons for the toy default (0.30) and a physical estimate (≈0.54, see §4).

## 2b. Added after the first summary: frequency-dependent damping and annual energy

- **Damping model choice** (sidebar). The new frequency-dependent option uses B(w) = k rho g S² (2J1(kr)/(kr))²/(4 cg), the Froude-Krylov plus Haskind estimate at every frequency.
  - It gives the physical long-wave scaling, c ∝ w³ (measured slope 3.02), and keeps eta_max = 1.
  - It is off by default, so the regression anchors are unchanged.
- **New tab "Site & annual energy"** (`owc_sea.py`, `site_tab.py`):
  - JONSWAP spectra from Hm0 and Te, using Te/Tp = 0.903 for gamma 3.3, computed from the spectrum.
  - Linear superposition of the regular-wave response.
  - Incident power checked against the 0.49 Hs²Te rule in deep water (to 1e-4).
  - The Sipora 2022 scatter table (5,194 in-sector hours), with the best fixed cPTO found for the year and, as an upper bound, cPTO retuned per sea state.

| Model (h = 10 m, inner radius 4 m) | Annual energy, best fixed cPTO | Capture width |
| --- | --- | --- |
| Toy, constant zeta | 229 MWh | 5.1 m |
| Toy, B(w) | 57 MWh | 1.3 m |
| Zheng wall model | 114 MWh | 2.5 m |

  - The constant-zeta toy overestimates long-period swell by about 4x.
  - The wall model gives about twice the physically scaled isolated estimate, consistent with the wall-doubling result (the geometries differ).
  - 43% of the site's wave energy is at kh < 0.5, where the toy is unreliable.
  - **Assumptions shown on screen:**
    - ERA5 deep-water sea states are applied at the device with no wave transformation.
    - Waves are long-crested from one direction.
    - Results are absorbed, not electrical, energy.

## 3. Prompt B: the paper's model (Zheng, Zhang & Iglesias 2019)

The equations were read from the PDF's **page images**. Every projection of the linear system (A.1-A.12) and the far-field formula (Eq. 35) were re-derived by hand. One typo was found: Eqs. 33-34 print Z₀(z) where Z₀(0) must be.

| Rung | Result |
| --- | --- |
| 1. Three methods for c agree (direct, far-field, Haskind) | **Pass**: agreement to 1.2e-3, shrinking 5-6x when M and L double, so the gap is truncation, not transcription |
| 2. Convergence in M and L | Converges, but the original 1e-4 target was not reached. The paper's M = 12, L = 20 is accurate to about 1-3%; slowest near the sloshing mode |
| 3. Thin wall against Martins-Rivas & Mei (2009) | **Indirect pass for the main mode**, using their results as replotted in Zheng et al. 2019 JFM Fig. 4 (c̄ peak 7.96 against 7.89). The sloshing spike is shifted by +0.07 in kh |
| 4. The paper's reported features | Resonances at kh 1.861 and 2.911 (paper 1.86, 2.90); Qe peak 1.742 (1.73); Δkh 1.23 → 0.61 (paper 1.19 → 0.56); eta ≈ 2 in the band |
| 5. Energy bound with a wall | **Pass**: eta never exceeds its per-direction bound; the bound averaged over wave direction is 2.000 |
| 6. Direction, draft and thin-wall limits | Paper trends reproduced; the thin-wall limit is not fully settled at (R − Ri)/h = 0.01 |

Each frequency takes about 0.2 s (4 BLAS threads). A 200-point sweep takes about 40 s and is cached on disk.

## 4. Is it verified against physics?

**The toy (VERIFICATION.md):**
- **Derived:** every formula is derived from the governing equations with **sympy**: c and a, the natural frequency √(g/L), aPTO, Eq. 2, the optimal cPTO, the energy balance, the group velocity, and the coefficient 0.4906 of the 0.49 Hs²Te rule.
- **Reproduced:** an **independent time-domain simulation** of the same ODEs gives the app's power to **1e-12**, and energy balances to 1e-12.
- **Live check:** the **Physics checks** tab can re-run that check at any operating point you set.
- **Units:** every public function passes a **pint** dimensional check.

**Physical plausibility of the toy (a finding):**
- The toy's damping **ζ = 0.30 is about half** the value implied by the Froude-Krylov force plus the Haskind relation: **0.54** at the natural frequency, **0.63** at the PTO resonance. The spread itself shows the cost of keeping the damping constant.
- With the physical ζ, **the default chamber has no PTO resonance**: the critical air height falls from 8.84 m to 3.36 m.
- The toy's long-wave scaling is c ∝ ω² instead of the physical ω³.

**The paper's model, validated against physics that comes from neither the paper nor our code:**
- **Long-wave limit at a reflecting wall:** the solver converges to |Qe| → 2ωAπRi² and c → π²ω³Ri⁴Z₀(0)²/(2ρg²h). The error falls like (kR)², down to **2e-4**. That independently confirms the excitation solution, the doubling caused by the wall, and Haskind's constant.
- **Low-frequency slope of c:** 3.01 (physics says 3).

## 5. Literature

- **The search:** 38 references from Crossref and OpenAlex (164 logged queries), each DOI checked, mapped to the **11 theory claims** the app uses (C1-C11 in LITERATURE.md).
- **Clearest support from abstracts:**
  - Sarmento & Falcão (1985): the chamber equation and linearised air compressibility.
  - Evans (1978): the piston model.
  - Newman (1962): the Haskind relation.
  - Zheng et al. (2019) JFM: 3D OWC at a coast, with the wall enhancing extraction.
  - Wilks (2025): convergence of eigenfunction matching at sharp corners. This explains rung 2.
- **Downloaded open copy:** Zheng et al. (2019) JFM 878 (accepted manuscript, TU Delft). It is the source of the indirect rung 3.
- **Limit:** full texts are mostly paywalled, and about two thirds of the abstracts are missing, so many entries are "topical" rather than "supported".

## 6. Errors I made and corrected

| Error | Correction |
| --- | --- |
| Said raising ζ would not change the PTO resonance | Wrong; it can remove it (§4). VERIFICATION.md corrected, and a test added |
| Cited Stansell & Pizer (arXiv) for the 1/k limit | That paper is about line absorbers. Replaced with the primary sources: Newman 1962, Budal & Falnes 1975, Evans 1976, Porter et al. 2021 |
| Recalled "Ning et al. 2016, Renewable Energy" | Does not exist; the real paper is Applied Energy 168. It was never cited in the app |
| Estimated 10-40 s for a 200-point sweep of the paper's model | It was about 2 min; fixed by the BLAS thread setting (now about 40 s) and a Compute button |
| The phasor title showed 180° at resonance | Wrong phase wrap; fixed |
| The ζ button first evaluated at the PTO resonance, which moves with ζ, so pressing it twice gave different values | Now evaluated at the natural frequency |
| Subagent work rejected at review | 12 dimension checks marked as expected failures (core fixed instead); a test written to the old tolerance (re-specified); labels overlapping curves; a clipped animation |

## 7. The strongest objections to drawing real-world conclusions

1. **The toy's hydrodynamics are chosen, not computed.** ζ and L are tuned, and eta ≤ 1 is built in through Haskind. It teaches the structure of Eq. 2, not real absorption or bandwidth.
2. **The wall model is ideal.** The infinite, rigid, perfectly reflecting wall creates the doubling. Real breakwaters absorb and scatter part of the wave.
3. **Everything is linear, lossless and regular.** There is no viscous loss at the chamber lip, no nonlinear air or turbine behaviour, no irregular sea and no annual energy. The optimal cPTO is retuned at every frequency, an upper bound.
4. **The highest numbers are the least reliable.** The sloshing peak (eta ≈ 3.2) is narrow, converges slowly and would be damped in reality.
5. **There is no validation against measurements.** No dataset was found that reports capture width against kh for a wall-embedded circular OWC.

## 8. Open items and next steps

- **Direct rung 3:** needs Martins-Rivas & Mei (2009), which is paywalled. Updating `docs/rungs/rung3_reference.json` updates the chart, the table and the test.
- **Not done yet:** a load-run that restores the Zheng sliders; a shared zoom across the four Zheng charts.
- **Still for later:**
  - wave transformation from the ERA5 node to the device depth (a spectral wave model such as SWAN);
  - directional spreading;
  - turbine efficiency and rated power;
  - a nonlinear turbine or a time-domain model.

## 9. How it was built

- **Opus** (the main session): plans, all physics text and derivations, the equation sheet, rung criteria, verification, review of every batch, and these reports.
- **Coding subagents:**
  - Haiku 5.5: Prompt A batches B1-B4.
  - Sonnet: the Learn tab, the Zheng solver, rungs 4-6, the UI, the interactive charts and literature retrieval.
- **Every batch was gated by Opus before commit**: tests, regression anchors and a diff review.
- **Scientific Agent Skills** (Kassis et al. 2026, arXiv:2609.00065): sympy, paper-lookup, citation-management, literature-review and dataviz.

**File map:**
- `owc_toy.py`, `owc_zheng.py`: physics cores, no UI.
- `owc_views.py`, `zheng_views.py`: computed views and export.
- `app.py`, `learn.py`, `charts.py`: the UI.
- `learn_text.py`, `zheng_text.py`: all user-facing physics text.
- `verification/`: independent checks.
- `docs/`: the equation sheet, rung outputs and literature.
- `tests/`: 58 tests.
