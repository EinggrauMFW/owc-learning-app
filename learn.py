"""Learn and Glossary tabs: step-by-step pictures of the toy OWC. UI module (imports streamlit).

Text comes from learn_text.py; the numbers come from owc_views (chamber_motion, curves).
"""
import json

import streamlit as st

import charts
import owc_views
from learn_text import GLOSSARY, STEPS

CAPTION = ("Drawing: incident wave only (scattered and radiated waves are not drawn). The timing of Qe uses "
           "the small-chamber limit; it is an assumption of the drawing, not an output of the toy. The wall "
           "draft is drawn schematically; it is not a model input.")


def is_dark():
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


def show_chart(chart, data=True, container=True):
    st.altair_chart(chart, width="stretch" if container else "content")
    if data:
        with st.expander("Show data"):
            st.dataframe(charts.data_of(chart), width="stretch")


def render_learn(state, cur):
    names = [f"{s['id']}. {s['title']}" for s in STEPS]
    choice = st.radio("Step", names, horizontal=True, key="learn_step")
    step = STEPS[names.index(choice)]
    st.progress(step["id"] / len(STEPS))
    st.subheader(step["title"])
    vis = step["visual"]
    if vis == "animation":  # full width, so the drawing is big enough to read
        m = owc_views.chamber_motion(state)
        st.iframe(svg_animation_html(m, owc_views.load_config()), height=520)  # our own generated HTML
    left, right = st.columns([1, 1.3])
    with left:
        for term, meaning in step["definitions"]:
            st.markdown(f"**{term}**: {meaning}")
        st.markdown(step["body"])
    with right:
        if vis == "animation":
            st.table([
                {"quantity": "|z|", "value": f"{m['z_abs']:.4g}", "unit": "m"},
                {"quantity": "phase of z relative to the outside wave crest at the chamber centre",
                 "value": f"{m['z_deg']:.1f}", "unit": "deg"},
                {"quantity": "|p|", "value": f"{m['p_abs']:.4g}", "unit": "Pa"},
                {"quantity": "|turbine flow|", "value": f"{m['q_turb_abs']:.4g}", "unit": "m^3/s"},
                {"quantity": "|air-compression flow|", "value": f"{m['q_air_abs']:.4g}", "unit": "m^3/s"},
                {"quantity": "|Qe|", "value": f"{m['Qe_abs']:.4g}", "unit": "m^3/s"},
            ])
            st.caption(CAPTION)
        else:
            dark = is_dark()
            if vis == "dispersion":
                show_chart(charts.dispersion(state, cur, dark))
            elif vis == "phasor":
                show_chart(charts.phasor(owc_views.chamber_motion(state), dark), container=False)  # equal x/y scales
            else:
                show_chart(getattr(charts, vis)(cur, state, dark))
    st.info("Look at: " + step["look"])
    st.success("Try: " + step["try"])


def render_glossary():
    q = st.text_input("Filter", key="gloss_filter").lower()
    st.table([{"symbol": s, "meaning": mean, "unit": u} for s, mean, u in GLOSSARY
              if q in s.lower() or q in mean.lower()])


