"""Streamlit front end for the toy OWC model. Run with:  streamlit run app.py

All defaults and ranges come from config/defaults.json (owc_views.load_config).
"""
import json
import os

# ponytail: the BLAS default oversubscribed this machine (0.55 s vs 0.19 s per Zheng frequency at 4 threads).
# Must be set before numpy loads; override by setting OPENBLAS_NUM_THREADS yourself.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

import numpy as np
import streamlit as st

import charts
import owc_toy as o
import owc_views
import learn
import run_demo
import site_tab
import zheng_text
import zheng_views

cfg = owc_views.load_config()
OPTIMAL = "optimal at every frequency"
FIXED = "fixed"
SANITY_TEXT = (
    "For kh large (deep water, kh > about 3) Pin approaches rho g^2 A^2 T / (8 pi). A regular wave of "
    "height H = 2A carries twice the power of an irregular sea with Hs = 2A and Te = T, because an "
    "irregular sea of significant wave height Hs has the energy of a regular wave of height Hs / sqrt(2); "
    "so the regular-wave value is about 2 x 0.49 Hs^2 Te."
)


def _set_zeta(which):
    """Callback: runs before the widgets are created, so the zeta slider can be set here."""
    if which == "toy":
        st.session_state["p_zeta"] = float(cfg["params"]["zeta"]["default"])
        st.session_state["zeta_note"] = "zeta = toy default (regression anchors apply)."
        st.session_state["zeta_set"] = st.session_state["p_zeta"]
        return
    cur_p = {n: float(st.session_state.get("p_" + n, cfg["params"][n]["default"])) for n in cfg["params"]}
    z, w = o.zeta_froude_krylov(o.Params(**cur_p))
    zc = cfg["params"]["zeta"]
    st.session_state["p_zeta"] = float(min(max(round(z, 2), zc["min"]), zc["max"]))
    st.session_state["zeta_note"] = (f"zeta = {z:.3f} from Froude-Krylov + Haskind at w = {w:.3f} rad/s "
                                     f"(natural frequency, T = {2 * np.pi / w:.2f} s); regression anchors do not apply. "
                                     "With this damping the PTO resonance may disappear: see the Model tab.")
    st.session_state["zeta_set"] = st.session_state["p_zeta"]


def _restore():
    """Callback: runs before the widgets are created, so session values can be set here."""
    up = st.session_state.get("upload")
    if up is None:
        return
    saved = json.loads(up.getvalue())["state"]
    for name in cfg["params"]:
        if name in saved["params"]:
            st.session_state["p_" + name] = float(saved["params"][name])
    st.session_state["T"] = float(saved["T"])
    st.session_state["p_damping"] = saved["params"].get("damping", "constant")
    st.session_state["c_pto_mode_label"] = FIXED if saved["c_pto_mode"] == "fixed" else OPTIMAL
    if saved["c_pto_fixed"] is not None:
        st.session_state["log_c_pto"] = float(np.log10(saved["c_pto_fixed"]))
    if saved["backend"] in owc_views.BACKENDS:
        st.session_state["backend"] = saved["backend"]


ZCFG = cfg["zheng"]
V0_LABELS = {"R": "pi R^2 h (paper)", "Ri": "pi Ri^2 h"}
LEARN_INFO = "Learn and Exercises use the piston toy model; switch the backend to 'piston (toy)'."


def zheng_sidebar():
    zs = zheng_views.default_zstate(cfg)
    for name, item in ZCFG["params"].items():
        isint = isinstance(item["default"], int)
        cast = int if isint else float
        zs["params"][name] = st.slider(f"{item['label']} [{item['unit']}]", cast(item["min"]), cast(item["max"]),
                                       cast(item["default"]), cast(item["step"]), help=item["tip"], key="z_" + name)
    opts = ZCFG["V0_uses"]["options"]
    zs["V0_uses"] = st.radio("Air volume V0", opts, format_func=V0_LABELS.get, key="z_V0")
    g = ZCFG["grid"]
    zs["grid"]["n"] = int(st.number_input("kh points", int(g["n_min"]), int(g["n_max"]), int(g["n"]), 1, key="z_n"))
    return zs


