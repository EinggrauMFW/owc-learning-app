import dataclasses
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import owc_toy as o  # noqa: E402
import owc_views as v  # noqa: E402
import run_demo  # noqa: E402

P = o.Params()
W = np.linspace(0.5, 3, 50)


def test_backend_contract():
    assert isinstance(o.PISTON, o.Backend)
    c, a = o.PISTON.coefficients(W, P)
    qe = o.PISTON.excitation(W, P)
    for arr in (c, a, qe):
        assert arr.shape == (50,)
        assert np.all(np.isfinite(arr))
    assert np.all(c > 0) and np.all(qe > 0)
    v = o.PISTON.validity(W, P)
    assert set(v) == {"k_rin_gt_1", "kh_lt_0p5", "no_pto_resonance"}
    for item in v.values():
        assert isinstance(item["mask"], np.ndarray) and item["mask"].dtype == bool
        assert item["mask"].shape == (50,)
        assert isinstance(item["message"], str) and item["message"]


def test_backend_kwarg_matches_default():
    cp = 0.012
    assert np.array_equal(o.power(W, cp, P), o.power(W, cp, P, backend=o.PISTON))
    assert np.array_equal(o.capture_width_ratio(W, cp, P),
                          o.capture_width_ratio(W, cp, P, backend=o.PISTON))
    assert np.array_equal(o.optimal_c_pto(W, P), o.optimal_c_pto(W, P, backend=o.PISTON))
    assert o.resonance_frequency_with_pto(P) == o.resonance_frequency_with_pto(P, backend=o.PISTON)


def test_validity_k_rin_hand_case():
    # k r_in = 1 -> k = 0.25 1/m (h = 10, r_in = 4), so w1 = sqrt(g k tanh(k h))
    w1 = np.sqrt(9.81 * 0.25 * np.tanh(2.5))
    m = o.PISTON.validity(np.array([w1 * (1 - 1e-6), w1 * (1 + 1e-6)]), P)["k_rin_gt_1"]["mask"]
    assert not m[0] and m[1]
    # k h = 0.5 -> k = 0.05 1/m, so w2 = sqrt(g k tanh(k h))
    w2 = np.sqrt(9.81 * 0.05 * np.tanh(0.5))
    m = o.PISTON.validity(np.array([w2 * (1 - 1e-6), w2 * (1 + 1e-6)]), P)["kh_lt_0p5"]["mask"]
    assert m[0] and not m[1]


def test_critical_H_air_bisection():
    H, tol = o.critical_H_air(P)
    assert o.has_pto_resonance(replace(P, H_air=H - tol))
    assert not o.has_pto_resonance(replace(P, H_air=H + tol))
    assert abs(H - 8.8434) < 1e-3
    # Independent cross-check: resonance iff H < max_w (-a(w) v^2 rho0 / (S w))
    w = np.linspace(0.1, 10, 200001)
    _, a = o.radiation_coefficients(w, P)
    h_max = np.max(-a * P.v**2 * P.rho0 / (P.S * w))
    assert abs(h_max - H) < 2 * tol


def test_no_resonance_flag():
    assert np.all(o.PISTON.validity(W, replace(P, H_air=12.0))["no_pto_resonance"]["mask"])
    assert not np.any(o.PISTON.validity(W, P)["no_pto_resonance"]["mask"])


def test_config_defaults_match_params_and_anchors():
    cfg = v.load_config()
    defaults = dataclasses.asdict(o.Params())
    assert cfg["damping"]["default"] == defaults.pop("damping")  # the one non-slider parameter
    assert set(cfg["params"]) == set(defaults)
    for key, val in defaults.items():
        assert cfg["params"][key]["default"] == val
    cur = v.curves(v.default_state(cfg))
    assert cur["w_nat"] == pytest.approx(1.528, abs=5e-4)
    assert cur["w_res"] == pytest.approx(1.647, abs=5e-4)
    assert cur["c_res"] == pytest.approx(1.199e-2, rel=1e-3)
    op = cur["op"]
    assert op["eta"] == pytest.approx(1.000, abs=1e-3)
    assert op["Pin_kW_per_m"] == pytest.approx(15.5, abs=0.05)
    assert op["capture_width_m"] == pytest.approx(op["inv_k_m"], abs=0.02)
    assert np.all(cur["eta_opt"] <= 1 + 1e-12)


