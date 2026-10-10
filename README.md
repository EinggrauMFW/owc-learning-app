# owc-toy: one equation behind every OWC paper

Learning model for the chamber equation in Zheng, Zhang and Iglesias (2019), Eq. (2):

    [ (c + cPTO) - i (a + aPTO) ] p = Qe

It is **not** the paper's model. In the paper c, a and Qe come from a 3D potential-flow solution at a wall. Here they come from a damped piston (water column of effective length L, damping ratio zeta). Qe is obtained from c by the Haskind relation for an isolated axisymmetric absorber, so the maximum capture width ratio is exactly 1 by construction. The wall-reflection effect (eta around 2 in the paper) is **not** modelled. Treat every number as qualitative.

## Run

    python -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt   # exact versions, Python 3.13
    .venv\Scripts\python -m pytest -q                         # 66 tests, no browser, no network
    .venv\Scripts\python run_demo.py                          # prints key numbers, saves owc_toy_demo.png
    .venv\Scripts\python -m streamlit run app.py              # interactive app (local only)
    .venv\Scripts\python run_demo.py exports\run_...\run.json # rebuild a figure from an exported run.json

## Files

| File | Role |
| --- | --- |
| `owc_toy.py` | numerical core: Backend interface, PistonBackend, Eq. (2), power, eta, validity masks, Exercise 2 bisection. No UI imports. |
| `owc_views.py` | state, every number the app shows (`curves`), export/load of `run.json`, exercises, predictions file. No UI imports. |
| `run_demo.py` | `make_figure` (used by the app and the export) and the command-line demo. |
| `app.py` | Streamlit UI. Reads all defaults and ranges from `config/defaults.json`. |
| `config/defaults.json` | every default, range, unit and tooltip. Defaults equal `owc_toy.Params()`. |
| `tests/` | 66 tests: `test_owc_toy.py` (original 10), `test_app.py` (backend contract, config anchors, bisection, validity masks, run.json round trip, pint dimensions, exercises, export, app smoke tests), `test_zheng.py` (verification ladder of the wall model), `test_physics.py` (SymPy derivations, time-domain check, long-wave limit), `test_sea.py` (spectra and annual energy). |

Export writes `exports/run_<date-time>/` (curves.csv and sweep.csv with units in the header, figure.png, figure.svg, run.json). Exercise predictions are stored only in `predictions.json` in this folder. Both are git-ignored.

## Symbols, units, conventions (SI, regular waves, time factor exp(-i w t))

| Symbol | Meaning | Unit |
| --- | --- | --- |
| p | chamber air-pressure amplitude | Pa |
| Qe | excitation volume flow (pressure held at zero) | m^3/s |
| c, a | radiation conductance and susceptance (paper: "radiation damping", "added mass") | m^3/s/Pa |
| cPTO | turbine conductance (the PTO "damping") | m^3/s/Pa |
| aPTO | air-compressibility term, w V0 / (v^2 rho0) | m^3/s/Pa |
| w, T | angular frequency, wave period (T = 2 pi / w) | rad/s, s |
| kh | wave number times water depth, from w^2 = g k tanh(k h) | - |
| eta | capture width ratio, k P / Pin (paper Eq. 6) | - |
| Pin | wave power per metre of crest, 0.5 rho g A^2 cg | W/m |

Defaults: h = 10 m, inner radius 4 m, L = 4.2 m, zeta = 0.3, air height 5 m (V0 = S x 5 m), A = 1 m, rho0 = 1.2 kg/m^3 (my choice). L is tuned so the water-column natural frequency sits near kh = 2.4. The paper's own V0 is pi R^2 h (10 m of air height here); with that value this toy has no PTO resonance, see Exercise 2.

## What the tests check

1. Dispersion relation solved to 1e-10.
2. Regular-wave deep-water power equals rho g^2 A^2 T / (8 pi), which is twice the irregular-sea rule 0.49 Hs^2 Te kW/m for Hs = 2A.
3. a is positive below the natural frequency and negative above; c peaks at the natural frequency.
4. aPTO > 0 moves the PTO resonance (a + aPTO = 0) above the natural frequency.
5. eta = 1 at the matched condition (cPTO = c, a + aPTO = 0) and never exceeds 1 for any cPTO.
6. The numeric maximum of P over cPTO equals sqrt(c^2 + (a + aPTO)^2), and the closed form P_opt = |Qe|^2 / (4 (c + cPTO_opt)).
7. Power scales with A^2.

## Limits to keep in mind