def render_zheng(state, zs):
    st.header(zheng_text.TITLE)
    for note in zheng_text.NOTES:
        st.info(note)
    st.caption(zheng_text.ACCURACY)
    st.caption(zheng_text.V0_SWITCH)
    n = zs["grid"]["n"]
    if not zheng_views.is_cached(zs) and not st.button(
            f"Compute {n} frequencies (roughly 0.2-0.6 s each; cached on disk afterwards)", key="z_compute"):
        st.warning("These inputs have not been computed yet. Press Compute; nothing is solved until then.")
        return
    bar = st.progress(0.0)
    zcur = zheng_views.curves(zs, progress=lambda i, n: bar.progress(i / n))
    bar.empty()
    dark = learn.is_dark()
    mains = charts.zheng_main(zcur, dark)
    for row in (mains[:2], mains[2:]):
        for col, ch in zip(st.columns(2), row):
            with col:
                learn.show_chart(ch)
    tail = "; cached" if zcur["cached"] else ""
    st.caption(f"solved {zcur['n']} frequencies in {zcur['solve_time_s']:.3g} s, {zcur['per_freq_s']:.3g} s each{tail}")
    st.subheader("PTO resonances (a + aPTO = 0)")
    if zcur["resonances"]:
        st.table([{"kh": f"{r['kh']:.4g}", "T [s]": f"{r['T_s']:.4g}", "eta (optimal cPTO)": f"{r['eta']:.4g}"}
                  for r in zcur["resonances"]])
    else:
        st.write("No PTO resonance in the kh range (a result, not an error).")
    for msg in zcur["validity_messages"].values():
        st.caption(msg)

    st.subheader("Consistency check (rung 1)")
    if st.button("Compute consistency check", key="z_cons_btn"):
        cb = st.progress(0.0)
        cons = zheng_views.consistency(zs, progress=lambda i, n: cb.progress(i / n))
        cb.empty()
        for col, ch in zip(st.columns(2), charts.zheng_consistency(cons, dark)):
            with col:
                learn.show_chart(ch)
        st.caption(f"{len(cons['kh'])} kh points, {cons['solve_time_s']:.3g} s" + ("; cached" if cons["cached"] else ""))

    st.subheader("Convergence (rung 2)")
    kh0 = st.number_input("kh", 0.05, 7.0, float(zcur["resonances"][0]["kh"]) if zcur["resonances"] else 2.0,
                          0.01, key="z_conv_kh")
    if st.button("Show convergence table", key="z_conv_btn"):
        st.table([{k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in r.items()}
                  for r in zheng_views.convergence(zs, kh0)])

    st.subheader("Export")
    if st.button("Export run", key="z_export"):
        st.success(f"Saved to {owc_views.export_run(state, fig=zheng_views.fig_main(zcur))}")


st.set_page_config(page_title="OWC toy model", layout="wide")
st.title("OWC toy model: interactive")
if st.session_state.get("backend") != owc_views.ZHENG_NAME:
    st.caption("Learning model: damped piston, isolated absorber, regular waves, linear. "
               "Not the Zheng et al. (2019) result and not a design tool.")

