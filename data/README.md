# Data

## `sipora_2022_sector_scatter_counts.csv`

Hours of 2022 in each (Hs, Te) bin at the Sipora (Mentawai, Indonesia) site of the author's undergraduate thesis, for waves from the thesis direction sector 191.25-213.75° only (5,194 hours, about 59% of the year).
- **Bins:** 0.5 m in Hs and 0.5 s in Te. The app uses the bin centres.
- **Te:** derived from the peak period Tp with the JONSWAP (γ = 3.3) ratio.
- **These are offshore conditions.** The ERA5 node (2.0° S, 99.5° E) is in deep water, and the app applies the sea states at the device without any wave transformation.

**Source and licence.** The table is derived from ERA5 hourly wave data:

> Copernicus Climate Change Service (C3S): ERA5 hourly data on single levels from 1940 to present. C3S Climate Data Store (CDS). DOI: [10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47). Variables used: significant height of combined wind waves and swell (`swh`), peak wave period (`pp1d`), mean wave direction (`mwd`), 2022, hourly.

ERA5 data are distributed under the [Creative Commons Attribution 4.0 licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The data were modified by:
- selecting one grid node and one direction sector;
- converting Tp to Te;
- binning into an Hs-Te scatter of hours.

**Contains modified Copernicus Climate Change Service information 2026.** Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.