* Piston assumption: valid when the chamber is small compared with the wavelength (k r_in below about 1, kh below 2.5 for these defaults). The PTO resonance (kh = 2.79) already sits just beyond that, so the grey zone in the figure is a warning, not a result.
* Optimal cPTO is chosen at every frequency (paper Eq. 39). A real turbine cannot do this, so panel (b) blue is an upper bound. The orange curve (one fixed cPTO) is closer to practice.
* Regular waves only. No spectrum, no annual energy, no viscous or turbine losses, no nonlinearity.

## Exercises (write your prediction first, then run)

1. **Damping ratio.** Set `zeta=0.15` in `Params`. Predict: what happens to the peak of c, to the width of the eta curve for the fixed cPTO, and to the optimal cPTO at resonance? Check with `run_demo.py`.
2. **Air compressibility.** Loop `H_air` from 2 to 15 m and find where `resonance_frequency_with_pto` stops finding a crossing (between 8 and 10 m in my run). Explain in one paragraph what that means for chamber design, using the signs of a and aPTO.
3. **Capture width check.** At the PTO resonance, show that P_opt / Pin equals 1/k (3.59 m in my run). Why is that the right answer for an isolated axisymmetric absorber?
4. **Bridge to the paper.** In Zheng et al. Fig. 5c, find the three intersections of a and -aPTO for the wall case. How many does this toy model have, and what physical mode is missing?

## Second backend: Zheng, Zhang and Iglesias (2019), OWC in a vertical wall

In the app sidebar, pick **Backend → "Zheng et al. 2019 wall OWC"**. It is a 3D linear potential-flow solution, solved by eigen-function matching, for an OWC half-embedded in an ideal vertical wall. It is shown separately from the piston toy and never on the same axes.

- New inputs are computed only when you press **Compute**: about 0.2 s per frequency, 200 frequencies by default. Results are cached in `cache/`.
- Equations are in `docs/zheng2019_equations.md`, transcribed from the paper's page images, with derivation notes.
- The verification ladder (rungs 1-6) is in `REPORT_B.md`, with raw outputs in `docs/rungs/`. Rung 3 is pending until Martins-Rivas and Mei (2009) is available.
- Check scripts: `python zheng_checks.py rung1|rung2|rung4|rung5|rung6|timing`.
- After pulling new code, restart Streamlit. It does not reload changed helper modules.

## Irregular waves and annual energy

The **Site & annual energy** tab has two parts:
- **A single sea state** (Hm0, Te, gamma) with its spectrum and absorbed-power density.
- **Annual energy for the Sipora 2022 swell sector** (`data/`, provenance in `data/README.md`).

It works for whichever model is selected. For the wall model, compute it on the Model tab first. The core is `owc_sea.py`, tested in `tests/test_sea.py`.

The sidebar's **Damping model** switches the toy to the frequency-dependent B(w), the physically scaled version.

## Licence and data

The code and documentation are under the [MIT licence](LICENSE). The Sipora wave table in `data/` is derived from ERA5 (Copernicus Climate Change Service, CC BY 4.0). Its attribution and the modifications made are in [data/README.md](data/README.md). Papers are cited, not included; see [NOTICE](NOTICE). Requires Python 3.13; exact package versions are in `requirements.txt`.

## References

Each DOI below was checked on Crossref. The full list (38 records), with BibTeX and what each reference supports, is in [LITERATURE.md](LITERATURE.md) and [docs/literature/references.bib](docs/literature/references.bib).