_HTML = """<div style="background:#f4f6f8;border-radius:10px;font-family:sans-serif;color:#222;max-width:900px">
<svg id="s" viewBox="0 0 760 400" style="display:block;width:100%;height:auto"></svg>
<div style="padding:4px 12px 8px"><button id="pp" style="padding:3px 12px">Pause</button>
<select id="sp" style="padding:3px"><option value="1">1x real time</option><option value="0.5">0.5x</option>
<option value="0.25">0.25x</option></select></div></div>
<script>
const D = __DATA__;
const L = 10, R = 750, T0 = 62, B0 = 350, r = D.r_in, wt_ = 0.15 * r;
const xmin = -Math.max(1.5 * D.wavelength, 5 * r), xmax = Math.max(0.6 * D.wavelength, 3 * r);
const ymin = -D.h, ymax = D.H_air + 0.4 * D.h;
const sx = (R - L) / (xmax - xmin), sy = (B0 - T0) / (ymax - ymin);
const X = x => L + (x - xmin) * sx, Y = y => B0 - (y - ymin) * sy;
const WATER = "#9cc9f0", WALL = "#2f3640", g = 0.18 * r, roofY = Y(D.H_air);
const bx = X(xmin + 0.1 * D.wavelength), bx2 = X(xmin + 1.1 * D.wavelength);
const rect = (x, y, w, h, f, extra) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${f}" ${extra || ""}/>`;
const br = (x1, x2, y, label, ty) => `<path d="M${x1} ${y - 5}V${y}H${x2}V${y - 5}" fill="none" stroke="#444"/>` +
  `<text x="${(x1 + x2) / 2}" y="${ty}" text-anchor="middle" font-size="12" fill="#222">${label}</text>`;
document.getElementById("s").innerHTML =
  rect(0, 0, 760, 400, "#f4f6f8", 'rx="10"') + rect(L, B0, R - L, 5, "#d8c08a") +
  '<polygon id="wl" fill="' + WATER + '"/><polygon id="wr" fill="' + WATER + '"/>' +
  rect(X(-r), 0, 2 * r * sx, 0, WATER, 'id="wi"') + rect(X(-r), 0, 2 * r * sx, 0, "#e4572e", 'id="air"') +
  rect(X(-r - wt_), roofY, wt_ * sx, Y(-0.4 * D.h) - roofY, WALL) + rect(X(r), roofY, wt_ * sx, Y(-0.4 * D.h) - roofY, WALL) +
  rect(X(-r - wt_), roofY - 5, (r + wt_ - g) * sx, 5, WALL) + rect(X(g), roofY - 5, (r + wt_ - g) * sx, 5, WALL) +
  rect(X(-g), roofY - 12, 2 * g * sx, 12, "#7a8594") +
  `<circle cx="${X(0)}" cy="${roofY - 6}" r="5" fill="#f4f6f8" stroke="${WALL}"/>` +
  '<path id="arr" stroke="#222" stroke-width="3" fill="none"/><polygon id="arh" fill="#222"/>' +
  '<text id="arl" font-size="11" fill="#222"/>' +
  '<text id="ro" x="16" y="22" font-size="12" fill="#222"></text>' +
  `<text x="744" y="22" font-size="11" text-anchor="end" fill="#555">vertical scale x${(sy / sx).toFixed(1)}</text>` +
  br(bx, bx2, 366, "lambda = " + D.wavelength.toFixed(1) + " m", 381) +
  br(X(-r), X(r), 366, "2 r_in = " + (2 * r).toFixed(1) + " m", 395);
const $ = id => document.getElementById(id);
const xl = [], xr = [];
for (let i = 0; i <= 160; i++) xl.push(xmin + (-r - xmin) * i / 160);
for (let i = 0; i <= 120; i++) xr.push(r + (xmax - r) * i / 120);
const poly = (xs, c) => xs.map(x => X(x) + "," + Y(D.A * Math.cos(D.k * x - c))).join(" ") +
  ` ${X(xs[xs.length - 1])},${B0} ${X(xs[0])},${B0}`;
function draw(t) {
  const c = D.w * t, cs = Math.cos(c), sn = Math.sin(c);
  $("wl").setAttribute("points", poly(xl, c)); $("wr").setAttribute("points", poly(xr, c));
  const z = D.z_re * cs + D.z_im * sn, p = D.p_re * cs + D.p_im * sn, q = D.q_turb_re * cs + D.q_turb_im * sn;
  $("wi").setAttribute("y", Y(z)); $("wi").setAttribute("height", B0 - Y(z));
  $("air").setAttribute("y", roofY); $("air").setAttribute("height", Math.max(0, Y(z) - roofY));
  $("air").setAttribute("fill", p > 0 ? "#e4572e" : "#2a78d6");
  $("air").setAttribute("fill-opacity", 0.15 + 0.55 * Math.min(1, Math.abs(p) / D.p_abs));
  const len = 50 * Math.min(1, Math.abs(q) / D.q_turb_abs), d = q > 0 ? -1 : 1, yc = roofY - 38, xc = X(0);
  const tip = yc + d * len / 2, h = Math.min(9, len);
  $("arr").setAttribute("d", `M${xc} ${yc - d * len / 2}V${tip - d * h}`);
  $("arh").setAttribute("points", `${xc - 6},${tip - d * h} ${xc + 6},${tip - d * h} ${xc},${tip}`);
  $("arl").setAttribute("x", xc + 12); $("arl").setAttribute("y", yc + 4); $("arl").textContent = q > 0 ? "air out" : "air in";
  $("ro").innerHTML = `<tspan x="16" dy="0">t/T = ${(t / D.T % 1).toFixed(2)}   outside eta(0) = ${(D.A * Math.cos(-c)).toFixed(2)} m   inner z = ${z.toFixed(2)} m</tspan>` +
    `<tspan x="16" dy="16">p = ${(p / 1000).toPrecision(3)} kPa   turbine flow = ${q.toPrecision(3)} m^3/s (positive = out)</tspan>`;
}
let t = 0, playing = true, last = null;
$("pp").onclick = () => { playing = !playing; $("pp").textContent = playing ? "Pause" : "Play"; };
function loop(ts) {
  if (playing && last !== null) t += (ts - last) / 1000 * parseFloat($("sp").value);
  last = playing ? ts : null;
  draw(t); requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
</script>"""


