# Literature support for the app's theory

Search date: 2026-10-10. Databases: Crossref and OpenAlex (164 API calls, every query logged in [docs/literature/search_log.md](docs/literature/search_log.md)).
- 38 records, with BibTeX in [docs/literature/references.bib](docs/literature/references.bib).
- Per-claim evidence table in [docs/literature/claim_map.md](docs/literature/claim_map.md).
- Papers citing Zheng 2019 in [docs/literature/zheng2019_citers.md](docs/literature/zheng2019_citers.md) (143 found).

**What "verified" means here:**
- **Identity:** every DOI was resolved on Crossref, and title, first author, year, journal, volume and pages were compared. Opus independently re-checked six of them.
- **Support:** judged from the abstract or the registered title only. Full texts are mostly paywalled and **were not read**.
  - **Supported:** the abstract states the point.
  - **Topical:** the paper is the standard source on the topic, but its abstract does not show the specific statement.
  - **Not checked:** there is no abstract. Treat these as pointers, not proof.

## Claim by claim

| # | What the app uses | Key verified sources | Support | Independent check in this repo |
| --- | --- | --- | --- | --- |
| C1 | Linear dispersion, group velocity, energy flux Pin = ρgA²c_g/2 | Mei, Stiassnie & Yue (2005, 2nd ed. 2016); Dean & Dalrymple (1991); Holthuijsen (2007), all textbooks | topical (standard textbook results) | **derived with sympy** (S6); dispersion checked against an independent root solver (7e-14) |
| C2 | OWC frequency-domain chamber equation, [(c+cPTO) − i(a+aPTO)] p = Qe | Evans (1982) JFM 114:481; **Sarmento & Falcão (1985) JFM 150:467**; Falcão & Henriques (2016) Renew. Energy 85:1391 (review) | **supported** (Sarmento & Falcão: linear OWC analysis with a turbine); topical (Evans: absorption by oscillating surface pressures) | **derived** from the column and air-chamber equations (S1-S3); time-domain integration matches to 1e-12 |
| C3 | Linearised air compressibility, aPTO = ωV0/(v²ρ0) | **Sarmento & Falcão (1985)**; Falcão & Justino (1999) Ocean Eng. 26:1275; Falcão & Henriques (2014) Int. J. Marine Energy 6:18; Falcão & Henriques (2019) RSER 112:483 ("spring-like air compressibility effect") | **supported** (Sarmento & Falcão abstract: compressibility can be important and can be linearised); topical (the others) | **derived** from isentropic compression (S2) |
| C4 | Rigid-piston (lumped) OWC model, the toy | **Evans (1978) IMA J. Appl. Math. 22:423**; Falnes (2002), Falnes & Kurniawan (2020) | **supported** (Evans 1978: a float on a column with spring-dashpot, absorption efficiency) | derived (S1); its limits quantified (L2, section 4 of VERIFICATION.md) |
| C5 | Haskind relation; maximum capture width 1/k = λ/2π for an axisymmetric absorber; it underlies the toy's Qe | **Newman (1962) J. Ship Res. 6:10** (Haskind relations); Budal & Falnes (1975) Nature 256:478; Evans (1976) JFM 77:1; Porter, Zheng & Greaves (2021) JFM 924 (open access) | **supported** (Newman: Haskind relation); topical (others) | the toy reproduces P/Pin = 1/k (Exercise 3); the Zheng solver satisfies Haskind to 1e-3 (rung 1) |
| C6 | Linear Wells turbine (flow ∝ pressure) | Raghunathan (1995) Prog. Aerosp. Sci. 31:335; Falcão & Henriques (2016) | not checked (no abstracts); standard practice, also stated in Zheng 2019 §2 | — (an assumption) |
| C7 | 3D OWC at a wall or coast by eigen-function matching; the wall increases absorption | Martins-Rivas & Mei (2009) JFM 626:395 and Ocean Eng. 36:426; Lovas, Mei & Liu (2010) Appl. Ocean Res. 32:267; Zheng, Zhang & Iglesias (2019) Mar. Struct. 66:121 (open copy); **Zheng et al. (2019) JFM 878:445** (open copy) | **supported** (Zheng JFM 2019: eigenfunction matching at a vertical coast, linear PTO with compressibility, coast effect enhances extraction); topical (the rest) | rungs 1, 2, 4, 5, 6; **long-wave limit L1** (below) |
| C8 | Eigen-function expansions for truncated cylinders in finite depth | Garrett (1971) JFM 46:129; Yeung (1981) Appl. Ocean Res. 3:119 | topical (Garrett: Bessel-function expansion for a circular dock) | rung 1 (three independent outputs agree) |
| C9 | Slow convergence caused by flow singularities at sharp wall corners (my explanation of rung 2) | Evans & Porter (1995) Appl. Ocean Res. 17:155; Porter & Evans (1995) JFM 294:155; **Wilks (2025) JMSE 13:398 (open access)** | **supported** (Wilks 2025: convergence of eigenfunction matching against singularity-respecting Galerkin methods, corner singularities named explicitly) | rung 2 measured: c and a change 1-4% from (12,20) to (16,30) |
| C10 | Experiments and field data on fixed or breakwater OWCs | Ning et al. (2016) Appl. Energy 168:636; Ning et al. (2016) Energy 115:326; Mustapa et al. (2017) RSER 77:43; Mutriku plant: Medina-Lopez (2017), Henriques (2017), Ibarra-Berastegi (2021, open access), Carrelhas (2023, open access) | topical; **no abstract reports Qe, c, a or capture-width data in a form the app can be compared with** | none yet (see "What is still missing") |
| C11 | Froude-Krylov force for a small body (used for the ζ estimate) | Newman (1977) Marine Hydrodynamics; Falnes (2002) | not checked (no abstracts); textbook result | used only as a labelled estimate (VERIFICATION.md §4) |