def test_run_json_round_trip(tmp_path):
    state = v.default_state()
    state["params"]["H_air"] = 7.0
    state["T"] = 5.0
    state["c_pto_mode"] = "fixed"
    state["c_pto_fixed"] = 0.02
    folder = v.export_run(state, tmp_path)
    loaded = v.load_run(folder)
    assert loaded == state
    ref, got = v.curves(state), v.curves(loaded)
    arrays = [key for key in ref if isinstance(ref[key], np.ndarray)]
    assert "eta_fixed" in arrays and "sweep_eta" in arrays
    for key in arrays:
        if ref[key].dtype == bool:
            np.testing.assert_array_equal(got[key], ref[key], err_msg=key)
        else:
            np.testing.assert_allclose(got[key], ref[key], rtol=0, atol=1e-12, err_msg=key)
    assert (folder / "curves.csv").read_text(encoding="utf-8").splitlines()[0].find("c [m^3/s/Pa]") >= 0
    run = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert {"versions", "git_commit", "date"} <= set(run)


# Dimensional check: every public function run on pint quantities (pint is test-only).
_PINT_CHECKS = [
    pytest.param("natural_frequency", lambda w, P, cp: o.natural_frequency(P), "1/s", id="natural_frequency"),
    pytest.param("wavenumber", lambda w, P, cp: o.wavenumber(w, P.h), "1/m", id="wavenumber"),
    pytest.param("group_velocity", lambda w, P, cp: o.group_velocity(w, P.h), "m/s", id="group_velocity"),
    pytest.param("incident_power", lambda w, P, cp: o.incident_power(w, P), "W/m", id="incident_power"),
    pytest.param("radiation_c", lambda w, P, cp: o.radiation_coefficients(w, P)[0], "m^3/s/Pa", id="radiation_c"),
    pytest.param("radiation_a", lambda w, P, cp: o.radiation_coefficients(w, P)[1], "m^3/s/Pa", id="radiation_a"),
    pytest.param("a_pto", lambda w, P, cp: o.a_pto(w, P), "m^3/s/Pa", id="a_pto"),
    pytest.param("excitation_flow", lambda w, P, cp: o.excitation_flow(w, P), "m^3/s", id="excitation_flow"),
    pytest.param("optimal_c_pto", lambda w, P, cp: o.optimal_c_pto(w, P), "m^3/s/Pa", id="optimal_c_pto"),
    pytest.param("pressure", lambda w, P, cp: o.pressure(w, cp, P), "Pa", id="pressure"),
    pytest.param("power", lambda w, P, cp: o.power(w, cp, P), "W", id="power"),
    pytest.param("capture_width_ratio", lambda w, P, cp: o.capture_width_ratio(w, cp, P), "dimensionless", id="capture_width_ratio"),
    pytest.param("optimal_power", lambda w, P, cp: o.optimal_power(w, P), "W", id="optimal_power"),
]


@pytest.mark.parametrize("name, fn, target", _PINT_CHECKS)
def test_dimensions_with_pint(monkeypatch, name, fn, target):
    pint = pytest.importorskip("pint")
    ureg = pint.UnitRegistry()
    monkeypatch.setattr(o, "G", 9.81 * ureg("m/s^2"))
    P = o.Params(h=10 * ureg.m, r_in=4 * ureg.m, L=4.2 * ureg.m, zeta=0.3 * ureg.dimensionless,
                 H_air=5 * ureg.m, rho=1025 * ureg("kg/m^3"), rho0=1.2 * ureg("kg/m^3"),
                 v=340 * ureg("m/s"), A=1 * ureg.m)
    w = np.array([1.0, 1.6]) * ureg("rad/s")
    cpto = 0.012 * ureg("m^3/s/Pa")
    q = fn(w, P, cpto)
    assert q.dimensionality == ureg(target).dimensionality, (name, q.dimensionality, target)


def test_app_smoke():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
    assert not at.exception
    at.radio(key="c_pto_mode_label").set_value("fixed").run()
    assert not at.exception
    at.slider(key="p_H_air").set_value(12.0).run()
    assert not at.exception
    assert any("No PTO resonance" in w.value for w in at.warning)


