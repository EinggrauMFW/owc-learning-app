"""App-facing helpers for the toy OWC: config, state, curves and run export. No UI imports.

Everything the views show is computed here from a plain-JSON state dict, so the
UI only draws numbers. Units as in owc_toy.py (SI).
"""
from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import replace
from datetime import datetime
from importlib import metadata
from pathlib import Path

import numpy as np

import owc_toy as o
import owc_zheng
import zheng_views

CONFIG_PATH = Path(__file__).with_name("config") / "defaults.json"
REPO_DIR = Path(__file__).resolve().parent
BACKENDS = {o.PISTON.name: o.PISTON, owc_zheng.ZhengWallBackend.name: owc_zheng.ZHENG}
ZHENG_NAME = owc_zheng.ZhengWallBackend.name  # Zheng is NOT routed through the toy curves()


def load_config(path=CONFIG_PATH) -> dict:
    """Parsed config/defaults.json."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def default_state(cfg=None) -> dict:
    """Plain-JSON app state."""
    cfg = cfg or load_config()
    return {
        "params": {**{name: cfg["params"][name]["default"] for name in cfg["params"]},
                   "damping": cfg["damping"]["default"]},
        "T": cfg["T"]["default"],
        "c_pto_mode": cfg["c_pto"]["mode"],
        "c_pto_fixed": None,  # None: c at the PTO resonance
        "backend": o.PISTON.name,
        "grid": {k: cfg["grid"][k] for k in ("w_min", "w_max", "n")},
        "c_pto_sweep": {k: cfg["c_pto_sweep"][k] for k in ("min", "max", "n")},
    }


def curves(state) -> dict:
    """Every number the views show, computed from state alone (no UI)."""
    P = o.Params(**state["params"])
    b = BACKENDS[state["backend"]]
    g = state["grid"]
    w = np.linspace(g["w_min"], g["w_max"], g["n"])

    c, a = b.coefficients(w, P)
    c_opt = o.optimal_c_pto(w, P, backend=b)
    has_res = bool(o.has_pto_resonance(P, backend=b))
    w_nat = float(o.natural_frequency(P))
    w_res = float(o.resonance_frequency_with_pto(P, w_lo=0.1, w_hi=10.0, n=200001, backend=b)) if has_res else None
    c_res = float(b.coefficients(w_res, P)[0]) if has_res else None
    if state["c_pto_fixed"] is not None:
        c_pto_fixed_used = float(state["c_pto_fixed"])
    elif has_res:
        c_pto_fixed_used = c_res
    else:
        c_pto_fixed_used = float(b.coefficients(w_nat, P)[0])
    eta_fixed = o.capture_width_ratio(w, c_pto_fixed_used, P, backend=b)

    validity = b.validity(w, P)
    k = o.wavenumber(w, P.h)
    out = {
        "w": w,
        "T": 2 * np.pi / w,
        "k": k,
        "kh": k * P.h,
        "c": c,
        "a": a,
        "a_pto": o.a_pto(w, P),
        "c_pto_opt": c_opt,
        "eta_opt": o.capture_width_ratio(w, c_opt, P, backend=b),
        "eta_fixed": eta_fixed,
        "w_nat": w_nat,
        "has_res": has_res,
        "w_res": w_res,
        "c_res": c_res,
        "c_pto_fixed_used": c_pto_fixed_used,
        "validity_messages": {name: item["message"] for name, item in validity.items()},
    }
    for name, item in validity.items():
        out["valid_" + name] = item["mask"]

    # operating point at the selected period
    T_sel = float(state["T"])
    w_sel = 2 * np.pi / T_sel
    k_sel = float(o.wavenumber(w_sel, P.h))
    pin = float(o.incident_power(w_sel, P))
    if state["c_pto_mode"] == "optimal":
        cp = float(o.optimal_c_pto(w_sel, P, backend=b))
    else:
        cp = c_pto_fixed_used
    pw = float(o.power(w_sel, cp, P, backend=b))
    p_sel = o.pressure(w_sel, cp, P, backend=b)
    p_phase = float(np.degrees(np.angle(p_sel)))
    sel_valid = validity_at(b, w_sel, P)
    out["op"] = {
        "w": w_sel,
        "T": T_sel,
        "k": k_sel,
        "kh": k_sel * P.h,
        "k_rin": k_sel * P.r_in,
        "Pin_kW_per_m": pin / 1e3,
        "c_pto": cp,
        "P_kW": pw / 1e3,
        "eta": float(o.capture_width_ratio(w_sel, cp, P, backend=b)),
        "capture_width_m": pw / pin,
        "inv_k_m": 1 / k_sel,
        "p_abs_Pa": float(abs(p_sel)),
        "p_phase_deg": p_phase,
        "in_phase": bool(abs(p_phase) < 1.0),
        "warnings": [validity[name]["message"] for name in validity if sel_valid[name]],
    }

    # sanity values to compare the operating point with
    out["sanity"] = {
        "Pin_kW_per_m": pin / 1e3,
        "Pin_deep_kW_per_m": P.rho * o.G**2 * P.A**2 * T_sel / (8 * np.pi) / 1e3,
        "kh": k_sel * P.h,
        "rule_049_kW_per_m": 0.49 * (2 * P.A) ** 2 * T_sel,  # irregular-sea rule, Hs = 2A, Te = T
    }

    # cPTO sweep at the selected period
    s = state["c_pto_sweep"]
    sweep = np.geomspace(s["min"], s["max"], s["n"])
    sweep_opt = float(o.optimal_c_pto(w_sel, P, backend=b))
    out["sweep_c_pto"] = sweep
    out["sweep_eta"] = o.capture_width_ratio(w_sel, sweep, P, backend=b)
    out["sweep_c_pto_opt"] = sweep_opt
    out["sweep_eta_opt"] = float(o.capture_width_ratio(w_sel, sweep_opt, P, backend=b))
    return out


def chamber_motion(state) -> dict:
    """Complex amplitudes of the chamber at the selected period, as plain floats (for the Learn drawing)."""
    P = o.Params(**state["params"])
    b = BACKENDS[state["backend"]]
    op = curves(state)["op"]
    w, cpto = op["w"], op["c_pto"]
    c, a = (float(x) for x in b.coefficients(w, P))
    apto, S = float(o.a_pto(w, P)), P.S
    Qe = abs(b.excitation(w, P)) * (-1j)  # phase of Qe is a DRAWING ASSUMPTION (small-chamber limit), not a toy output
    p = Qe / ((c + cpto) - 1j * (a + apto))
    q_rad = (c - 1j * a) * p
    q_pto = (cpto - 1j * apto) * p
    q_turb = cpto * p
    q_air = -1j * apto * p
    z = 1j * q_pto / (w * S)
    out = {"A": P.A, "h": P.h, "r_in": P.r_in, "H_air": P.H_air, "L": P.L, "w": w, "T": op["T"],
           "k": op["k"], "wavelength": 2 * np.pi / op["k"]}
    for name, val in (("Qe", Qe), ("p", p), ("q_rad", q_rad), ("q_pto", q_pto), ("q_turb", q_turb),
                      ("q_air", q_air), ("z", z)):
        val = complex(val)
        out.update({name + "_re": val.real, name + "_im": val.imag, name + "_abs": abs(val),
                    name + "_deg": float(np.degrees(np.angle(val)))})
    return out


def validity_at(backend, w_sel, P) -> dict:
    """Validity masks at one frequency, as {name: bool}."""
    v = backend.validity(np.array([w_sel]), P)
    return {name: bool(item["mask"][0]) for name, item in v.items()}


def _plain(x):
    """json default: numpy scalars and arrays to Python types."""
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    raise TypeError(f"not JSON serialisable: {type(x)}")


def _versions() -> dict:
    out = {"python": platform.python_version()}
    for name in ("numpy", "scipy", "matplotlib", "streamlit"):
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pass
    return out


def _git_commit():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_DIR, capture_output=True,
                           text=True, check=True)
        return r.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def export_run(state, out_root=REPO_DIR / "exports", fig=None) -> Path:
    """Write curves.csv, sweep.csv and run.json into out_root/run_<stamp>/ and return that folder."""
    zheng = state["backend"] == ZHENG_NAME
    cur = zheng_views.curves(state["zheng"]) if zheng else curves(state)
    stamp = datetime.now().strftime("run_%Y%m%d-%H%M%S")
    folder = Path(out_root) / stamp
    n = 1
    while folder.exists():
        folder = Path(out_root) / f"{stamp}-{n}"
        n += 1
    folder.mkdir(parents=True)

    if zheng:
        return _export_zheng(state, cur, folder, fig)

    names = ["w", "T", "k", "kh", "c", "a", "a_pto", "c_pto_opt", "eta_opt", "eta_fixed"]
    units = {"w": "rad/s", "T": "s", "k": "1/m", "kh": "-", "c": "m^3/s/Pa", "a": "m^3/s/Pa",
             "a_pto": "m^3/s/Pa", "c_pto_opt": "m^3/s/Pa", "eta_opt": "-", "eta_fixed": "-"}
    valid = [key for key in cur if key.startswith("valid_")]
    cols = [cur[n_] for n_ in names] + [cur[key].astype(float) for key in valid]
    header = ",".join([f"{n_} [{units[n_]}]" for n_ in names] + [f"{key} [0/1]" for key in valid])
    np.savetxt(folder / "curves.csv", np.column_stack(cols), delimiter=",", header=header,
               comments="", fmt="%.17g")

    sweep_header = "c_pto [m^3/s/Pa],eta [-]"
    np.savetxt(folder / "sweep.csv", np.column_stack([cur["sweep_c_pto"], cur["sweep_eta"]]),
               delimiter=",", header=sweep_header, comments="", fmt="%.17g")

    if fig is not None:
        fig.savefig(folder / "figure.png", dpi=160)
        fig.savefig(folder / "figure.svg")
    run = {
        "state": state,
        "backend": state["backend"],
        "versions": _versions(),
        "git_commit": _git_commit(),
        "date": datetime.now().isoformat(timespec="seconds"),
        "operating_point": cur["op"],
        "note": "Toy piston model (isolated, regular waves). Not the Zheng et al. (2019) result.",
    }
    with open(folder / "run.json", "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2, default=_plain)
    return folder


def _export_zheng(state, cur, folder, fig):
    names = ["kh", "w", "Qbar", "cbar", "abar", "aPTObar", "cPTObar", "eta_opt"]
    units = {"kh": "-", "w": "rad/s", "Qbar": "-", "cbar": "-", "abar": "-", "aPTObar": "-",
             "cPTObar": "-", "eta_opt": "-"}
    np.savetxt(folder / "zcurves.csv", np.column_stack([cur[n_] for n_ in names]), delimiter=",",
               header=",".join(f"{n_} [{units[n_]}]" for n_ in names), comments="", fmt="%.17g")
    if fig is not None:
        fig.savefig(folder / "figure.png", dpi=160)
        fig.savefig(folder / "figure.svg")
    run = {
        "state": state,
        "backend": state["backend"],
        "versions": _versions(),
        "git_commit": _git_commit(),
        "date": datetime.now().isoformat(timespec="seconds"),
        "resonances": cur["resonances"],
        "note": "Zheng et al. (2019) wall backend: ideal reflecting wall, linear, regular waves.",
    }
    with open(folder / "run.json", "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2, default=_plain)
    return folder


PREDICTIONS_PATH = REPO_DIR / "predictions.json"


def load_predictions(path=PREDICTIONS_PATH) -> dict:
    """Stored exercise predictions {id: text}; {} if the file is missing."""
    if not Path(path).exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_prediction(ex_id: str, text: str, path=PREDICTIONS_PATH):
    """Write one prediction into the local JSON file (nothing is sent anywhere)."""
    data = load_predictions(path)
    data[ex_id] = text
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


EXERCISES = [
    {"id": "1", "title": "Damping ratio",
     "question": "Set zeta from 0.3 to 0.15. Predict: what happens to the peak of c, to the width of the "
                 "eta curve for the fixed cPTO, and to the optimal cPTO at resonance?"},
    {"id": "2", "title": "Air compressibility",
     "question": "Increase H_air from 2 m upwards. At what H_air does the PTO resonance (a + aPTO = 0) "
                 "disappear? Explain what that means for chamber design, using the signs of a and aPTO."},
    {"id": "3", "title": "Capture width check",
     "question": "At the PTO resonance, compare P_opt / Pin with 1/k. Why is that the right answer for an "
                 "isolated axisymmetric absorber?"},
    {"id": "4", "title": "Bridge to the paper",
     "question": "In Zheng et al. (2019) Fig. 5c, find the intersections of a and -aPTO for the wall case. "
                 "How many does this toy model have, and what physical mode is missing?"},
]


def run_exercise(ex_id: str, state) -> dict:
    """Numbers for one exercise (plain Python types). No prose beyond labels."""
    P = o.Params(**state["params"])
    b = BACKENDS[state["backend"]]
    if ex_id == "1":
        rows = []
        for z in (state["params"]["zeta"], 0.15):
            cur = curves({**state, "params": {**state["params"], "zeta": z}})
            m = cur["eta_fixed"] > 0.5
            rows.append({
                "zeta": float(z),
                "c_peak": float(np.max(cur["c"])),
                "kh_width_eta_fixed_gt_0p5": float(cur["kh"][m].max() - cur["kh"][m].min()) if np.any(m) else 0.0,
                "c_pto_opt_at_res": cur["c_res"],
            })
        return {"rows": rows}
    if ex_id == "2":
        H, tol = o.critical_H_air(P, backend=b)
        return {
            "H_crit_m": float(H),
            "tol_m": float(tol),
            "method": "bisection on has_pto_resonance, H_air in [0.5, 20] m",
            "resonance_at_H_minus_tol": bool(o.has_pto_resonance(replace(P, H_air=H - tol), backend=b)),
            "resonance_at_H_plus_tol": bool(o.has_pto_resonance(replace(P, H_air=H + tol), backend=b)),
        }
    if ex_id == "3":
        if not o.has_pto_resonance(P, backend=b):
            return {"error": "No PTO resonance for these inputs."}
        w_res = float(o.resonance_frequency_with_pto(P, w_lo=0.1, w_hi=10.0, n=200001, backend=b))
        return {
            "w_res": w_res,
            "T_res_s": float(2 * np.pi / w_res),
            "P_opt_over_Pin_m": float(o.optimal_power(w_res, P, backend=b) / o.incident_power(w_res, P)),
            "inv_k_m": float(1 / o.wavenumber(w_res, P.h)),
        }
    if ex_id == "4":
        w = np.linspace(0.1, 10, 200001)
        _, a = b.coefficients(w, P)
        s = a + o.a_pto(w, P)
        idx = np.where(np.sign(s[:-1]) != np.sign(s[1:]))[0]
        kh_cross = []
        for j in idx:
            w_c = w[j] - s[j] * (w[j + 1] - w[j]) / (s[j + 1] - s[j])
            kh_cross.append(float(o.wavenumber(w_c, P.h) * P.h))
        return {"n_crossings": int(len(idx)), "kh_crossings": kh_cross}
    raise ValueError(f"unknown exercise {ex_id!r}")


def load_run(path) -> dict:
    """State from a run.json (file or its folder)."""
    p = Path(path)
    if p.is_dir():
        p = p / "run.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)["state"]
