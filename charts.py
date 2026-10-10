"""Interactive Altair charts for the app (hover tooltips, x zoom/pan, legend highlight). No streamlit import.

Numbers come from owc_views.curves / chamber_motion / zheng_views.curves / consistency; matplotlib stays only for export.
data_of(chart) gives the plotted table (for the "Show data" expanders).
"""
import altair as alt
import numpy as np
import pandas as pd

import owc_toy as o
import owc_views

SERIES = {False: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"], True: ["#3987e5", "#d95926", "#199e70", "#c98500"]}
INK = {False: "#52514e", True: "#c3c2b7"}
GRID = {False: "#e6e5e1", True: "#2a2a28"}
BAND_GREY = "#8a8984"
BAND_ORANGE = {False: "#eb6834", True: "#d95926"}
H = 300


def _style(chart, dark, title):
    ink = INK[dark]
    return (chart.properties(title=alt.TitleParams(title, anchor="start", color=ink, fontSize=13))
            .configure_axis(gridColor=GRID[dark], labelColor=ink, titleColor=ink, domainColor=ink, tickColor=ink)
            .configure_legend(labelColor=ink, titleColor=ink, orient="bottom", labelLimit=0)
            .configure_view(stroke=None))


def _runs(x, mask):
    """[(x_start, x_end)] for each contiguous True run of mask (extended to the neighbouring grid points)."""
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((float(x[max(i - 1, 0)]), float(x[min(j + 1, n - 1)])))
            i = j + 1
        else:
            i += 1
    return out


def bands_for(x, grey_mask=None, orange_mask=None, dark=False):
    b = []
    for mask, col, op in ((grey_mask, BAND_GREY, 0.15), (orange_mask, BAND_ORANGE[dark], 0.12)):
        if mask is not None and np.any(mask):
            b += [{"x0": a, "x1": c, "color": col, "opacity": op} for a, c in _runs(x, np.asarray(mask))]
    return b


def _line(x, series, *, xtitle, ytitle, title, dark=False, bands=(), vrules=(), hrules=(), points=(),
          notes=(), ydomain=None, xlog=False, ylog=False):
    """series: [(name, y array, dash or None)]. vrules: dict(x, label, dash). hrules: dict(y, label, dash).
    points: (x, y, label)."""
    x = np.asarray(x, float)
    names = [s[0] for s in series]
    wide = pd.DataFrame({"x": x, **{f"s{i}": np.asarray(s[1], float) for i, s in enumerate(series)}})
    long = pd.DataFrame({"x": np.tile(x, len(series)), "series": np.repeat(names, len(x)),
                         "y": np.concatenate([np.asarray(s[1], float) for s in series])})
    ink = INK[dark]
    xs = alt.Scale(type="log" if xlog else "linear", domain=[float(x.min()), float(x.max())], nice=False)
    ys = alt.Scale(type="log" if ylog else "linear", domain=ydomain or alt.Undefined) if (ydomain or ylog) else alt.Scale()
    X = alt.X("x:Q", title=xtitle, scale=xs)
    Y = alt.Y("y:Q", title=ytitle, scale=ys)
    tips = [alt.Tooltip(field="x", type="quantitative", title=xtitle, format=".4g")] + [
        alt.Tooltip(field=f"s{i}", type="quantitative", title=n, format=".3g") for i, n in enumerate(names)]

    zoom = alt.selection_interval(bind="scales", encodings=["x"])
    hover = alt.selection_point(name="hover", on="pointerover", nearest=True, fields=["x"], empty=False)
    color = alt.Color("series:N", scale=alt.Scale(domain=names, range=SERIES[dark][:len(names)]),
                      legend=alt.Legend(title=None) if len(names) > 1 else None)
    enc = dict(x=X, y=Y, color=color)
    if any(s[2] for s in series):
        enc["strokeDash"] = alt.StrokeDash("series:N", scale=alt.Scale(domain=names, range=[s[2] or [1, 0] for s in series]),
                                           legend=None)
    line = alt.Chart(long).mark_line(strokeWidth=2, clip=True).encode(**enc).add_params(zoom)
    if len(names) > 1:
        leg = alt.selection_point(fields=["series"], bind="legend")
        line = line.encode(opacity=alt.condition(leg, alt.value(1), alt.value(0.2))).add_params(leg)
    layers = []
    for b in bands:
        layers.append(alt.Chart(pd.DataFrame([b])).mark_rect(clip=True, opacity=b["opacity"], color=b["color"])
                      .encode(x=alt.X("x0:Q", scale=xs), x2="x1:Q"))
    layers.append(line)
    top = 4
    for r in vrules:
        d = pd.DataFrame({"x": [r["x"]], "label": [r["label"]]})
        layers.append(alt.Chart(d).mark_rule(color=ink, strokeWidth=1.2, strokeDash=r.get("dash") or [1, 0], clip=True)
                      .encode(x=alt.X("x:Q", scale=xs)))
        layers.append(alt.Chart(d).mark_text(align="left", baseline="top", dx=4, color=ink, fontSize=11, clip=True)
                      .encode(x=alt.X("x:Q", scale=xs), y=alt.value(top), text="label:N"))
        top += 14
    for r in hrules:
        d = pd.DataFrame({"y": [r["y"]], "label": [r["label"]], "x": [float(x.min())]})
        layers.append(alt.Chart(d).mark_rule(color=ink, strokeWidth=1.2, strokeDash=r.get("dash") or [1, 0], clip=True)
                      .encode(y=alt.Y("y:Q", scale=ys)))
        layers.append(alt.Chart(d).mark_text(align="left", baseline="bottom", dx=4, dy=-3, color=ink, fontSize=11)
                      .encode(x=alt.X("x:Q", scale=xs), y=alt.Y("y:Q", scale=ys), text="label:N"))
    for px, py, lab in points:
        d = pd.DataFrame({"x": [px], "y": [py], "label": [lab]})
        layers.append(alt.Chart(d).mark_point(filled=True, size=90, color=ink, clip=True)
                      .encode(x=alt.X("x:Q", scale=xs), y=alt.Y("y:Q", scale=ys),
                              tooltip=[alt.Tooltip("label:N", title=""), alt.Tooltip("x:Q", title=xtitle, format=".4g"),
                                       alt.Tooltip("y:Q", title=ytitle, format=".4g")]))
        layers.append(alt.Chart(d).mark_text(align="left", baseline="bottom", dx=7, dy=-5, color=ink, fontSize=11)
                      .encode(x=alt.X("x:Q", scale=xs), y=alt.Y("y:Q", scale=ys), text="label:N"))
    for i, n in enumerate(notes):
        layers.append(alt.Chart(pd.DataFrame({"t": [n]})).mark_text(align="left", baseline="bottom", dx=6, color=ink,
                      fontSize=11).encode(x=alt.value(0), y=alt.value(H - 6 - 14 * i), text="t:N"))
    # hover: transparent selectors, a vertical rule and markers on every series; the tooltip lists all values
    layers.append(alt.Chart(wide).mark_point(opacity=0, size=60).encode(x=alt.X("x:Q", scale=xs), tooltip=tips)
                  .add_params(hover))
    layers.append(alt.Chart(wide).mark_rule(color=ink, strokeWidth=1).encode(x=alt.X("x:Q", scale=xs), tooltip=tips)
                  .transform_filter(hover))
    layers.append(alt.Chart(long).mark_point(filled=True, size=70, clip=True).encode(x=X, y=Y, color=color)
                  .transform_filter(hover))
    chart = _style(alt.layer(*layers).properties(height=H), dark, title)
    return chart


def data_of(chart):
    """Plotted numbers as a DataFrame with the tooltip titles as column names."""
    sel = chart.layer[-3] if len(chart.layer) > 3 and chart.layer[-3].mark.opacity == 0 else chart.layer[2]
    df = sel.data.copy()
    if isinstance(sel.encoding.tooltip, list) and len(sel.encoding.tooltip) == len(df.columns):
        return df.rename(columns={t["field"]: t["title"] for t in sel.encoding.tooltip})
    return df[["arrow", "re", "im"]] if "arrow" in df else df


def _toy_marks(cur, state, dark):
    P = o.Params(**state["params"])
    bands = bands_for(cur["kh"], cur["valid_k_rin_gt_1"], cur["valid_kh_lt_0p5"], dark)
    v = [{"x": float(o.wavenumber(cur["w_nat"], P.h) * P.h), "label": "natural freq.", "dash": [2, 3]}]
    if cur["has_res"]:
        v.append({"x": float(o.wavenumber(cur["w_res"], P.h) * P.h), "label": "a + aPTO = 0"})
    v.append({"x": float(cur["op"]["kh"]), "label": f"selected T = {cur['op']['T']:.2f} s", "dash": [6, 3]})
    return bands, v


def coefficients(cur, state, dark=False):
    bands, v = _toy_marks(cur, state, dark)
    s = 1e3
    notes = [] if cur["has_res"] else ["No PTO resonance for these inputs (a result, not an error)"]
    return _line(cur["kh"], [("c", cur["c"] * s, None), ("a", cur["a"] * s, None), ("-aPTO", -cur["a_pto"] * s, None)],
                 xtitle="kh (wave number x depth)", ytitle="m^3/s/Pa (x1e-3)", title="(a) Radiation c, a and -aPTO",
                 dark=dark, bands=bands, vrules=v, notes=notes)


def eta(cur, state, dark=False):
    bands, v = _toy_marks(cur, state, dark)
    v = [r for r in v if r["label"].startswith("selected")]
    return _line(cur["kh"], [("cPTO optimal at every frequency (upper bound)", cur["eta_opt"], None),
                             (f"one fixed cPTO = {cur['c_pto_fixed_used']:.3g} m^3/s/Pa", cur["eta_fixed"], [6, 3])],
                 xtitle="kh", ytitle="capture width ratio eta = kP/Pin", title="(b) Capture width ratio",
                 dark=dark, bands=bands, vrules=v, ydomain=[0, 1.1])


def sweep(cur, state, dark=False):
    P = o.Params(**state["params"])
    c_sel = float(o.radiation_coefficients(cur["op"]["w"], P)[0])
    return _line(cur["sweep_c_pto"] / c_sel, [(f"T = {cur['op']['T']:.2f} s", cur["sweep_eta"], None)],
                 xtitle="cPTO / c (at the selected T)", ytitle="eta", title="(c) Why there is an optimal cPTO",
                 dark=dark, xlog=True, ydomain=[0, 1.1],
                 points=[(cur["sweep_c_pto_opt"] / c_sel, cur["sweep_eta_opt"], "optimum cPTO")])


def dispersion(state, cur, dark=False):
    P, op, T_cfg = o.Params(**state["params"]), cur["op"], owc_views.load_config()["T"]
    T = np.linspace(T_cfg["min"], T_cfg["max"], 300)
    return _line(T, [(f"h = {P.h:g} m", 2 * np.pi / o.wavenumber(2 * np.pi / T, P.h), None),
                     ("deep water", o.G * T**2 / (2 * np.pi), [6, 3])],
                 xtitle="wave period T [s]", ytitle="wavelength lambda [m]", title=f"Dispersion, h = {P.h:g} m",
                 dark=dark, points=[(op["T"], 2 * np.pi / op["k"], f"selected T = {op['T']:.2f} s")],
                 hrules=[{"y": 2 * np.pi * P.r_in, "label": "k r_in = 1 (above: piston idea OK)", "dash": [2, 3]}])


def phasor(m, dark=False):
    s = m["Qe_abs"]
    q_rad = complex(m["q_rad_re"], m["q_rad_im"]) / s
    q_pto = complex(m["q_pto_re"], m["q_pto_im"]) / s
    qe = complex(m["Qe_re"], m["Qe_im"]) / s
    p_dir = complex(m["p_re"], m["p_im"]) / m["p_abs"]
    phase = (m["p_deg"] - m["Qe_deg"] + 180) % 360 - 180
    phase = 0.0 if abs(phase) < 0.05 else phase
    arrows = [("radiated (c - i a) p", 0j, q_rad, q_rad),
              ("into air chamber (cPTO - i aPTO) p", q_rad, q_rad + q_pto, q_pto),
              ("Qe", 0j, qe, qe), ("p (direction only)", 0j, 0.6 * p_dir, 0.6 * p_dir)]
    names = [a[0] for a in arrows]
    ink = INK[dark]
    rng = [SERIES[dark][1], SERIES[dark][0], ink, "#8a8984"]
    df = pd.DataFrame([{"arrow": n, "x": a.real, "y": a.imag, "x2": b.real, "y2": b.imag, "re": v.real, "im": v.imag,
                        "angle": float(np.degrees(np.arctan2((b - a).real, (b - a).imag)))} for n, a, b, v in arrows])
    lim = float(1.25 * max(abs(v) for _, _, b, _ in arrows for v in (b.real, b.imag)) + 0.05)
    sc = alt.Scale(domain=[-lim, lim], nice=False)
    col = alt.Color("arrow:N", scale=alt.Scale(domain=names, range=rng), legend=alt.Legend(title=None))
    tips = [alt.Tooltip("arrow:N", title=""), alt.Tooltip("re:Q", title="real / |Qe|", format=".3f"),
            alt.Tooltip("im:Q", title="imaginary / |Qe|", format=".3f")]
    base = alt.Chart(df)
    seg = base.mark_rule(strokeWidth=2.5, clip=True).encode(
        x=alt.X("x:Q", scale=sc, title="real part / |Qe|"), x2="x2:Q",
        y=alt.Y("y:Q", scale=sc, title="imaginary part / |Qe|"), y2="y2:Q", color=col, tooltip=tips,
        strokeDash=alt.StrokeDash("arrow:N", scale=alt.Scale(domain=names, range=[[1, 0]] * 3 + [[6, 4]]), legend=None))
    head = base.mark_point(shape="triangle", filled=True, size=130, clip=True).encode(
        x=alt.X("x2:Q", scale=sc), y=alt.Y("y2:Q", scale=sc), angle=alt.Angle("angle:Q", scale=None),
        color=col, tooltip=tips)
    axes = alt.Chart(pd.DataFrame({"z": [0]}))
    zl = [axes.mark_rule(color="#8a8984", strokeWidth=0.8).encode(x=alt.datum(0)),
          axes.mark_rule(color="#8a8984", strokeWidth=0.8).encode(y=alt.datum(0))]
    chart = alt.layer(*zl, seg, head).properties(width=340, height=340)
    chart = _style(chart, dark, f"Eq. 2 as arrows, T = {m['T']:.2f} s, p vs Qe: {phase:.1f} deg")
    return chart


def zheng_main(zcur, dark=False):
    kh = zcur["kh"]
    v = [{"x": r["kh"], "label": "a + aPTO = 0"} for r in zcur["resonances"]]
    bands = []
    for k in zcur["validity_messages"]:
        bands += bands_for(kh, None, zcur["valid_" + k], dark)
    kw = dict(dark=dark, bands=bands, vrules=v, xtitle="kh")
    return [
        _line(kh, [("Qbar", zcur["Qbar"], None)], ytitle="Qbar_e", title="(a) Excitation flow", **kw),
        _line(kh, [("cbar", zcur["cbar"], None), ("abar", zcur["abar"], None), ("-aPTObar", -zcur["aPTObar"], None)],
              ytitle="dimensionless", title="(b) Radiation coefficients", **kw),
        _line(kh, [("cPTObar optimal", zcur["cPTObar"], None)], ytitle="cPTObar optimal",
              title="(c) Optimal turbine conductance", **kw),
        _line(kh, [("eta (optimal cPTO)", zcur["eta_opt"], None)], ytitle="eta (optimal cPTO)",
              title="(d) Capture width ratio",
              hrules=[{"y": 1, "label": "isolated-absorber limit (eta = 1)", "dash": [2, 3]},
                      {"y": 2, "label": "2 (beta-averaged wall limit)", "dash": [6, 3]}], **kw),
    ]


def zheng_consistency(cons, dark=False):
    kh = cons["kh"]
    a = _line(kh, [("DM", cons["c_DM"], None), ("FFC", cons["c_FFC"], [6, 3]), ("HR", cons["c_HR"], [2, 2])],
              xtitle="kh", ytitle="c [m^3/s/Pa]", title="(a) c by three methods (rung 1)", dark=dark)
    b = _line(kh, [("|FFC - DM| / DM", np.maximum(cons["rel_FFC"], 1e-16), None),
                   ("|HR - DM| / DM", np.maximum(cons["rel_HR"], 1e-16), [6, 3])],
              xtitle="kh", ytitle="relative difference", title="(b) Relative differences (rung 1)", dark=dark, ylog=True)
    return [a, b]


def thin_wall_validation(kh, scaled, ref, dark=False):
    """Indirect rung 3: our thin-wall c, a (scaled w rho / R, given in `scaled` by "c"/"a") with the
    reference points read off Zheng et al. 2019 JFM Fig. 4."""
    out = []
    for q, name, title in (("c", "c w rho / R", "(a) Radiation conductance, thin wall"),
                           ("a", "a w rho / R", "(b) Radiation susceptance, thin wall")):
        pts = [(p["kh"], p["value"], "Martins-Rivas & Mei: " + p["label"]) for p in ref["points"] if p["q"] == q]
        out.append(_line(kh, [(f"{name}, this solver", scaled[q], None)], xtitle="kh", ytitle=name, title=title,
                         dark=dark, points=pts))
    return out


def long_wave(rows, dark=False):
    """L1: relative error of the solver against the exact long-wave limit, log-log, with a kh^2 guide."""
    kh = np.array([r["kh"] for r in rows])
    eq = np.abs(np.array([r["Qe_ratio"] for r in rows]) - 1)
    ec = np.abs(np.array([r["c_ratio"] for r in rows]) - 1)
    guide = ec[-1] * (kh / kh[-1]) ** 2
    return _line(kh, [("|Qe| error = |solver/limit - 1|", eq, None), ("c error", ec, None),
                      ("slope 2 guide (error ~ kh^2)", guide, [2, 3])],
                 xtitle="kh", ytitle="relative error vs exact limit",
                 title="Long-wave limit at a reflecting wall: error falls like (kh)^2", dark=dark, xlog=True, ylog=True)


# ------------------------------------------------------------------ site & annual energy tab
HEAT = {False: ["#cfe0f6", "#1c4f8f"], True: ["#1a2b40", "#7fb2ef"]}


def site_line(w, y, ytitle, title, dark=False):
    """y(w) drawn against the period T = 2 pi / w [s], 2-25 s (never dual axis)."""
    T = 2 * np.pi / np.asarray(w, float)
    m = (T >= 2) & (T <= 25)
    i = np.argsort(T[m])
    return _line(T[m][i], [(ytitle, np.asarray(y, float)[m][i], None)], xtitle="wave period T [s]", ytitle=ytitle,
                 title=title, dark=dark)


def site_heatmap(df, col, title, dark=False):
    """df: te0, te1, hs0, hs1, te, hs, hours and col; rect marks for the rows with hours > 0."""
    d = df[df["hours"] > 0]
    ink = INK[dark]
    sc = alt.Scale(range=HEAT[dark], interpolate="lab")
    tips = [alt.Tooltip("te:Q", title="Te [s]"), alt.Tooltip("hs:Q", title="Hs [m]"),
            alt.Tooltip("hours:Q", title="hours", format=".4g"), alt.Tooltip(f"{col}:Q", title=col, format=".4g")]
    ch = alt.Chart(d).mark_rect().encode(
        x=alt.X("te0:Q", title="Te bin centre [s]", scale=alt.Scale(zero=False, nice=False)), x2="te1:Q",
        y=alt.Y("hs0:Q", title="Hs bin centre [m]", scale=alt.Scale(zero=False, nice=False)), y2="hs1:Q",
        color=alt.Color(f"{col}:Q", scale=sc, legend=alt.Legend(title=col, orient="right")), tooltip=tips)
    return _style(ch.properties(height=H), dark, title).configure_legend(labelColor=ink, titleColor=ink)
