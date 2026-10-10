# Search log

All dates 2026-10-10. Each row is one HTTP call (curl --get --data-urlencode, User-Agent without contact info; Crossref calls spaced >=1.1 s; OpenAlex >=0.3 s). Raw JSON responses were kept locally and are not published (they contain full publisher abstracts); repeat any call from this log to regenerate them. (The first run of s2 was interrupted by a console-encoding error and re-run, so its first calls appear twice). Hits = OpenAlex meta.count / Crossref total-results / 1 for single-record. HTTP status shown; bodies were JSON-parsed (non-JSON noted).

| # | tag | endpoint | params | http | hits | note |
|---|---|---|---|---|---|---|
| 1 | c1_mei | https://api.openalex.org/works | search=Theory and Applications of Ocean Surface Waves Mei Stiassnie Yue; per_page=5 | 200 | 363 |  |
| 2 | c1_dean | https://api.openalex.org/works | search=Water Wave Mechanics for Engineers and Scientists Dean Dalrymple; per_page=5 | 200 | 1456 |  |
| 3 | c1_holth | https://api.openalex.org/works | search=Waves in Oceanic and Coastal Waters Holthuijsen; per_page=5 | 200 | 2593 |  |
| 4 | c2_evans82 | https://api.openalex.org/works | search=Evans A theory for wave-power absorption by oscillating bodies OR oscillating-water-column hydrodynamic; per_page=5 | 200 | 1328 |  |
| 5 | c2_sf85 | https://api.openalex.org/works | search=Sarmento Falcao Wave generation by an oscillating surface-pressure and its application in wave-energy extracti; per_page=5 | 200 | 65 |  |
| 6 | c2_fh16 | https://api.openalex.org/works | search=Oscillating-water-column wave energy converters and air turbines: A review; per_page=5 | 200 | 2223 |  |
| 7 | c3_fj | https://api.openalex.org/works | search=Falcao Justino OWC wave energy devices with air flow control; per_page=5 | 200 | 54 |  |
| 8 | c3_fh14 | https://api.openalex.org/works | search=Model-prototype similarity of oscillating-water-column wave energy converters; per_page=5 | 200 | 712 |  |
| 9 | c4_evans78 | https://api.openalex.org/works | search=Evans The oscillating water column wave-energy device; per_page=5 | 200 | 2246 |  |
| 10 | c4_falnes | https://api.openalex.org/works | search=Ocean Waves and Oscillating Systems Falnes; per_page=5 | 200 | 1322 |  |
| 11 | c5_newman62 | https://api.openalex.org/works | search=Newman The exciting forces on fixed bodies in waves; per_page=5 | 200 | 2373 |  |
| 12 | c5_budal | https://api.openalex.org/works | search=Budal Falnes A resonant point absorber of ocean-wave power; per_page=5 | 200 | 219 |  |
| 13 | c5_evans76 | https://api.openalex.org/works | search=Evans A theory for wave-power absorption by oscillating bodies; per_page=5 | 200 | 2721 |  |
| 14 | c5_newman76 | https://api.openalex.org/works | search=Newman The interaction of stationary vessels with regular waves; per_page=5 | 200 | 760 |  |
| 15 | c5_stansell | https://api.openalex.org/works | search=Stansell Pizer Haskind maximum capture width axisymmetric wave energy; per_page=5 | 200 | 0 |  |
| 16 | c5_porter | https://api.openalex.org/works | search=Porter Zheng Greaves Extending limits for wave power absorption by axisymmetric devices; per_page=5 | 200 | 17 |  |
| 17 | c6_rag | https://api.openalex.org/works | search=Raghunathan The Wells air turbine for wave energy conversion; per_page=5 | 200 | 265 |  |
| 18 | c7_mrm_tip | https://api.openalex.org/works | search=Martins-Rivas Mei Wave power extraction from an oscillating water column at the tip of a breakwater; per_page=5 | 200 | 61 |  |
| 19 | c7_mrm_coast | https://api.openalex.org/works | search=Martins-Rivas Mei Wave power extraction from an oscillating water column along a straight coast; per_page=5 | 200 | 54 |  |
| 20 | c7_lovas | https://api.openalex.org/works | search=Lovas Mei Liu Oscillating water column at a coastal corner for wave power extraction; per_page=5 | 200 | 20 |  |
| 21 | c7_zheng | https://api.openalex.org/works | search=Zheng Zhang Iglesias Coast/breakwater-integrated OWC wave energy converters; per_page=5 | 200 | 111 |  |
| 22 | c8_garrett | https://api.openalex.org/works | search=Garrett Wave forces on a circular dock; per_page=5 | 200 | 229 |  |
| 23 | c8_yeung | https://api.openalex.org/works | search=Yeung Added mass and damping of a vertical cylinder in finite-depth waters; per_page=5 | 200 | 134 |  |
| 24 | c9_ep | https://api.openalex.org/works | search=Evans Porter Hydrodynamic characteristics of an oscillating water column device; per_page=5 | 200 | 247 |  |
| 25 | c9_conv | https://api.openalex.org/works | search=convergence matched eigenfunction expansion edge singularity thin barrier wave; per_page=5 | 200 | 238 |  |
| 26 | c10_ning | https://api.openalex.org/works | search=Ning Hydrodynamic performance of a fixed OWC wave energy device: an experimental study; per_page=5 | 200 | 365 |  |
| 27 | c10_mut | https://api.openalex.org/works | search=Mutriku breakwater wave energy plant OWC; per_page=5 | 200 | 262 |  |
| 28 | c10_mustapa | https://api.openalex.org/works | search=Wave energy device and breakwater integration: a review; per_page=5 | 200 | 2000 |  |
| 29 | c11_newman | https://api.openalex.org/works | search=Newman Marine Hydrodynamics; per_page=5 | 200 | 6600 |  |
| 30 | x_evans82 | https://api.crossref.org/works | query.bibliographic=Evans 1982 Wave-power absorption by systems of oscillating surface pressure distributions Journal of Fluid Mec; rows=4 | 200 | 739610 |  |
| 31 | x_sf85 | https://api.crossref.org/works | query.bibliographic=Sarmento Falcao 1985 Wave generation by an oscillating surface-pressure and its application in wave-energy ext; rows=4 | 200 | 148588 |  |
| 32 | x_fj99 | https://api.crossref.org/works | query.bibliographic=Falcao Justino 1999 OWC wave energy devices with air flow control Ocean Engineering; rows=4 | 200 | 1133010 |  |
| 33 | x_evans78 | https://api.crossref.org/works | query.bibliographic=Evans 1978 The oscillating water column wave-energy device Journal of the Institute of Mathematics and its App; rows=4 | 200 | 976869 |  |
| 34 | x_budal | https://api.crossref.org/works | query.bibliographic=Budal Falnes 1975 A resonant point absorber of ocean-wave power Nature; rows=4 | 200 | 94670 |  |
| 35 | x_evans76 | https://api.crossref.org/works | query.bibliographic=Evans 1976 A theory for wave-power absorption by oscillating bodies Journal of Fluid Mechanics 77 1; rows=4 | 200 | 305934 |  |
| 36 | x_garrett | https://api.crossref.org/works | query.bibliographic=Garrett 1971 Wave forces on a circular dock Journal of Fluid Mechanics 46 129; rows=4 | 200 | 162740 |  |
| 37 | x_yeung | https://api.crossref.org/works | query.bibliographic=Yeung 1981 Added mass and damping of a vertical cylinder in finite-depth waters Applied Ocean Research 3 119; rows=4 | 200 | 612595 |  |
| 38 | x_rag | https://api.crossref.org/works | query.bibliographic=Raghunathan 1995 The Wells air turbine for wave energy conversion Progress in Aerospace Sciences 31 335; rows=4 | 200 | 575645 |  |
| 39 | x_mrm_tip | https://api.crossref.org/works | query.bibliographic=Martins-Rivas Mei 2009 Wave power extraction from an oscillating water column at the tip of a breakwater Journ; rows=4 | 200 | 42126 |  |
| 40 | x_mrm_coast | https://api.crossref.org/works | query.bibliographic=Martins-Rivas Mei 2009 Wave power extraction from an oscillating water column along a straight coast Ocean Eng; rows=4 | 200 | 106691 |  |
| 41 | x_lovas | https://api.crossref.org/works | query.bibliographic=Lovas Mei Liu 2010 Oscillating water column at a coastal corner for wave power extraction Applied Ocean Resear; rows=4 | 200 | 130828 |  |
| 42 | x_ning | https://api.crossref.org/works | query.bibliographic=Ning 2016 Hydrodynamic performance of a fixed OWC wave energy device: an experimental study Renewable Energy; rows=4 | 200 | 3520221 |  |
| 43 | x_newman62 | https://api.crossref.org/works | query.bibliographic=Newman 1962 The exciting forces on fixed bodies in waves Journal of Ship Research 6; rows=4 | 200 | 10884573 |  |
| 44 | x_newman76 | https://api.crossref.org/works | query.bibliographic=Newman 1976 The interaction of stationary vessels with regular waves Proceedings 11th Symposium on Naval Hydro; rows=4 | 200 | 73652 |  |
| 45 | x_mutriku | https://api.crossref.org/works | query.bibliographic=Mutriku breakwater wave energy plant OWC performance results; rows=4 | 200 | 7352165 |  |
| 46 | x_falnes | https://api.crossref.org/works | query.bibliographic=Falnes Ocean Waves and Oscillating Systems Cambridge University Press; rows=4 | 200 | 8146829 |  |
| 47 | x_falnes2 | https://api.crossref.org/works | query.bibliographic=Falnes Kurniawan Ocean Waves and Oscillating Systems second edition; rows=4 | 200 | 6364775 |  |
| 48 | x_newman_mh | https://api.crossref.org/works | query.bibliographic=Newman Marine Hydrodynamics MIT Press; rows=4 | 200 | 1913309 |  |
| 49 | x_evans82 | https://api.crossref.org/works | query.bibliographic=Evans 1982 Wave-power absorption by systems of oscillating surface pressure distributions Journal of Fluid Mec; rows=4 | 200 | 739610 |  |
| 50 | x_sf85 | https://api.crossref.org/works | query.bibliographic=Sarmento Falcao 1985 Wave generation by an oscillating surface-pressure and its application in wave-energy ext; rows=4 | 200 | 148588 |  |
| 51 | x_fj99 | https://api.crossref.org/works | query.bibliographic=Falcao Justino 1999 OWC wave energy devices with air flow control Ocean Engineering; rows=4 | 200 | 1133010 |  |
| 52 | x_evans78 | https://api.crossref.org/works | query.bibliographic=Evans 1978 The oscillating water column wave-energy device Journal of the Institute of Mathematics and its App; rows=4 | 200 | 976869 |  |
| 53 | x_budal | https://api.crossref.org/works | query.bibliographic=Budal Falnes 1975 A resonant point absorber of ocean-wave power Nature; rows=4 | 200 | 94670 |  |
| 54 | x_evans76 | https://api.crossref.org/works | query.bibliographic=Evans 1976 A theory for wave-power absorption by oscillating bodies Journal of Fluid Mechanics 77 1; rows=4 | 200 | 305934 |  |
| 55 | x_garrett | https://api.crossref.org/works | query.bibliographic=Garrett 1971 Wave forces on a circular dock Journal of Fluid Mechanics 46 129; rows=4 | 200 | 162740 |  |
| 56 | x_yeung | https://api.crossref.org/works | query.bibliographic=Yeung 1981 Added mass and damping of a vertical cylinder in finite-depth waters Applied Ocean Research 3 119; rows=4 | 200 | 612595 |  |
| 57 | x_rag | https://api.crossref.org/works | query.bibliographic=Raghunathan 1995 The Wells air turbine for wave energy conversion Progress in Aerospace Sciences 31 335; rows=4 | 200 | 575645 |  |
| 58 | x_mrm_tip | https://api.crossref.org/works | query.bibliographic=Martins-Rivas Mei 2009 Wave power extraction from an oscillating water column at the tip of a breakwater Journ; rows=4 | 200 | 42126 |  |
| 59 | x_mrm_coast | https://api.crossref.org/works | query.bibliographic=Martins-Rivas Mei 2009 Wave power extraction from an oscillating water column along a straight coast Ocean Eng; rows=4 | 200 | 106691 |  |
| 60 | x_lovas | https://api.crossref.org/works | query.bibliographic=Lovas Mei Liu 2010 Oscillating water column at a coastal corner for wave power extraction Applied Ocean Resear; rows=4 | 200 | 130828 |  |
| 61 | x_ning | https://api.crossref.org/works | query.bibliographic=Ning 2016 Hydrodynamic performance of a fixed OWC wave energy device: an experimental study Renewable Energy; rows=4 | 200 | 3520221 |  |
| 62 | x_newman62 | https://api.crossref.org/works | query.bibliographic=Newman 1962 The exciting forces on fixed bodies in waves Journal of Ship Research 6; rows=4 | 200 | 10884573 |  |
| 63 | x_newman76 | https://api.crossref.org/works | query.bibliographic=Newman 1976 The interaction of stationary vessels with regular waves Proceedings 11th Symposium on Naval Hydro; rows=4 | 200 | 73652 |  |
| 64 | x_mutriku | https://api.crossref.org/works | query.bibliographic=Mutriku breakwater wave energy plant OWC performance results; rows=4 | 200 | 7352165 |  |
| 65 | x_falnes | https://api.crossref.org/works | query.bibliographic=Falnes Ocean Waves and Oscillating Systems Cambridge University Press; rows=4 | 200 | 8146829 |  |
| 66 | x_falnes2 | https://api.crossref.org/works | query.bibliographic=Falnes Kurniawan Ocean Waves and Oscillating Systems second edition; rows=4 | 200 | 6364775 |  |
| 67 | x_newman_mh | https://api.crossref.org/works | query.bibliographic=Newman Marine Hydrodynamics MIT Press; rows=4 | 200 | 1913309 |  |
| 68 | y_ning | https://api.crossref.org/works | query.bibliographic=Ning Zou Teng Liu Wang Hydrodynamic performance of a fixed OWC wave energy device: an experimental study Renew; rows=5 | 200 | 1123667 |  |
| 69 | y_ning_b | https://api.crossref.org/works | query.bibliographic=Ning hydrodynamic OWC chamber experimental fixed breakwater 2016 Renewable Energy; rows=5; filter=from-pub-date:2015,until-pub-date:2017,type:journal-article | 200 | 124382 |  |
| 70 | y_mei | https://api.crossref.org/works | query.bibliographic=Mei Stiassnie Yue Theory and Applications of Ocean Surface Waves World Scientific; rows=3 | 200 | 434421 |  |
| 71 | y_dean | https://api.crossref.org/works | query.bibliographic=Dean Dalrymple Water Wave Mechanics for Engineers and Scientists World Scientific; rows=3 | 200 | 7051291 |  |
| 72 | y_holt | https://api.crossref.org/works | query.bibliographic=Holthuijsen Waves in Oceanic and Coastal Waters Cambridge University Press 2007; rows=3 | 200 | 6995521 |  |
| 73 | y_mutriku | https://api.crossref.org/works | query.bibliographic=Mutriku wave energy plant breakwater OWC operational data performance Torre-Enciso OR Ibarra-Berastegi OR Medi; rows=6 | 200 | 11137 |  |
| 74 | y_stansell | https://api.crossref.org/works | query.bibliographic=Stansell Pizer maximum capture width Haskind axisymmetric wave energy; rows=3 | 200 | 3471774 |  |
| 75 | z_stansell | https://api.openalex.org/works | search=Stansell Pizer maximum capture width; per_page=5; filter=title.search:capture width | 200 | 0 |  |
| 76 | z_ning | https://api.openalex.org/works | search=Hydrodynamic performance of a fixed OWC wave energy device an experimental study; per_page=5; filter=title.search:fixed OWC wave energy device experimental,publication_year:2015-2017 | 200 | 0 |  |
| 77 | z_newman76 | https://api.openalex.org/works | search=interaction of stationary vessels with regular waves; per_page=5; filter=title.search:stationary vessels with regular waves | 200 | 0 |  |
| 78 | z_mei | https://api.openalex.org/works | search=Theory and Applications of Ocean Surface Waves; per_page=5; filter=type:book | 200 | 5083 |  |
| 79 | arxiv_1112.3494 | https://export.arxiv.org/api/query | id_list=1112.3494 | 429 | None | NONJSON Rate exceeded. |
| 80 | zheng2019_citers | https://api.openalex.org/works | filter=cites:W2939890631,from_publication_date:2019-06-01; per_page=100; sort=cited_by_count:desc | 200 | 143 |  |
| 81 | arxiv_1112.3494_retry | https://export.arxiv.org/api/query | id_list=1112.3494 | 429 | None | NONJSON Rate exceeded. |
| 82 | w_c9a | https://api.crossref.org/works | query.bibliographic=Porter Evans Complementary approximations to wave scattering by vertical barriers Journal of Fluid Mechanics; rows=3 | 200 | 136107 |  |
| 83 | w_c9b | https://api.crossref.org/works | query.bibliographic=edge singularity eigenfunction expansion slow convergence vertical barrier water waves matching; rows=5 | 200 | 37614 |  |
| 84 | w_mut | https://api.crossref.org/works | query.bibliographic=Torre-Enciso Mutriku wave power plant: from the thinking out to the reality; rows=3 | 200 | 316621 |  |
| 85 | zheng2019_citers_p2 | https://api.openalex.org/works | filter=cites:W2939890631,from_publication_date:2019-06-01; per_page=100; page=2; sort=cited_by_count:desc | 200 | 143 |  |
| 86 | cr_10_1142_5566 | https://api.crossref.org/works/10.1142%2F5566 |  | 200 | 1 |  |
| 87 | oa_10_1142_5566 | https://api.openalex.org/works/doi:10.1142/5566 |  | 200 | 1 |  |
| 88 | cr_10_1142_10212 | https://api.crossref.org/works/10.1142%2F10212 |  | 200 | 1 |  |
| 89 | oa_10_1142_10212 | https://api.openalex.org/works/doi:10.1142/10212 |  | 200 | 1 |  |
| 90 | cr_10_1142_1232 | https://api.crossref.org/works/10.1142%2F1232 |  | 200 | 1 |  |
| 91 | oa_10_1142_1232 | https://api.openalex.org/works/doi:10.1142/1232 |  | 200 | 1 |  |
| 92 | cr_10_1017_cbo9780511618536 | https://api.crossref.org/works/10.1017%2Fcbo9780511618536 |  | 200 | 1 |  |
| 93 | oa_10_1017_cbo9780511618536 | https://api.openalex.org/works/doi:10.1017/cbo9780511618536 |  | 200 | 1 |  |
| 94 | cr_10_1017_s0022112082000263 | https://api.crossref.org/works/10.1017%2Fs0022112082000263 |  | 200 | 1 |  |
| 95 | oa_10_1017_s0022112082000263 | https://api.openalex.org/works/doi:10.1017/s0022112082000263 |  | 200 | 1 |  |
| 96 | cr_10_1017_s0022112085000234 | https://api.crossref.org/works/10.1017%2Fs0022112085000234 |  | 200 | 1 |  |
| 97 | oa_10_1017_s0022112085000234 | https://api.openalex.org/works/doi:10.1017/s0022112085000234 |  | 200 | 1 |  |
| 98 | cr_10_1016_j_renene_2015_07_086 | https://api.crossref.org/works/10.1016%2Fj.renene.2015.07.086 |  | 200 | 1 |  |
| 99 | oa_10_1016_j_renene_2015_07_086 | https://api.openalex.org/works/doi:10.1016/j.renene.2015.07.086 |  | 200 | 1 |  |
| 100 | cr_10_1016_s0029_8018_98_00075_4 | https://api.crossref.org/works/10.1016%2Fs0029-8018%2898%2900075-4 |  | 200 | 1 |  |
| 101 | oa_10_1016_s0029_8018_98_00075_4 | https://api.openalex.org/works/doi:10.1016/s0029-8018(98)00075-4 |  | 200 | 1 |  |
| 102 | cr_10_1016_j_ijome_2014_05_002 | https://api.crossref.org/works/10.1016%2Fj.ijome.2014.05.002 |  | 200 | 1 |  |
| 103 | oa_10_1016_j_ijome_2014_05_002 | https://api.openalex.org/works/doi:10.1016/j.ijome.2014.05.002 |  | 200 | 1 |  |
| 104 | cr_10_1016_j_rser_2019_04_040 | https://api.crossref.org/works/10.1016%2Fj.rser.2019.04.040 |  | 200 | 1 |  |
| 105 | oa_10_1016_j_rser_2019_04_040 | https://api.openalex.org/works/doi:10.1016/j.rser.2019.04.040 |  | 200 | 1 |  |
| 106 | cr_10_1093_imamat_22_4_423 | https://api.crossref.org/works/10.1093%2Fimamat%2F22.4.423 |  | 200 | 1 |  |
| 107 | oa_10_1093_imamat_22_4_423 | https://api.openalex.org/works/doi:10.1093/imamat/22.4.423 |  | 200 | 1 |  |
| 108 | cr_10_1017_cbo9780511754630 | https://api.crossref.org/works/10.1017%2Fcbo9780511754630 |  | 200 | 1 |  |
| 109 | oa_10_1017_cbo9780511754630 | https://api.openalex.org/works/doi:10.1017/cbo9780511754630 |  | 200 | 1 |  |
| 110 | cr_10_1017_9781108674812 | https://api.crossref.org/works/10.1017%2F9781108674812 |  | 200 | 1 |  |
| 111 | oa_10_1017_9781108674812 | https://api.openalex.org/works/doi:10.1017/9781108674812 |  | 200 | 1 |  |
| 112 | cr_10_5957_jsr_1962_6_4_10 | https://api.crossref.org/works/10.5957%2Fjsr.1962.6.4.10 |  | 200 | 1 |  |
| 113 | oa_10_5957_jsr_1962_6_4_10 | https://api.openalex.org/works/doi:10.5957/jsr.1962.6.4.10 |  | 200 | 1 |  |
| 114 | cr_10_1038_256478a0 | https://api.crossref.org/works/10.1038%2F256478a0 |  | 200 | 1 |  |
| 115 | oa_10_1038_256478a0 | https://api.openalex.org/works/doi:10.1038/256478a0 |  | 200 | 1 |  |
| 116 | cr_10_1017_s0022112076001109 | https://api.crossref.org/works/10.1017%2Fs0022112076001109 |  | 200 | 1 |  |
| 117 | oa_10_1017_s0022112076001109 | https://api.openalex.org/works/doi:10.1017/s0022112076001109 |  | 200 | 1 |  |
| 118 | cr_10_1017_jfm_2021_645 | https://api.crossref.org/works/10.1017%2Fjfm.2021.645 |  | 200 | 1 |  |
| 119 | oa_10_1017_jfm_2021_645 | https://api.openalex.org/works/doi:10.1017/jfm.2021.645 |  | 200 | 1 |  |
| 120 | cr_10_48550_arxiv_1112_3494 | https://api.crossref.org/works/10.48550%2Farxiv.1112.3494 |  | 404 | None | NONJSON Resource not found. |
| 121 | oa_10_48550_arxiv_1112_3494 | https://api.openalex.org/works/doi:10.48550/arxiv.1112.3494 |  | 200 | 1 |  |
| 122 | cr_10_1016_0376_0421_95_00001_f | https://api.crossref.org/works/10.1016%2F0376-0421%2895%2900001-f |  | 200 | 1 |  |
| 123 | oa_10_1016_0376_0421_95_00001_f | https://api.openalex.org/works/doi:10.1016/0376-0421(95)00001-f |  | 200 | 1 |  |
| 124 | cr_10_1017_s0022112009005990 | https://api.crossref.org/works/10.1017%2Fs0022112009005990 |  | 200 | 1 |  |
| 125 | oa_10_1017_s0022112009005990 | https://api.openalex.org/works/doi:10.1017/s0022112009005990 |  | 200 | 1 |  |
| 126 | cr_10_1016_j_oceaneng_2009_01_009 | https://api.crossref.org/works/10.1016%2Fj.oceaneng.2009.01.009 |  | 200 | 1 |  |
| 127 | oa_10_1016_j_oceaneng_2009_01_009 | https://api.openalex.org/works/doi:10.1016/j.oceaneng.2009.01.009 |  | 200 | 1 |  |
| 128 | cr_10_1016_j_apor_2010_06_004 | https://api.crossref.org/works/10.1016%2Fj.apor.2010.06.004 |  | 200 | 1 |  |
| 129 | oa_10_1016_j_apor_2010_06_004 | https://api.openalex.org/works/doi:10.1016/j.apor.2010.06.004 |  | 200 | 1 |  |
| 130 | cr_10_1016_j_marstruc_2019_04_001 | https://api.crossref.org/works/10.1016%2Fj.marstruc.2019.04.001 |  | 200 | 1 |  |
| 131 | oa_10_1016_j_marstruc_2019_04_001 | https://api.openalex.org/works/doi:10.1016/j.marstruc.2019.04.001 |  | 200 | 1 |  |
| 132 | cr_10_1017_jfm_2019_656 | https://api.crossref.org/works/10.1017%2Fjfm.2019.656 |  | 200 | 1 |  |
| 133 | oa_10_1017_jfm_2019_656 | https://api.openalex.org/works/doi:10.1017/jfm.2019.656 |  | 200 | 1 |  |
| 134 | cr_10_1017_s0022112071000430 | https://api.crossref.org/works/10.1017%2Fs0022112071000430 |  | 200 | 1 |  |
| 135 | oa_10_1017_s0022112071000430 | https://api.openalex.org/works/doi:10.1017/s0022112071000430 |  | 200 | 1 |  |
| 136 | cr_10_1016_0141_1187_81_90101_2 | https://api.crossref.org/works/10.1016%2F0141-1187%2881%2990101-2 |  | 200 | 1 |  |
| 137 | oa_10_1016_0141_1187_81_90101_2 | https://api.openalex.org/works/doi:10.1016/0141-1187(81)90101-2 |  | 200 | 1 |  |
| 138 | cr_10_1016_0141_1187_95_00008_9 | https://api.crossref.org/works/10.1016%2F0141-1187%2895%2900008-9 |  | 200 | 1 |  |
| 139 | oa_10_1016_0141_1187_95_00008_9 | https://api.openalex.org/works/doi:10.1016/0141-1187(95)00008-9 |  | 200 | 1 |  |
| 140 | cr_10_1017_s0022112095002849 | https://api.crossref.org/works/10.1017%2Fs0022112095002849 |  | 200 | 1 |  |
| 141 | oa_10_1017_s0022112095002849 | https://api.openalex.org/works/doi:10.1017/s0022112095002849 |  | 200 | 1 |  |
| 142 | cr_10_1016_j_wavemoti_2024_103421 | https://api.crossref.org/works/10.1016%2Fj.wavemoti.2024.103421 |  | 200 | 1 |  |
| 143 | oa_10_1016_j_wavemoti_2024_103421 | https://api.openalex.org/works/doi:10.1016/j.wavemoti.2024.103421 |  | 200 | 1 |  |
| 144 | cr_10_3390_jmse13030398 | https://api.crossref.org/works/10.3390%2Fjmse13030398 |  | 200 | 1 |  |
| 145 | oa_10_3390_jmse13030398 | https://api.openalex.org/works/doi:10.3390/jmse13030398 |  | 200 | 1 |  |
| 146 | cr_10_1016_j_apenergy_2016_01_107 | https://api.crossref.org/works/10.1016%2Fj.apenergy.2016.01.107 |  | 200 | 1 |  |
| 147 | oa_10_1016_j_apenergy_2016_01_107 | https://api.openalex.org/works/doi:10.1016/j.apenergy.2016.01.107 |  | 200 | 1 |  |
| 148 | cr_10_1016_j_energy_2016_09_001 | https://api.crossref.org/works/10.1016%2Fj.energy.2016.09.001 |  | 200 | 1 |  |
| 149 | oa_10_1016_j_energy_2016_09_001 | https://api.openalex.org/works/doi:10.1016/j.energy.2016.09.001 |  | 200 | 1 |  |
| 150 | cr_10_1016_j_energy_2015_02_012 | https://api.crossref.org/works/10.1016%2Fj.energy.2015.02.012 |  | 200 | 1 |  |
| 151 | oa_10_1016_j_energy_2015_02_012 | https://api.openalex.org/works/doi:10.1016/j.energy.2015.02.012 |  | 200 | 1 |  |
| 152 | cr_10_1016_j_rser_2017_03_110 | https://api.crossref.org/works/10.1016%2Fj.rser.2017.03.110 |  | 200 | 1 |  |
| 153 | oa_10_1016_j_rser_2017_03_110 | https://api.openalex.org/works/doi:10.1016/j.rser.2017.03.110 |  | 200 | 1 |  |
| 154 | cr_10_1061_9780784480304_063 | https://api.crossref.org/works/10.1061%2F9780784480304.063 |  | 200 | 1 |  |
| 155 | oa_10_1061_9780784480304_063 | https://api.openalex.org/works/doi:10.1061/9780784480304.063 |  | 200 | 1 |  |
| 156 | cr_10_1016_j_oceaneng_2021_108654 | https://api.crossref.org/works/10.1016%2Fj.oceaneng.2021.108654 |  | 200 | 1 |  |
| 157 | oa_10_1016_j_oceaneng_2021_108654 | https://api.openalex.org/works/doi:10.1016/j.oceaneng.2021.108654 |  | 200 | 1 |  |
| 158 | cr_10_1115_omae2017_62651 | https://api.crossref.org/works/10.1115%2Fomae2017-62651 |  | 200 | 1 |  |
| 159 | oa_10_1115_omae2017_62651 | https://api.openalex.org/works/doi:10.1115/omae2017-62651 |  | 200 | 1 |  |
| 160 | cr_10_1016_j_rser_2023_113299 | https://api.crossref.org/works/10.1016%2Fj.rser.2023.113299 |  | 200 | 1 |  |
| 161 | oa_10_1016_j_rser_2023_113299 | https://api.openalex.org/works/doi:10.1016/j.rser.2023.113299 |  | 200 | 1 |  |
| 162 | cr_10_7551_mitpress_4443_001_0001 | https://api.crossref.org/works/10.7551%2Fmitpress%2F4443.001.0001 |  | 200 | 1 |  |
| 163 | oa_10_7551_mitpress_4443_001_0001 | https://api.openalex.org/works/doi:10.7551/mitpress/4443.001.0001 |  | 200 | 1 |  |
| 164 | arxiv_1112.3494_retry2 | https://export.arxiv.org/api/query | id_list=1112.3494 | 429 | None | NONJSON Rate exceeded. |

Total API calls: 164
