"""Toy OWC figure: make_figure(cur, state) returns a matplotlib Figure.

    python run_demo.py                  saves owc_toy_demo.png next to this file and prints a summary
    python run_demo.py path/to/run.json saves figure_from_run.png next to that run.json
"""
import sys
from pathlib import Path

import matplotlib
from matplotlib.figure import Figure
import numpy as np

import owc_toy as o
import owc_views

BLUE, ORANGE, AQUA, GREY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#6b6a66", "#0b0b0b"
STYLE = {"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
         "axes.edgecolor": "#8a8984", "axes.labelcolor": INK, "text.color": INK,
         "xtick.color": "#52514e", "ytick.color": "#52514e"}


def draw_coefficients(ax, cur, state):
    """Panel (a): radiation c, a and -aPTO against kh."""
    P = o.Params(**state["params"])
    kh = cur["kh"]
    ax.grid(True, color="#e6e5e1", lw=0.6)
    ax.set_axisbelow(True)
    # shading: where the toy model's own validity limits are broken
    ax.fill_between(kh, 0, 1, where=cur["valid_k_rin_gt_1"], transform=ax.get_xaxis_transform(),
                    color="#d9d8d3", alpha=0.35, lw=0)
    ax.fill_between(kh, 0, 1, where=cur["valid_kh_lt_0p5"], transform=ax.get_xaxis_transform(),
                    color="#f2d7c9", alpha=0.35, lw=0)
    ax.axvline(cur["op"]["kh"], color=INK, lw=0.8)

    s = 1e3
    ax.plot(kh, cur["c"] * s, color=BLUE, lw=2, label="c")
    ax.plot(kh, cur["a"] * s, color=ORANGE, lw=2, ls="--", label="a")
    ax.plot(kh, -cur["a_pto"] * s, color=GREY, lw=1.5, ls=":", label="-aPTO")
    ax.axhline(0, color="#8a8984", lw=0.8)
    ax.axvline(o.wavenumber(cur["w_nat"], P.h) * P.h, color=GREY, lw=1, ls=":", label="natural freq.")
    if cur["has_res"]:
        khr = o.wavenumber(cur["w_res"], P.h) * P.h
        ax.axvline(khr, color=AQUA, lw=1, ls="-")
        ax.text(khr + 0.08, 0.55, "a + aPTO = 0", color=INK, fontsize=8,
                transform=ax.get_xaxis_transform())
    else:
        ax.text(0.02, 0.97, "No PTO resonance for these inputs (a result, not an error)",
                transform=ax.transAxes, va="top", fontsize=8)
    shaded = cur["valid_k_rin_gt_1"]
    if np.any(shaded):
        ax.text(kh.max(), 0.97, "grey: k r_in > 1,\npiston idea weak", fontsize=7.5, ha="right",
                color="#52514e", va="top", transform=ax.get_xaxis_transform())
    ax.set_xlabel("kh  (wave number x depth)")
    ax.set_ylabel("m$^3$/s/Pa  (x10$^{-3}$)")
    ax.set_title("(a) Radiation c, a and -aPTO", loc="left", fontsize=10)
    ax.legend(frameon=False, loc="lower left", fontsize=8)


def draw_eta(ax, cur, state):
    """Panel (b): capture width ratio against kh."""
    kh = cur["kh"]
    ax.grid(True, color="#e6e5e1", lw=0.6)
    ax.set_axisbelow(True)
    # shading: where the toy model's own validity limits are broken
    ax.fill_between(kh, 0, 1, where=cur["valid_k_rin_gt_1"], transform=ax.get_xaxis_transform(),
                    color="#d9d8d3", alpha=0.35, lw=0)
    ax.fill_between(kh, 0, 1, where=cur["valid_kh_lt_0p5"], transform=ax.get_xaxis_transform(),
                    color="#f2d7c9", alpha=0.35, lw=0)
    ax.axvline(cur["op"]["kh"], color=INK, lw=0.8)

    ax.plot(kh, cur["eta_opt"], color=BLUE, lw=2,
            label="cPTO optimal at every frequency (upper bound)")
    ax.plot(kh, cur["eta_fixed"], color=ORANGE, lw=2, ls="--",
            label=f"one fixed cPTO = {cur['c_pto_fixed_used']:.3g} m$^3$/s/Pa")
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("kh")
    ax.set_ylabel("capture width ratio  $\\eta = kP/P_{in}$")
    ax.set_title("(b) Capture width ratio", loc="left", fontsize=10)
    ax.legend(frameon=False, loc="lower center", fontsize=8)


