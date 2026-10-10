"""Text shown with the Zheng et al. (2019) backend. Physics wording lives here only (Prompt B section 3)."""

TITLE = "Zheng, Zhang and Iglesias (2019): OWC half-embedded in a vertical wall (3D linear potential flow)"

NOTES = [
    "This backend models an ideal, perfectly reflecting, rigid, infinite vertical wall, a lossless linear "
    "Wells turbine and regular waves only. The doubling of the capture width ratio relative to an isolated "
    "device depends on the wall assumption; real coasts and breakwaters partly absorb or scatter waves "
    "(the author's reading, flagged as such).",
    "The optimal cPTO is chosen at every frequency (Eq. 39): an upper bound, a real turbine cannot retune.",
    "There is no isolated offshore OWC in this backend. The paper's open-sea curves come from a different "
    "model (its ref. [36]). The piston toy is not 'the offshore case' and is not compared like for like.",
    "Results are dimensionless through h, except the air-compressibility term aPTO = w V0 / (v^2 rho0), "
    "which makes them depend on h itself (the paper fixes h = 10 m, rho/rho0 = 1000, v = 340 m/s).",
    "eta above 1 is expected here. The bound used (derived for this app, not a cited result): at each wave "
    "direction eta <= 2 |Qe(beta)|^2 / mean over beta of |Qe|^2, whose average over beta is 2. A single "
    "direction may exceed 2.",
]

ACCURACY = (
    "Numerical accuracy at the paper's truncation M = 12, L = 20: the three ways of computing c (direct, "
    "far-field, Haskind) agree to about 1e-3 and the gap shrinks with M and L (truncation error). Changing "
    "(M, L) to (16, 30) moves c and a by up to a few percent near the sharp peaks; the series converge slowly, "
    "probably because the flow is singular at the corners of the chamber wall."
)

V0_SWITCH = "Air volume V0: the paper uses pi R^2 h (outer radius). pi Ri^2 h (inner radius) is offered because the paper does not test the choice."
