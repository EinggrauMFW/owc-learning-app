"""Numbers and figures for the Zheng et al. (2019) wall backend. No streamlit import.

zstate is plain JSON: {"params": {...}, "V0_uses", "grid": {kh_min, kh_max, n}, "consistency_n"}.
Dimensionless groups: docs/zheng2019_equations.md section 4 (paper Eq. 37).
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import replace
from pathlib import Path

import matplotlib
from matplotlib.figure import Figure
import numpy as np

import owc_toy as o
import owc_zheng as z

REPO_DIR = Path(__file__).resolve().parent
CACHE_DIR = REPO_DIR / "cache"
ZB = z.ZhengWallBackend()


def default_zstate(cfg) -> dict:
    zc = cfg["zheng"]
    return {"params": {k: v["default"] for k, v in zc["params"].items()},
            "V0_uses": zc["V0_uses"]["default"],
            "grid": {k: zc["grid"][k] for k in ("kh_min", "kh_max", "n")},
            "consistency_n": zc["consistency_n"]}


def zheng_params(zs) -> z.ZhengParams:
    q = zs["params"]
    h = q["h"]
    R = q["R_over_h"] * h
    Ri = R - q["wall_over_h"] * h
    if Ri <= 0:
        raise ValueError("inner radius Ri = R - wall*h must be positive")
    return z.ZhengParams(h=h, R=R, Ri=Ri, d=q["d_over_h"] * h, beta=float(np.radians(q["beta_deg"])),
                         M=int(q["M"]), L=int(q["L"]), rho=q["rho"], rho0=q["rho0"], v=q["v"],
                         A=q["A"], V0_uses=zs["V0_uses"])


def _key(zs, prefix):
    return CACHE_DIR / f"{prefix}_{hashlib.sha1(json.dumps(zs, sort_keys=True).encode()).hexdigest()}"


def _load(base):
    npz, js = base.with_suffix(".npz"), base.with_suffix(".json")
    if npz.exists() and js.exists():
        with np.load(npz) as f:
            return {k: f[k] for k in f.files}, json.loads(js.read_text())
    return None


def _save(base, arrays, scalars):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(base.with_suffix(".npz"), **arrays)
    base.with_suffix(".json").write_text(json.dumps(scalars))


class _Pre:
    """Backend holding already computed c, a, |Qe| on the grid (so owc_toy helpers reuse them)."""
    name = "precomputed"

    def __init__(self, c, a, qe):
        self.c, self.a, self.qe = c, a, qe

    def coefficients(self, w, p):
        return self.c, self.a

    def excitation(self, w, p, beta=None):
        return self.qe


def _resonances(kh, w, s, eta):
    """Sign changes of s = a + aPTO, linear interpolation on the grid."""
    out = []
    for j in np.where(np.sign(s[:-1]) != np.sign(s[1:]))[0]:
        t = s[j] / (s[j] - s[j + 1])
        wr = w[j] + t * (w[j + 1] - w[j])
        out.append({"kh": float(kh[j] + t * (kh[j + 1] - kh[j])), "w": float(wr), "T_s": float(2 * np.pi / wr),
                    "eta": float(eta[j] + t * (eta[j + 1] - eta[j]))})
    return out


def is_cached(zs) -> bool:
    """True if curves(zs) would load from the disk cache (no solve needed)."""
    return _load(_key(zs, "zheng")) is not None


def curves(zs, progress=None) -> dict:
    p = zheng_params(zs)
    g = zs["grid"]
    kh = np.linspace(g["kh_min"], g["kh_max"], int(g["n"]))
    w = z.w_from_kh(kh, p.h)
    base = _key(zs, "zheng")
    hit = _load(base)
    if hit:
        arr, sc = hit
        c, a, Qe = arr["c"], arr["a"], arr["Qe"]
        cached = True
    else:
        c, a, Qe = np.empty(len(w)), np.empty(len(w)), np.empty(len(w), complex)
        t0 = time.perf_counter()
        for i, wi in enumerate(w):
            sol = z.solve(wi, p, [p.beta])  # one factorisation for R and S
            q = z._Q(sol, sol["x_R"], p)
            c[i], a[i] = -q.real, q.imag
            Qe[i] = z._Q(sol, sol["x_S"][0], p)
            if progress:
                progress(i + 1, len(w))
        sc = {"solve_time_s": time.perf_counter() - t0}
        _save(base, {"c": c, "a": a, "Qe": Qe}, sc)
        cached = False
    n = len(w)
    ap = o.a_pto(w, p)
    pre = _Pre(c, a, np.abs(Qe))
    c_opt = o.optimal_c_pto(w, p, backend=pre)
    eta = o.capture_width_ratio(w, c_opt, p, backend=pre)
    sq = np.sqrt(o.G / p.h)
    f = p.rho * sq / p.h
    val = ZB.validity(w, p)
    out = {"kh": kh, "w": w, "T": 2 * np.pi / w, "c": c, "a": a, "Qe": Qe, "Qe_abs": np.abs(Qe),
           "a_pto": ap, "c_pto_opt": c_opt, "eta_opt": eta,
           "Qbar": sq * np.abs(Qe) / (p.A * p.h * o.G), "cbar": f * c, "abar": f * a,
           "aPTObar": f * ap, "cPTObar": f * c_opt,
           "resonances": _resonances(kh, w, a + ap, eta),
           "solve_time_s": float(sc["solve_time_s"]), "per_freq_s": float(sc["solve_time_s"]) / n,
           "n": n, "cached": cached,
           "validity_messages": {k: v["message"] for k, v in val.items()}}
    for k, v in val.items():
        out["valid_" + k] = v["mask"]
    return out


def consistency(zs, progress=None) -> dict:
    p = zheng_params(zs)
    n = int(zs["consistency_n"])
    kh = np.linspace(zs["grid"]["kh_min"], zs["grid"]["kh_max"], n)
    base = _key(zs, "zheng_cons")
    hit = _load(base)
    if hit:
        arr, sc = hit
        return {**arr, "kh": kh, "solve_time_s": sc["solve_time_s"], "cached": True}
    w = z.w_from_kh(kh, p.h)
    dm, ffc, hr = np.empty(n), np.empty(n), np.empty(n)
    t0 = time.perf_counter()
    for i, wi in enumerate(w):
        dm[i] = z.c_a_direct(wi, p)[0]
        ffc[i] = z.c_far_field(wi, p)
        hr[i] = z.c_haskind(wi, p)
        if progress:
            progress(i + 1, n)
    arr = {"c_DM": dm, "c_FFC": ffc, "c_HR": hr, "rel_FFC": np.abs(ffc - dm) / dm, "rel_HR": np.abs(hr - dm) / dm}
    sc = {"solve_time_s": time.perf_counter() - t0}
    _save(base, arr, sc)
    return {**arr, "kh": kh, **sc, "cached": False}


def convergence(zs, kh, pairs=((8, 10), (12, 20), (16, 30), (24, 40))) -> list[dict]:
    p0 = zheng_params(zs)
    w = float(z.w_from_kh(kh, p0.h))
    rows = []
    for M, L in pairs:
        p = replace(p0, M=M, L=L)
        sol = z.solve(w, p, [p.beta])
        q = z._Q(sol, sol["x_R"], p)
        c, a = -q.real, q.imag
        qe = abs(z._Q(sol, sol["x_S"][0], p))
        pre = _Pre(c, a, qe)
        eta = float(o.capture_width_ratio(w, o.optimal_c_pto(w, p, backend=pre), p, backend=pre))
        rows.append({"M": M, "L": L, "Qe_abs": float(qe), "c": float(c), "a": float(a), "eta_opt": eta})
    last = dict(rows[-1])
    for r in rows:
        for k in ("Qe_abs", "c", "a", "eta_opt"):
            r["d_" + k] = abs(r[k] - last[k]) / abs(last[k])
    return rows


# ---- figures -------------------------------------------------------------------------------

def fig_main(cur):
    import run_demo as r
    with matplotlib.rc_context(r.STYLE):
        fig = Figure(figsize=(12, 7.5), layout="constrained")
        (a1, a2), (a3, a4) = fig.subplots(2, 2)
        kh = cur["kh"]
        for ax in (a1, a2, a3, a4):
            ax.grid(True, color="#e6e5e1", lw=0.6)
            ax.set_axisbelow(True)
            ax.set_xlabel("kh")
            for res in cur["resonances"]:
                ax.axvline(res["kh"], color=r.AQUA, lw=0.9)
            for k in cur["validity_messages"]:
                ax.fill_between(kh, 0, 1, where=cur["valid_" + k], transform=ax.get_xaxis_transform(),
                                color="#f2d7c9", lw=0)
        a1.plot(kh, cur["Qbar"], color=r.BLUE, lw=2)
        a1.set_ylabel("$\\bar Q_e$")
        a1.set_title("(a) Excitation flow", loc="left", fontsize=10)
        a2.plot(kh, cur["cbar"], color=r.BLUE, lw=2, label="$\\bar c$")
        a2.plot(kh, cur["abar"], color=r.ORANGE, lw=2, ls="--", label="$\\bar a$")
        a2.plot(kh, -cur["aPTObar"], color=r.GREY, lw=1.5, ls=":", label="$-\\bar a_{PTO}$")
        a2.axhline(0, color="#8a8984", lw=0.8)
        a2.set_title("(b) Radiation coefficients (green: a + aPTO = 0)", loc="left", fontsize=10)
        a2.legend(frameon=False, fontsize=8)
        a3.plot(kh, cur["cPTObar"], color=r.BLUE, lw=2)
        a3.set_ylabel("$\\bar c_{PTO}$ optimal")
        a3.set_title("(c) Optimal turbine conductance", loc="left", fontsize=10)
        a4.plot(kh, cur["eta_opt"], color=r.BLUE, lw=2)
        a4.axhline(1, color=r.GREY, lw=1, ls=":")
        a4.axhline(2, color=r.GREY, lw=1, ls="--")
        x = kh.min() + 0.01 * np.ptp(kh)
        a4.text(x, 1.0, "isolated-absorber limit (eta = 1)", fontsize=8, va="bottom")
        a4.text(x, 2.0, "2 (beta-averaged wall limit)", fontsize=8, va="bottom")
        a4.set_ylabel("$\\eta$ (optimal cPTO)")
        a4.set_title("(d) Capture width ratio", loc="left", fontsize=10)
        fig.suptitle("Zheng et al. (2019) wall-mounted OWC, regular waves, linear", fontsize=9,
                     color="#52514e", x=0.01, ha="left")
    return fig


def fig_consistency(cons):
    import run_demo as r
    with matplotlib.rc_context(r.STYLE):
        fig = Figure(figsize=(11, 4), layout="constrained")
        a1, a2 = fig.subplots(1, 2)
        kh = cons["kh"]
        for ax in (a1, a2):
            ax.grid(True, color="#e6e5e1", lw=0.6)
            ax.set_axisbelow(True)
            ax.set_xlabel("kh")
        a1.plot(kh, cons["c_DM"], color=r.BLUE, lw=2, label="DM")
        a1.plot(kh, cons["c_FFC"], color=r.ORANGE, lw=2, ls="--", label="FFC")
        a1.plot(kh, cons["c_HR"], color=r.AQUA, lw=2, ls=":", label="HR")
        a1.set_ylabel("c [m$^3$/s/Pa]")
        a1.legend(frameon=False)
        a1.set_title("(a) c by three methods (rung 1)", loc="left", fontsize=10)
        a2.semilogy(kh, np.maximum(cons["rel_FFC"], 1e-16), color=r.ORANGE, lw=2, label="|FFC - DM| / DM")
        a2.semilogy(kh, np.maximum(cons["rel_HR"], 1e-16), color=r.AQUA, lw=2, label="|HR - DM| / DM")
        a2.set_ylabel("relative difference")
        a2.legend(frameon=False)
        a2.set_title("(b) Relative differences (rung 1)", loc="left", fontsize=10)
    return fig
