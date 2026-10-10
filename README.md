# owc-toy: one equation behind every OWC paper

Learning model for the chamber equation in Zheng, Zhang and Iglesias (2019), Eq. (2):

    [ (c + cPTO) - i (a + aPTO) ] p = Qe

It is **not** the paper's model. In the paper c, a and Qe come from a 3D potential-flow solution at a wall. Here they come from a damped piston (water column of effective length L, damping ratio zeta). Qe is obtained from c by the Haskind relation for an isolated axisymmetric absorber, so the maximum capture width ratio is exactly 1 by construction. The wall-reflection effect (eta around 2 in the paper) is **not** modelled. Treat every number as qualitative.

## Run

    python -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt   # exact versions, Python 3.13
    .venv\Scripts\python -m pytest -q                         # 34 tests, no browser, no network
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
| `tests/` | `test_owc_toy.py` (original 10), `test_app.py` (backend contract, config anchors, bisection, validity masks, run.json round trip, pint dimensions, exercises, export, app smoke test). |

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