def test_exercises_numbers():
    state = v.default_state()
    h = v.run_exercise("2", state)
    assert abs(h["H_crit_m"] - 8.8434) < 1e-3
    assert h["resonance_at_H_minus_tol"] is True
    assert h["resonance_at_H_plus_tol"] is False
    r3 = v.run_exercise("3", state)
    assert r3["P_opt_over_Pin_m"] == pytest.approx(r3["inv_k_m"], rel=1e-6)
    assert v.run_exercise("4", state)["n_crossings"] == 2


def test_export_writes_figures(tmp_path):
    state = v.default_state()
    folder = v.export_run(state, tmp_path, fig=run_demo.make_figure(v.curves(state), state))
    assert (folder / "figure.png").stat().st_size > 0
    assert (folder / "figure.svg").stat().st_size > 0


def test_predictions_local_file(tmp_path):
    path = tmp_path / "p.json"
    v.save_prediction("1", "x", path=path)
    assert v.load_predictions(path=path) == {"1": "x"}


def _default_motion(**state_kw):
    state = v.default_state()
    state.update(state_kw)
    return state, v.chamber_motion(state)


def test_chamber_motion_flow_balance():
    _, m = _default_motion()
    z = lambda n: complex(m[n + "_re"], m[n + "_im"])  # noqa: E731
    assert abs(z("q_rad") + z("q_pto") - z("Qe")) <= 1e-12 * abs(z("Qe"))
    assert abs(z("q_turb") + z("q_air") - z("q_pto")) <= 1e-12 * abs(z("q_pto"))
    _, m = _default_motion(T=2 * np.pi / o.resonance_frequency_with_pto(o.Params()))
    assert abs(m["p_deg"] - m["Qe_deg"]) < 0.1


def test_chamber_motion_open_chamber_limit():
    _, m = _default_motion(c_pto_mode="fixed", c_pto_fixed=1e6)
    assert m["p_abs"] * 1e6 < 1.01 * m["Qe_abs"]
    assert abs(m["z_im"]) / m["z_abs"] < 1e-3
    assert m["z_re"] > 0


def test_learn_tab_renders_every_step():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60).run()
    assert not at.exception
    for option in at.radio(key="learn_step").options:
        at.radio(key="learn_step").set_value(option).run()
        assert not at.exception, option
    at.text_input(key="gloss_filter").set_value("pto").run()
    assert not at.exception


def test_svg_animation_html_selfcontained():
    import learn

    state, m = _default_motion()
    html = learn.svg_animation_html(m, v.load_config())
    assert "<svg" in html and "requestAnimationFrame" in html
    assert "http://" not in html and "https://" not in html


# ---- Zheng backend ----------------------------------------------------------------------------

def _zstate(n=20):
    import zheng_views
    zs = zheng_views.default_zstate(v.load_config())
    zs["grid"]["n"] = n
    return zs


def test_zheng_curves_small_grid_and_cache(tmp_path, monkeypatch):
    import time
    import zheng_views as zv

    monkeypatch.setattr(zv, "CACHE_DIR", tmp_path)
    zs = _zstate(20)
    t0 = time.perf_counter()
    c1 = zv.curves(zs)
    t1 = time.perf_counter() - t0
    assert not c1["cached"]
    for k in ("c", "a", "Qbar", "eta_opt", "cbar", "abar", "aPTObar", "cPTObar"):
        assert np.all(np.isfinite(c1[k])), k
    assert np.all(c1["c"] > 0) and np.all(c1["eta_opt"] > 0)
    assert any(1.5 <= r["kh"] <= 3.2 for r in c1["resonances"])
    t0 = time.perf_counter()
    c2 = zv.curves(zs)
    t2 = time.perf_counter() - t0
    assert c2["cached"] and t2 < t1 / 5
    for k in ("c", "a", "Qe", "eta_opt"):
        assert np.array_equal(c1[k], c2[k])


def test_app_zheng_smoke(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    import zheng_views as zv

    monkeypatch.setattr(zv, "CACHE_DIR", tmp_path)
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120).run()
    at.session_state["z_n"] = 20  # before switching, so the first Zheng run is the small grid
    at.selectbox(key="backend").set_value(v.ZHENG_NAME).run()
    assert not at.exception
    assert any("perfectly reflecting" in i.value for i in at.info)
    assert any("not been computed" in x.value for x in at.warning)  # nothing solved before Compute
    at.button(key="z_compute").click().run()
    assert not at.exception
    assert any("solved 20 frequencies" in c.value for c in at.caption)