**The wall model and its validation**
- Zheng, S., Zhang, Y. & Iglesias, G. (2019). Coast/breakwater-integrated OWC: A theoretical model. *Marine Structures* 66, 121–135. [doi:10.1016/j.marstruc.2019.04.001](https://doi.org/10.1016/j.marstruc.2019.04.001)
- Zheng, S., Antonini, A., Zhang, Y., Greaves, D., Miles, J. & Iglesias, G. (2019). Wave power extraction from multiple oscillating water columns along a straight coast. *J. Fluid Mech.* 878, 445–480. [doi:10.1017/jfm.2019.656](https://doi.org/10.1017/jfm.2019.656)
- Martins-Rivas, H. & Mei, C. C. (2009). Wave power extraction from an oscillating water column at the tip of a breakwater. *J. Fluid Mech.* 626, 395–414. [doi:10.1017/s0022112009005990](https://doi.org/10.1017/s0022112009005990)
- Martins-Rivas, H. & Mei, C. C. (2009). Wave power extraction from an oscillating water column along a straight coast. *Ocean Engineering* 36, 426–433. [doi:10.1016/j.oceaneng.2009.01.009](https://doi.org/10.1016/j.oceaneng.2009.01.009)
- Garrett, C. J. R. (1971). Wave forces on a circular dock. *J. Fluid Mech.* 46, 129–139. [doi:10.1017/s0022112071000430](https://doi.org/10.1017/s0022112071000430)
- Evans, D. V. & Porter, R. (1995). Hydrodynamic characteristics of an oscillating water column device. *Applied Ocean Research* 17, 155–164. [doi:10.1016/0141-1187(95)00008-9](https://doi.org/10.1016/0141-1187(95)00008-9)
- Wilks, B. & Meylan, M. H. (2025). A numerical comparison of eigenfunction matching and singularity-respecting Galerkin approximation methods for linear water wave scattering. *J. Mar. Sci. Eng.* 13, 398. [doi:10.3390/jmse13030398](https://doi.org/10.3390/jmse13030398)

**The chamber equation, air compressibility and the turbine**
- Evans, D. V. (1978). The oscillating water column wave-energy device. *IMA J. Appl. Math.* 22, 423–433. [doi:10.1093/imamat/22.4.423](https://doi.org/10.1093/imamat/22.4.423)
- Evans, D. V. (1982). Wave-power absorption by systems of oscillating surface pressure distributions. *J. Fluid Mech.* 114, 481–499. [doi:10.1017/s0022112082000263](https://doi.org/10.1017/s0022112082000263)
- Sarmento, A. J. N. A. & Falcão, A. F. de O. (1985). Wave generation by an oscillating surface-pressure and its application in wave-energy extraction. *J. Fluid Mech.* 150, 467–485. [doi:10.1017/s0022112085000234](https://doi.org/10.1017/s0022112085000234)
- Falcão, A. F. O. & Henriques, J. C. C. (2016). Oscillating-water-column wave energy converters and air turbines: A review. *Renewable Energy* 85, 1391–1424. [doi:10.1016/j.renene.2015.07.086](https://doi.org/10.1016/j.renene.2015.07.086)
- Falcão, A. F. O. & Henriques, J. C. C. (2019). The spring-like air compressibility effect in oscillating-water-column wave energy converters: Review and analyses. *Renew. Sustain. Energy Rev.* 112, 483–498. [doi:10.1016/j.rser.2019.04.040](https://doi.org/10.1016/j.rser.2019.04.040)

**Absorption limits and the Haskind relation**
- Newman, J. N. (1962). The exciting forces on fixed bodies in waves. *J. Ship Research* 6, 10–17. [doi:10.5957/jsr.1962.6.4.10](https://doi.org/10.5957/jsr.1962.6.4.10)
- Budal, K. & Falnes, J. (1975). A resonant point absorber of ocean-wave power. *Nature* 256, 478–479. [doi:10.1038/256478a0](https://doi.org/10.1038/256478a0)
- Evans, D. V. (1976). A theory for wave-power absorption by oscillating bodies. *J. Fluid Mech.* 77, 1–25. [doi:10.1017/s0022112076001109](https://doi.org/10.1017/s0022112076001109)
- Porter, R., Zheng, S. & Greaves, D. (2021). Extending limits for wave power absorption by axisymmetric devices. *J. Fluid Mech.* 924. [doi:10.1017/jfm.2021.645](https://doi.org/10.1017/jfm.2021.645)

**Textbooks**
- Mei, C. C., Stiassnie, M. & Yue, D. K.-P. (2005). *Theory and Applications of Ocean Surface Waves*. World Scientific. [doi:10.1142/5566](https://doi.org/10.1142/5566)
- Falnes, J. & Kurniawan, A. (2020). *Ocean Waves and Oscillating Systems*, 2nd ed. Cambridge University Press. [doi:10.1017/9781108674812](https://doi.org/10.1017/9781108674812)
- Holthuijsen, L. H. (2007). *Waves in Oceanic and Coastal Waters*. Cambridge University Press. [doi:10.1017/cbo9780511618536](https://doi.org/10.1017/cbo9780511618536)

**Data**
- Copernicus Climate Change Service (C3S). ERA5 hourly data on single levels from 1940 to present. C3S Climate Data Store. [doi:10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47) (CC BY 4.0; see [data/README.md](data/README.md))

**Software**
- Python 3.13; Streamlit 1.65.0, NumPy 2.4.2, SciPy 1.17.1, SymPy 1.14.0, Pint 0.26.1, Altair 6.3.0, Matplotlib 3.11.1, pandas 3.0.6 (exact pins in `requirements.txt`).
- Verification and literature workflows used Scientific Agent Skills: Kassis, T., Agarwal, V., He, Y., Patel, D. & Brueckner, A. M. (2026). Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065. [doi:10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065)