def svg_animation_html(m, cfg):
    """Self-contained HTML (inline SVG + JS) of the chamber over one wave; m = owc_views.chamber_motion(state)."""
    return _HTML.replace("__DATA__", json.dumps(m))


def render_physics_checks(state, op):
    """VERIFICATION.md plus a live time-domain check at the operating point chosen in the sidebar."""
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "verification"))
    import verify_toy

    st.subheader("Check this operating point by time integration")
    st.caption("Integrates the column and air-chamber ODEs (no frequency-domain code) for 80 wave periods "
               "and compares the mean turbine power with the app's value.")
    if state["params"].get("damping", "constant") != "constant":
        st.info("Not available with the frequency-dependent damping model: a damping that changes with frequency has "
                "no simple time-domain ODE (it needs a memory/convolution term, Cummins' equation). Switch the damping "
                "model to 'constant zeta' to run this check.")
    elif st.button("Run time-domain check", key="phys_run"):
        P = owc_views.o.Params(**state["params"])
        P_t, p_amp, e_res = verify_toy.n2_time_domain(op["w"], op["c_pto"], P)
        P_f = op["P_kW"] * 1e3
        st.table([
            {"quantity": "mean turbine power, time domain", "value": f"{P_t / 1e3:.6g}", "unit": "kW"},
            {"quantity": "mean turbine power, frequency domain (app)", "value": f"{P_f / 1e3:.6g}", "unit": "kW"},
            {"quantity": "relative difference", "value": f"{abs(P_t - P_f) / P_f:.1e}", "unit": "dimensionless"},
            {"quantity": "|p| time domain / app", "value": f"{p_amp:.5g} / {op['p_abs_Pa']:.5g}", "unit": "Pa"},
            {"quantity": "energy residual (wave work - radiated - absorbed) / wave work",
             "value": f"{e_res:.1e}", "unit": "dimensionless"},
        ])
    st.markdown((root / "VERIFICATION.md").read_text(encoding="utf-8"))
    st.divider()
    st.markdown((root / "LITERATURE.md").read_text(encoding="utf-8"))


