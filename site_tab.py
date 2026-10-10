"""'Site & annual energy' tab: irregular-wave power and annual energy (physics in owc_sea, text in site_text)."""
import hashlib
import json

import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import minimize_scalar

import charts
import learn
import owc_sea
import owc_toy
import site_text
import zheng_views

W_TOY = np.linspace(0.2, 4.0, 1500)


def _model(state, zstate):
    """(warning key, w, coeffs, a_pto, h, model identity for the cache) or None if the Zheng model is not cached."""
    if zstate is None:
        p = owc_toy.Params(**state["params"])
        coeffs, a_pto = owc_sea.toy_coeffs(W_TOY, p)
        key = "toy_constant" if state["params"]["damping"] == "constant" else "toy_fk"
        return key, W_TOY, coeffs, a_pto, state["params"]["h"], ["toy", state["params"]]
    if not zheng_views.is_cached(zstate):
        st.warning("Compute the wall model on the Model tab first (it is cached afterwards).")
        return None
    cur, p = zheng_views.curves(zstate), zheng_views.zheng_params(zstate)
    w = cur["w"]
    coeffs = {"c": cur["c"], "a": cur["a"], "qe_unit": np.abs(cur["Qe"]) / p.A}
    return "zheng", w, coeffs, owc_toy.a_pto(w, p), p.h, ["zheng", zstate]


def _best_cpto(w, coeffs, a_pto, s):
    c, a, q = coeffs["c"], coeffs["a"], coeffs["qe_unit"]
    r = minimize_scalar(lambda lc: -owc_sea.absorbed_power(w, s, owc_sea.unit_power(c, a, q, a_pto, 10**lc)),
                        bounds=(-6, 1), method="bounded", options={"xatol": 1e-4})
    return 10**r.x


def _single(state, w, coeffs, a_pto, h, dark):
    st.subheader("Single sea state")
    c1, c2, c3 = st.columns(3)
    hs = c1.slider("Hm0 [m]", 0.25, 4.0, 1.25, 0.05, key="site_hs")
    te = c2.slider("Te [s]", 4.0, 20.0, 12.25, 0.25, key="site_te")
    gamma = c3.slider("gamma", 1.0, 7.0, 3.3, 0.1, key="site_gamma")
    best, fixed = "best fixed cPTO for this sea state", "cPTO from the sidebar (fixed mode)"
    mode = st.radio("Turbine", [best, fixed], horizontal=True, key="site_turbine")
    S = owc_sea.spectrum(w, hs, te, gamma)
    J = owc_sea.incident_power(w, S, h)
    if mode == fixed and state.get("c_pto_fixed") is not None:
        cp = state["c_pto_fixed"]
    else:  # also the fallback when the sidebar is not in fixed mode (first option)
        cp = _best_cpto(w, coeffs, a_pto, S)
    p1 = owc_sea.unit_power(coeffs["c"], coeffs["a"], coeffs["qe_unit"], a_pto, cp)
    P = owc_sea.absorbed_power(w, S, p1)
    frac = owc_sea.captured_fraction(w, S, hs)
    if frac < 0.99:
        st.warning(f"{100 * (1 - frac):.1f}% of this sea state's energy lies outside the model's frequency grid.")
    learn.show_chart(charts.site_line(w, S, "S(w) [m^2 s/rad]", "(a) Wave spectrum", dark))
    learn.show_chart(charts.site_line(w, 2 * S * p1, "2 S(w) P1(w) [W/(rad/s)]", "(b) Absorbed power density", dark))
    m = st.columns(4)
    m[0].metric("J [kW/m]", f"{J / 1e3:.4g}")
    m[1].metric("P [kW]", f"{P / 1e3:.4g}")
    m[2].metric("Capture width [m]", f"{P / J:.4g}")
    m[3].metric("cPTO used [m^3/s/Pa]", f"{cp:.4g}")


def _annual(w, coeffs, a_pto, h, ident, dark):
    st.subheader("Sipora 2022 (thesis sector)")
    gamma = st.session_state.get("site_gamma", 3.3)
    sc = owc_sea.load_scatter()
    key = hashlib.sha1(json.dumps([ident, gamma], sort_keys=True, default=str).encode()).hexdigest()
    cache = st.session_state.setdefault("site_aep_cache", {})
    if st.button("Compute annual energy", key="site_aep") and key not in cache:
        with st.spinner("Integrating over the scatter table (a few seconds)..."):
            cache[key] = owc_sea.site_energy(w, coeffs, a_pto, sc, h, gamma=gamma)
    r = cache.get(key)
    if r is None:
        st.caption("Press the button; nothing is computed until then.")
        return
    m = st.columns(3)
    m[0].metric("Annual energy, best fixed cPTO [MWh]", f"{r['E_fixed_MWh']:.4g}")
    m[1].metric("Annual energy, cPTO retuned per sea state [MWh]", f"{r['E_tuned_MWh']:.4g}")
    m[2].metric("Incident energy per metre of crest [MWh/m]", f"{r['E_incident_MWh_per_m']:.4g}")
    m = st.columns(3)
    m[0].metric("Capture width [m]", f"{r['E_fixed_MWh'] / r['E_incident_MWh_per_m']:.4g}")
    m[1].metric("Hours covered", f"{r['total_hours']:.0f}")
    m[2].metric("Best fixed cPTO [m^3/s/Pa]", f"{r['c_pto']:.4g}")

    rows = sc["rows"]
    df = pd.DataFrame({
        "hs0": [float(x["hs_lower_m"]) for x in rows], "hs1": [float(x["hs_upper_m"]) for x in rows],
        "te0": [float(x["te_lower_s"]) for x in rows], "te1": [float(x["te_upper_s"]) for x in rows],
        "hs": sc["hs"], "te": sc["te"], "hours": r["hours"], "J_kW_per_m": r["J"] / 1e3,
        "P_fixed_kW": r["P_fixed"] / 1e3, "P_tuned_kW": r["P_tuned"] / 1e3,
        "E_fixed_MWh": r["P_fixed"] * r["hours"] / 1e6})
    for col, title in (("hours", "Hours per bin"), ("P_fixed_kW", "Mean absorbed power per bin, fixed cPTO [kW]"),
                       ("E_fixed_MWh", "Energy per bin, fixed cPTO [MWh]")):
        st.altair_chart(charts.site_heatmap(df, col, title, dark), width="stretch")
        with st.expander("Show data"):
            st.dataframe(df[df["hours"] > 0][list(dict.fromkeys(["hs", "te", "hours", col]))], width="stretch")
    st.caption(site_text.COMPARISON_NOTE)
    st.download_button("Download results (CSV)", df[["hs", "te", "hours", "J_kW_per_m", "P_fixed_kW", "P_tuned_kW",
                                                     "E_fixed_MWh"]].to_csv(index=False), "site_results.csv", "text/csv")


def render_site(state, zstate, cfg):
    st.header(site_text.TITLE)
    st.markdown(site_text.INTRO)
    with st.expander("Definitions"):
        for term, meaning in site_text.DEFINITIONS:
            st.markdown(f"**{term}**: {meaning}")
    mod = _model(state, zstate)
    if mod is None:
        return
    key, w, coeffs, a_pto, h, ident = mod
    st.warning(site_text.MODEL_WARNING[key])
    st.info("\n".join(f"- {a}" for a in site_text.ASSUMPTIONS))
    dark = learn.is_dark()
    _single(state, w, coeffs, a_pto, h, dark)
    _annual(w, coeffs, a_pto, h, ident, dark)