def draw_sweep(ax, cur, state):
    """Panel (c): eta against cPTO at the selected period."""
    P = o.Params(**state["params"])
    ax.grid(True, color="#e6e5e1", lw=0.6)
    ax.set_axisbelow(True)

    c_sel = float(o.radiation_coefficients(cur["op"]["w"], P)[0])
    ax.plot(cur["sweep_c_pto"] / c_sel, cur["sweep_eta"], color=BLUE, lw=2,
            label=f"T = {cur['op']['T']:.2f} s")
    ax.plot(cur["sweep_c_pto_opt"] / c_sel, cur["sweep_eta_opt"], "o", color=BLUE, ms=6,
            mec="#fcfcfb", mew=1.5)
    ax.set_xscale("log")
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("cPTO / c  (at the selected T)")
    ax.set_ylabel("$\\eta$")
    ax.set_title("(c) Why there is an optimal cPTO", loc="left", fontsize=10)
    ax.legend(frameon=False, loc="lower center", fontsize=8)


def make_figure(cur, state):
    """Three panels from the numbers in cur = owc_views.curves(state). No pyplot."""
    with matplotlib.rc_context(STYLE):
        fig = Figure(figsize=(13, 3.9), layout="constrained")
        ax = fig.subplots(1, 3)
        draw_coefficients(ax[0], cur, state)
        draw_eta(ax[1], cur, state)
        draw_sweep(ax[2], cur, state)

        fig.suptitle("Toy OWC (piston model, isolated, regular waves) - not the Zheng et al. result",
                     fontsize=9, color="#52514e", x=0.01, ha="left")
    return fig


if __name__ == "__main__":
    matplotlib.use("Agg")
    if len(sys.argv) > 1:
        run_path = Path(sys.argv[1])
        run_json = run_path / "run.json" if run_path.is_dir() else run_path
        state = owc_views.load_run(run_json)
        fig = make_figure(owc_views.curves(state), state)
        fig.savefig(run_json.resolve().parent / "figure_from_run.png", dpi=160)
    else:
        P = o.Params()
        state = owc_views.default_state()
        state["T"] = 2 * np.pi / o.resonance_frequency_with_pto(P)
        fig = make_figure(owc_views.curves(state), state)
        out = Path(__file__).with_name("owc_toy_demo.png")
        fig.savefig(out, dpi=160)

        w_nat = o.natural_frequency(P)
        w_res = o.resonance_frequency_with_pto(P)
        c_res, _ = o.radiation_coefficients(w_res, P)
        kr = o.wavenumber(w_res, P.h)
        print(f"natural freq   w={w_nat:.3f} rad/s  T={2*np.pi/w_nat:.2f} s  kh={o.wavenumber(w_nat,P.h)*P.h:.2f}")
        print(f"PTO resonance  w={w_res:.3f} rad/s  T={2*np.pi/w_res:.2f} s  kh={kr*P.h:.2f}")
        print(f"at PTO resonance: c={c_res:.4e} m3/s/Pa, optimal cPTO = c, eta = "
              f"{float(o.capture_width_ratio(w_res, c_res, P)):.3f}")
        print(f"Pin={o.incident_power(w_res,P)/1e3:.1f} kW/m (A=1 m), P_opt={float(o.optimal_power(w_res,P))/1e3:.1f} kW, "
              f"capture width = P/Pin = {float(o.optimal_power(w_res,P)/o.incident_power(w_res,P)):.2f} m (1/k = {1/kr:.2f} m)")
        print("saved", out)