def test_zheng_export(tmp_path, monkeypatch):
    import zheng_views as zv

    monkeypatch.setattr(zv, "CACHE_DIR", tmp_path / "cache")
    state = v.default_state()
    state["backend"] = v.ZHENG_NAME
    state["zheng"] = _zstate(20)
    folder = v.export_run(state, out_root=tmp_path / "exports")
    assert (folder / "zcurves.csv").exists()
    run = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert run["backend"] == v.ZHENG_NAME and "zheng" in run["state"]


def test_charts_build_valid_vegalite(tmp_path, monkeypatch):
    import charts
    import zheng_views as zv

    monkeypatch.setattr(zv, "CACHE_DIR", tmp_path)
    st_ = v.default_state()
    cur = v.curves(st_)
    kh = np.linspace(0.3, 3, 12)
    cons = {"kh": kh, "c_DM": kh, "c_FFC": kh * 1.01, "c_HR": kh * 0.99,
            "rel_FFC": np.full(12, 0.01), "rel_HR": np.full(12, 0.01)}
    zcur = zv.curves(_zstate(20))
    for dark in (False, True):
        built = [charts.coefficients(cur, st_, dark), charts.eta(cur, st_, dark), charts.sweep(cur, st_, dark),
                 charts.dispersion(st_, cur, dark), charts.phasor(v.chamber_motion(st_), dark),
                 *charts.zheng_main(zcur, dark), *charts.zheng_consistency(cons, dark)]
        for ch in built:
            assert ch.to_dict()
            assert len(charts.data_of(ch)) > 0
        for ch in built[:4] + built[5:]:
            assert '"params"' in json.dumps(ch.to_dict())


def test_physics_checks_tab_runs_time_domain():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120).run()
    at.button(key="phys_run").click().run()
    assert not at.exception
    rows = [t for t in at.table if "relative difference" in str(t.value)]
    assert rows, "time-domain check table missing"


def test_zeta_presets():
    from streamlit.testing.v1 import AppTest
    import owc_toy as o

    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120).run()
    at.button(key="zeta_fk").click().run()
    assert not at.exception
    z_expected = round(o.zeta_froude_krylov(o.Params())[0], 2)
    assert at.slider(key="p_zeta").value == pytest.approx(z_expected)  # 0.63 at the defaults
    assert any("Froude-Krylov" in c.value for c in at.caption)
    at.button(key="zeta_toy").click().run()
    assert at.slider(key="p_zeta").value == pytest.approx(0.3)


def test_zheng_validation_section(tmp_path, monkeypatch):
    """Validation charts build; the thin-wall section waits for its button (nothing solved before)."""
    import json
    import zheng_views as zv
    import charts

    monkeypatch.setattr(zv, "CACHE_DIR", tmp_path)
    ref = json.loads((Path(__file__).resolve().parents[1] / "docs" / "rungs" / "rung3_reference.json").read_text())
    kh = np.linspace(0.5, 7, 30)
    for ch in charts.thin_wall_validation(kh, {"c": np.sin(kh) + 2, "a": np.cos(kh)}, ref):
        assert "params" in json.dumps(ch.to_dict())
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120).run()
    assert not at.exception
    assert any("Not computed yet" in w.value for w in at.warning)


def test_site_tab_toy():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=180).run()
    next(b for b in at.button if b.key == "site_aep").click()
    at.run()
    assert not at.exception
    m = next(x for x in at.metric if "Annual energy" in x.label)
    assert float(m.value) > 0
    assert any("No wave transformation" in e.value for e in list(at.warning) + list(at.info))


def test_site_charts_build():
    import pandas as pd
    import charts

    w = np.linspace(0.2, 4, 100)
    df = pd.DataFrame({"te0": [7.0, 7.5], "te1": [7.5, 8.0], "hs0": [0.5, 0.5], "hs1": [1.0, 1.0], "te": [7.25, 7.75],
                       "hs": [0.75, 0.75], "hours": [16.0, 0.0], "P_fixed_kW": [1.0, 2.0]})
    for dark in (False, True):
        assert "params" in json.dumps(charts.site_line(w, w**2, "y", "t", dark).to_dict())
        assert "tooltip" in json.dumps(charts.site_heatmap(df, "P_fixed_kW", "t", dark).to_dict())