with st.sidebar:
    backend = st.selectbox("Backend", list(owc_views.BACKENDS), key="backend")
    ZHENG = backend == owc_views.ZHENG_NAME
    if ZHENG:
        state = owc_views.default_state(cfg)
        state["backend"] = backend
        state["zheng"] = zstate = zheng_sidebar()
    else:
        params = {}
        for name, item in cfg["params"].items():
            params[name] = st.slider(f"{item['label']} [{item['unit']}]", float(item["min"]), float(item["max"]),
                                     float(item["default"]), float(item["step"]), help=item["tip"], key="p_" + name)
            if name == "zeta":
                zb1, zb2 = st.columns(2)
                zb1.button("Toy default (0.30)", key="zeta_toy", on_click=_set_zeta, args=("toy",),
                           help="The value the regression anchors use.")
                zb2.button("Physical (≈0.54)", key="zeta_fk", on_click=_set_zeta, args=("fk",),
                           help="Damping consistent with the Froude-Krylov force + Haskind relation for the "
                                "current inputs, evaluated at the natural frequency sqrt(g/L) (VERIFICATION.md §4). "
                                "Diffraction is neglected: an estimate.")
                if st.session_state.get("zeta_set") == params["zeta"]:  # note only while the slider is untouched
                    st.caption(st.session_state["zeta_note"])
                dopts = cfg["damping"]["options"]
                params["damping"] = st.radio("Damping model", list(dopts), format_func=dopts.get, key="p_damping",
                                             help=cfg["damping"]["tip"])
                if params["damping"] != "constant":
                    st.caption("zeta is not used in this mode; regression anchors do not apply.")
        T_cfg = cfg["T"]
        T = st.slider(f"{T_cfg['label']} [{T_cfg['unit']}]", float(T_cfg["min"]), float(T_cfg["max"]),
                      float(T_cfg["default"]), float(T_cfg["step"]), help=T_cfg["tip"], key="T")

        state = owc_views.default_state(cfg)
        state["params"] = params
        state["T"] = T
        state["backend"] = backend

        mode_label = st.radio("Turbine cPTO", [OPTIMAL, FIXED], key="c_pto_mode_label", help=cfg["c_pto"]["tip"])
        c_sel = float(o.radiation_coefficients(2 * np.pi / T, o.Params(**params))[0])
        if mode_label == FIXED:
            default_log = float(np.log10(owc_views.curves(state)["c_pto_fixed_used"]))
            log_c = st.slider("log10 cPTO [m^3/s/Pa]", float(cfg["c_pto"]["log10_min"]),
                              float(cfg["c_pto"]["log10_max"]), default_log, float(cfg["c_pto"]["log10_step"]), key="log_c_pto")
            c_val = 10 ** log_c
            state["c_pto_mode"] = "fixed"
            state["c_pto_fixed"] = c_val
            st.caption(f"cPTO = {c_val:.4g} m^3/s/Pa = {c_val / c_sel:.3g} x c at the selected T")
        else:
            state["c_pto_mode"] = "optimal"

cur = None if ZHENG else owc_views.curves(state)
op = None if ZHENG else cur["op"]

tab_learn, tab_model, tab_site, tab_ex, tab_gloss, tab_phys = st.tabs(
    ["Learn step by step", "Model", "Site & annual energy", "Exercises", "Glossary", "Physics checks"])

with tab_learn:
    if ZHENG:
        st.info(LEARN_INFO)
    else:
        learn.render_learn(state, cur)

with tab_gloss:
    learn.render_glossary()

with tab_phys:
    if ZHENG:
        st.info("Toy-model checks are shown with the piston (toy) backend. Below: validation of the Zheng backend; "
                "the full verification ladder (rungs 1-6) is in REPORT_B.md.")
    else:
        learn.render_physics_checks(state, op)
        st.divider()
    learn.render_zheng_validation(cfg)

