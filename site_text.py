"""Text for the "Site & annual energy" tab. Physics wording lives here only."""

TITLE = "Irregular waves and annual energy"

INTRO = (
    "A real sea is a sum of many regular waves with different periods and heights, described by a spectrum S(w). "
    "Because the model is linear, the device's power in a sea state is the sum of its power in each component: "
    "P = integral of 2 S(w) P1(w) dw, where P1 is the power in a regular wave of 1 m amplitude. "
    "The incident power per metre of crest is J = rho g integral of S(w) cg(w) dw."
)

DEFINITIONS = [
    ("Significant wave height Hm0 (Hs) [m]", "4 sqrt(m0), with m0 the area under the spectrum. Close to the mean height of the highest third of the waves."),
    ("Energy period Te [s]", "2 pi m_{-1}/m0. The period of a regular wave with the same height that carries the same power in deep water. Scatter tables for wave energy use Te."),
    ("Peak period Tp [s]", "Period of the spectrum's peak. For JONSWAP with gamma = 3.3, Te = 0.903 Tp (computed here)."),
    ("JONSWAP spectrum", "A standard shape for wind seas and swell; gamma sets how peaked it is (1 = Pierson-Moskowitz, 3.3 = the usual default)."),
    ("Scatter table", "Hours per year in each (Hs, Te) bin at a site. Annual energy = sum over bins of (mean power) x (hours)."),
    ("Capture width (irregular) [m]", "Absorbed energy divided by incident energy per metre of crest."),
]

ASSUMPTIONS = [
    "Long-crested waves from one direction (no directional spreading).",
    "No wave transformation: the Sipora sea states are ERA5 values at a deep-water node (736 m) and are applied "
    "unchanged at a device in the chosen depth h (no shoaling, refraction or breaking).",
    "The turbine setting cPTO is fixed within a sea state. 'Best fixed cPTO' is one value for the whole year; "
    "'retuned per sea state' changes it between sea states (an upper bound for slow control). Retuning per wave "
    "component is not possible in an irregular sea, so the per-frequency optimum of the Model tab is not used here.",
    "Linear, lossless, no turbine efficiency, no rated-power limit: the results are absorbed (pneumatic) power, "
    "not electricity.",
    "The Sipora table covers only the hours with waves from the thesis sector 191.25-213.75 deg (5,194 h in 2022, "
    "about 59% of the year). Annual energy here means energy in those hours.",
]

MODEL_WARNING = {
    "toy_constant": "Piston toy with constant zeta: its radiation damping does not fall at long periods the way real "
                    "radiation does (c ~ w^2 instead of w^3), so it overestimates power in long-period swell. "
                    "Use the frequency-dependent damping model for a physically scaled estimate.",
    "toy_fk": "Piston toy with frequency-dependent damping B(w): physically scaled at long periods, still a piston "
              "estimate (Froude-Krylov force, diffraction neglected).",
    "zheng": "Zheng et al. wall backend: ideal, perfectly reflecting, infinite wall. The wall roughly doubles the "
             "absorption relative to an isolated device; a real breakwater reflects less.",
}

COMPARISON_NOTE = (
    "Reference results for the Sipora 2022 in-sector hours (h = 10 m, inner radius 4 m, best fixed cPTO): toy with "
    "constant zeta 229 MWh, toy with B(w) 57 MWh, Zheng wall model 114 MWh. The wall model gives about twice the "
    "physically scaled isolated estimate, consistent with the wall-doubling result (the geometries differ, so this is "
    "an observation, not a proof)."
)