## Validation done in this repository (not from the literature)

This is the strongest evidence, because it does not depend on anyone's paper:
- **Sympy derivations** of every toy formula from its governing equations, and a **time-domain simulation** matching to 1e-12 ([VERIFICATION.md](VERIFICATION.md)).
- **Long-wave limit at a reflecting wall** ([verification/validate_limits.py](verification/validate_limits.py)). For kR → 0 the chamber surface follows the standing wave, 2A at the wall, so |Qe| → 2ωAπRi² and, through Haskind, c → π²ω³Ri⁴Z₀(0)²/(2ρg²h). The Zheng solver converges to both:

| kh | 0.4 | 0.2 | 0.1 | 0.05 | 0.025 |
| --- | --- | --- | --- | --- | --- |
| \|Qe\| / limit | 1.0319 | 1.0086 | 1.0024 | 1.00065 | 1.00018 |
| c / limit | 1.062 | 1.0165 | 1.0046 | 1.0013 | 1.00034 |

  The error falls like (kR)². This independently confirms three things: the scattering solution, the wall doubling of the incident wave, and the Haskind constant in Zheng's Eq. 36.

- **Low-frequency scaling** of c: the Zheng solver gives a slope of 3.01, matching the physics (3). The toy gives 2.01, the artefact of its constant damping.

## What the literature does NOT settle, and what is still missing

- **Rung 3** (thin-wall comparison with Martins-Rivas & Mei 2009) **still needs the paper**. OpenAlex lists no open copy of either Martins-Rivas & Mei paper, of Evans & Porter (1995), or of Lovas et al. (2010).
- **Zheng et al. (2019) JFM 878 was downloaded** from TU Delft's repository (the handle link is dead, and Plymouth's PEARL returned 403). Its Fig. 4 replots Martins-Rivas & Mei's thin-wall c and a. Our solver matches the main mode within read-off error: an **indirect rung 3**, see docs/rungs/rung3_indirect.md.
- **No experimental dataset** in the abstracts found gives capture width against kh for a wall-embedded circular OWC, so the app has **no validation against measurements**. Mutriku papers report plant operation, not linear-theory coefficients.
- **About two thirds of the abstracts are missing** from OpenAlex, so many entries are "topical" or "not checked". The support column must not be read as proof that a paper states a specific formula.

## Corrections made after this search

- **VERIFICATION.md cited "Stansell & Pizer, arXiv:1112.3494"** for the 1/k limit. That paper is about line absorbers (Appl. Ocean Res. 40:83, 2013) and only restates the point-absorber limit in its introduction. It is now replaced by the primary sources: Newman (1962), Budal & Falnes (1975), Evans (1976), plus Porter et al. (2021).
- **A remembered reference, "Ning et al. 2016, Renewable Energy", does not exist.** The real paper is Ning et al. 2016, Applied Energy 168:636-648. It was never cited in the app's documents.
- **Two Crossref metadata errors** were fixed in the BibTeX file: Budal is spelled "BUDAR" in Crossref, and the given and family names of Mei et al. are swapped.

Tools: the paper-lookup, citation-management and literature-review skills from Scientific Agent Skills (Kassis et al. 2026, arXiv:2609.00065).
