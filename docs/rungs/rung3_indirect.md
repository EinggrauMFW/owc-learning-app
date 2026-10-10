# Rung 3 (indirect): thin-wall OWC at a straight coast, against Martins-Rivas & Mei (2009a)

**Source of the reference values.** Zheng et al. (2019) J. Fluid Mech. 878:445-480 (doi 10.1017/jfm.2019.656), Figure 4. It plots Martins-Rivas & Mei's (2009a) thin-wall results as circles and Zheng's own lines for Ri/h = 0.49 (two OWCs 200 depths apart, so each behaves as a single device). We read it from the accepted-manuscript open copy at TU Delft (repository.tudelft.nl, record uuid:33ced909-a5e4-45cc-be1d-c6ac09f0cc04). The PDF itself is not included in this repository.

**How the values were read.** Opus read the circles off a 4x render of the figure using the axis pixel scale: 81 px per kh unit and 25.6 px per unit on the y-axis. Estimated read-off error: ±0.1 in value and ±0.02 in kh. Each peak is also only as sharp as the circle sampling allows.

**Why "indirect".** These are Martins-Rivas & Mei's values as replotted by Zheng's group and read by eye, not their published numbers. The direct rung 3 still needs the original paper.

Case: R/h = 0.5, Ri/h = 0.49, d/h = 0.2, h = 10 m. Scaling: (c̄, ā) = (c, a) w rho / R, as in that figure.

| Feature | Martins-Rivas & Mei (circles) | Zheng line | Ours (12,20) | Ours (16,30) |
| --- | --- | --- | --- | --- |
| c̄ main peak | 7.89 @ 1.72 | ≈ circles | 7.963 @ 1.727 | 7.969 @ 1.723 |
| ā maximum | 3.13 @ 1.36 | ≈ circles | 3.244 @ 1.325 | 3.247 @ 1.323 |
| ā minimum | −5.31 @ 2.32 | ≈ circles | −5.302 @ 2.314 | −5.303 @ 2.306 |
| ā at kh = 7 | −3.24 | ≈ circles | −3.215 | −3.200 |
| c̄ sloshing spike | 12.7 @ 4.05 | 13.2 @ 4.12 | 13.49 @ 4.131 | 13.56 @ 4.127 |
| ā spike max / min | 4.53 @ 4.00 / −8.24 @ 4.19 | ≈ 4.6 / ≈ −8.3 | 4.93 @ 4.07 / −8.51 @ 4.21 | 4.97 / −8.54 |

**Result.**
- **Main (pumping, or Helmholtz) mode:** agreement within the read-off error, at most 0.11 in value and 0.035 in kh.
- **Sloshing spike:** our values follow Zheng's line, but are 0.4-0.8 higher in value and about 0.07 higher in kh than Martins-Rivas & Mei's circles. Three things probably contribute:
  - a finite wall (Ri/h = 0.49) against an infinitely thin one;
  - circle sampling that misses the top of a peak only about 0.05 wide;
  - the slow convergence near this mode (rung 2).

  This is our reading, not a proven explanation.