def render_zheng_validation(cfg):
    """Validation of the Zheng wall backend against results that do not come from its own code."""
    import json
    import sys
    from pathlib import Path

    import numpy as np
    import zheng_views

    root = Path(__file__).resolve().parent
    dark = is_dark()
    st.header("Validation of the Zheng et al. (2019) wall backend")

    st.subheader("1. Long-wave limit at a reflecting wall (independent physics)")
    st.caption("For kR -> 0 the chamber surface follows the standing wave (2A at the wall), so |Qe| -> 2 w A pi Ri^2 "
               "and, by the Haskind relation, c -> pi^2 w^3 Ri^4 Z0(0)^2 / (2 rho g^2 h). The solver must tend to 1 on "
               "both ratios; the error should fall like (kR)^2. Default geometry.")
    sys.path.insert(0, str(root / "verification"))
    import validate_limits
    rows = validate_limits.l1_long_wave()
    show_chart(charts.long_wave(rows, dark))

    st.subheader("2. Thin-wall OWC against Martins-Rivas & Mei (2009a), indirect rung 3")
    ref = json.loads((root / "docs" / "rungs" / "rung3_reference.json").read_text(encoding="utf-8"))
    st.caption(ref["source"] + " Case: R/h = 0.5, Ri/h = 0.49, d/h = 0.2, M = 12, L = 20. Points = reference, "
               "line = this solver; hover for values.")
    zs = zheng_views.default_zstate(cfg)
    zs["params"].update({"R_over_h": 0.5, "wall_over_h": 0.01, "d_over_h": 0.2, "beta_deg": 90, "M": 12, "L": 20})
    zs["grid"]["n"] = 400  # the sloshing spike is only about 0.05 wide in kh
    if not zheng_views.is_cached(zs) and not st.button("Compute the thin-wall case (400 frequencies, about 1-2 min; "
                                                       "cached afterwards)", key="z_val_compute"):
        st.warning("Not computed yet. Press the button; nothing is solved until then.")
        return
    bar = st.progress(0.0)
    zcur = zheng_views.curves(zs, progress=lambda i, n: bar.progress(i / n))
    bar.empty()
    p = zheng_views.zheng_params(zs)
    s = zcur["w"] * p.rho / p.R
    scaled = {"c": zcur["c"] * s, "a": zcur["a"] * s}
    for ch in charts.thin_wall_validation(zcur["kh"], scaled, ref, dark):
        show_chart(ch)
    def nearest_extremum(q):
        """Our matching peak/trough within +-0.15 in kh (features can shift slightly), else the value at kh."""
        y, kh = scaled[q["q"]], zcur["kh"]
        win = np.abs(kh - q["kh"]) <= 0.15
        if "minimum" in q["label"]:
            i = np.flatnonzero(win)[np.argmin(y[win])]
        elif any(w in q["label"] for w in ("peak", "spike", "maximum")):
            i = np.flatnonzero(win)[np.argmax(y[win])]
        else:
            return "-", f"{np.interp(q['kh'], kh, y):.2f}"
        return f"{kh[i]:.2f}", f"{y[i]:.2f}"

    rows = []
    for q in ref["points"]:
        k_ext, v_ext = nearest_extremum(q)
        rows.append({"feature": q["label"], "reference kh": f"{q['kh']:.2f}",
                     "reference value (read off)": f"{q['value']:.2f}",
                     "this solver at the same kh": f"{np.interp(q['kh'], zcur['kh'], scaled[q['q']]):.2f}",
                     "this solver's matching extremum": f"{v_ext} at kh {k_ext}" if k_ext != "-" else v_ext})
    st.table(rows)
    st.caption("Main (pumping) mode: agreement within the read-off error. Sloshing spike near kh 4.1: this solver "
               "follows Zheng's own line and is 0.4-0.8 higher and about 0.07 further in kh than the circles. "
               "Likely causes: finite wall thickness (0.49 vs 0.5), circle sampling of a peak only about 0.05 wide, "
               "and slow convergence near this mode. This is a reading, not a proof. Details: docs/rungs/rung3_indirect.md.")