with tab_model:
    if ZHENG:
        render_zheng(state, zstate)
    else:
        # validity: always visible
        if op["warnings"]:
            for msg in op["warnings"]:
                st.warning(msg)
        else:
            st.success("Operating point inside the toy model's own validity limits (k r_in < 1, kh > 0.5).")
        if np.any(cur["valid_k_rin_gt_1"]):
            st.info("Grey band on the kh plots: k r_in > 1, where the piston idea is weak (the toy model's own "
                    "assumption, not a literature criterion). Orange band: kh < 0.5.")

        dark = learn.is_dark()
        # full width each: room for the reference-line labels and the long legend names
        learn.show_chart(charts.coefficients(cur, state, dark))
        learn.show_chart(charts.eta(cur, state, dark))
        learn.show_chart(charts.sweep(cur, state, dark))

        # operating point table
        st.subheader("Operating point (regular wave, period T)")
        st.table([
            {"quantity": "wave period T", "value": f"{op['T']:.4g}", "unit": "s"},
            {"quantity": "angular frequency w", "value": f"{op['w']:.4g}", "unit": "rad/s"},
            {"quantity": "wave number k", "value": f"{op['k']:.4g}", "unit": "1/m"},
            {"quantity": "kh", "value": f"{op['kh']:.4g}", "unit": "dimensionless"},
            {"quantity": "k r_in", "value": f"{op['k_rin']:.4g}", "unit": "dimensionless"},
            {"quantity": "incident power Pin", "value": f"{op['Pin_kW_per_m']:.4g}", "unit": "kW/m"},
            {"quantity": "cPTO used", "value": f"{op['c_pto']:.4g}", "unit": "m^3/s/Pa"},
            {"quantity": "power P", "value": f"{op['P_kW']:.4g}", "unit": "kW"},
            {"quantity": "capture width ratio eta = kP/Pin", "value": f"{op['eta']:.4g}", "unit": "dimensionless"},
            {"quantity": "capture width P/Pin", "value": f"{op['capture_width_m']:.4g}", "unit": "m"},
            {"quantity": "1/k", "value": f"{op['inv_k_m']:.4g}", "unit": "m"},
            {"quantity": "chamber pressure |p|", "value": f"{op['p_abs_Pa']:.4g}", "unit": "Pa"},
            {"quantity": "phase of p relative to Qe", "value": f"{op['p_phase_deg']:.4g}", "unit": "deg"},
            {"quantity": "in phase with Qe", "value": "yes" if op["in_phase"] else "no", "unit": "dimensionless"},
        ])
        st.caption("eta <= 1 for this isolated model by construction (Haskind relation). The optimal-cPTO curve "
                   "is an upper bound: a real turbine cannot retune at every frequency.")

        # sanity check: always visible
        san = cur["sanity"]
        st.subheader("Sanity check (always visible)")
        st.table([
            {"quantity": "Pin (finite depth)", "value": f"{san['Pin_kW_per_m']:.4g}", "unit": "kW/m"},
            {"quantity": "Pin_deep = rho g^2 A^2 T / (8 pi)", "value": f"{san['Pin_deep_kW_per_m']:.4g}", "unit": "kW/m"},
            {"quantity": "kh", "value": f"{san['kh']:.4g}", "unit": "dimensionless"},
            {"quantity": "rule 0.49 Hs^2 Te (Hs = 2A, Te = T)", "value": f"{san['rule_049_kW_per_m']:.4g}", "unit": "kW/m"},
        ])
        st.markdown(SANITY_TEXT)
        st.write(f"Pin_deep / rule = {san['Pin_deep_kW_per_m'] / san['rule_049_kW_per_m']:.2f}")

        # export / load
        st.subheader("Export / load")
        if st.button("Export run"):
            folder = owc_views.export_run(state, fig=run_demo.make_figure(cur, state))
            st.success(f"Saved to {folder}")
        st.file_uploader("Load run.json", type="json", key="upload")
        st.button("Restore state from file", on_click=_restore)

with tab_site:
    site_tab.render_site(state, zstate if ZHENG else None, cfg)

with tab_ex:
    if ZHENG:
        st.info(LEARN_INFO)
    else:
        preds = owc_views.load_predictions()
        for ex in owc_views.EXERCISES:
            eid = ex["id"]
            st.subheader(f"Exercise {eid}: {ex['title']}")
            st.write(ex["question"])
            pred = st.text_area("My prediction (stored only in predictions.json in this folder)",
                                value=preds.get(eid, ""), key="pred_" + eid)
            if st.button("Run", key="run_" + eid):
                owc_views.save_prediction(eid, pred)
                st.session_state["shown_" + eid] = True
            if st.session_state.get("shown_" + eid):
                res = owc_views.run_exercise(eid, state)
                left, right = st.columns(2)
                with left:
                    st.markdown("**My prediction**")
                    st.write(pred)
                with right:
                    st.markdown("**Result**")
                    st.json(res)
                if eid == "2":
                    st.write(f"H_crit = {res['H_crit_m']:.4f} m, bisection tolerance {res['tol_m']:g} m")
