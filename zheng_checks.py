"""python zheng_checks.py rung1|rung2|timing"""
import dataclasses
import sys
import time

import numpy as np

import owc_toy
import owc_zheng as oz

P = oz.ZhengParams()
B = oz.ZhengWallBackend()


def rung1():
    print(f"{'kh':>7} {'c_DM':>13} {'c_FFC':>13} {'c_HR':>13} {'DM-FFC':>10} {'DM-HR':>10} {'HR/DM':>8}")
    d1, d2 = [], []
    for kh in np.linspace(0.1, 7, 40):
        w = float(oz.w_from_kh(kh, P.h))
        dm, _ = oz.c_a_direct(w, P)
        ffc, hr = oz.c_far_field(w, P), oz.c_haskind(w, P)
        d1.append(abs(dm - ffc) / abs(dm))
        d2.append(abs(dm - hr) / abs(dm))
        print(f"{kh:7.3f} {dm:13.6e} {ffc:13.6e} {hr:13.6e} {d1[-1]:10.2e} {d2[-1]:10.2e} {hr/dm:8.5f}")
    print(f"max rel diff DM-FFC = {max(d1):.3e}, DM-HR = {max(d2):.3e}")


def rung2():
    grid = [(M, L) for M in (6, 8, 12, 16) for L in (10, 20, 30)]
    worst = {g: 0.0 for g in grid}
    for kh in (1.73, 2.9, 4.82):
        w = float(oz.w_from_kh(kh, P.h))
        res = {}
        for M, L in grid:
            p = dataclasses.replace(P, M=M, L=L)
            c, a = oz.c_a_direct(w, p)
            q = abs(oz.excitation_flow_complex(w, p, np.pi / 2))
            eta = float(owc_toy.capture_width_ratio(w, owc_toy.optimal_c_pto(w, p, backend=B), p, backend=B))
            res[(M, L)] = np.array([q, c, a, eta])
        ref = res[(16, 30)]
        print(f"\nkh={kh}\n{'M':>3} {'L':>3} {'|Qe|':>12} {'c':>12} {'a':>12} {'eta_opt':>10}  rel change vs (16,30): Qe, c, a, eta")
        for g in grid:
            r = np.abs(res[g] - ref) / np.abs(ref)
            worst[g] = max(worst[g], r.max())
            print(f"{g[0]:3d} {g[1]:3d} {res[g][0]:12.6e} {res[g][1]:12.6e} {res[g][2]:12.6e} {res[g][3]:10.6f}  "
                  + " ".join(f"{x:9.2e}" for x in r))
    ok = [g for g in grid if worst[g] < 1e-4 and g != (16, 30)]
    ok.sort(key=lambda g: (g[0] + 1) * (g[1] + 1))
    print("\nsmallest (M, L) with all changes < 1e-4 vs (16,30):", ok[0] if ok else "none (other than reference)")
    print("worst change per (M,L):", {g: f"{v:.1e}" for g, v in worst.items()})


def timing():
    w = oz.w_from_kh(np.linspace(0.05, 7, 200), P.h)
    oz._factor.cache_clear()
    t = time.perf_counter()
    B.coefficients(w, P)
    B.excitation(w, P)
    dt = time.perf_counter() - t
    print(f"200 frequencies (M=12, L=20): {dt:.2f} s total, {dt/200*1e3:.1f} ms per frequency")


# ---------------------------------------------------------------- rungs 4-6 (reports, no targets)
from scipy.optimize import brentq, minimize_scalar

H = P.h
_cache = {}


def mk(Rh=0.5, th=0.1, dh=0.2, beta=np.pi / 2, V0_uses="R"):
    return dataclasses.replace(P, R=Rh * H, Ri=(Rh - th) * H, d=dh * H, beta=beta, V0_uses=V0_uses)


def ev(kh, p):
    """(c, a, |Qe|) at kh, cached; c, a and Qe share one factorisation via oz._factor's cache."""
    key = (round(float(kh), 12), p)
    if key not in _cache:
        w = float(oz.w_from_kh(kh, H))
        c, a = oz.c_a_direct(w, p)
        _cache[key] = (c, a, abs(oz.excitation_flow_complex(w, p, p.beta)))
    return _cache[key]


class _CB:
    """owc_toy Backend view over the cache (kh recovered from w)."""
    name = "cached zheng"

    def _kh(self, w):
        return float(owc_toy.wavenumber(w, H)) * H

    def coefficients(self, w, p):
        return ev(self._kh(w), p)[:2]

    def excitation(self, w, p, beta=None):
        return ev(self._kh(w), p)[2]


def feat(kh, p):
    """Dimensionless Qbar, cbar, f = (a + aPTO) bar, optimal cPTO bar, and eta at optimal cPTO."""
    w = float(oz.w_from_kh(kh, H))
    c, a, q = ev(kh, p)
    s = p.rho * np.sqrt(owc_toy.G / H) / H
    cb = _CB()
    cp = float(owc_toy.optimal_c_pto(w, p, backend=cb))
    return dict(Q=np.sqrt(owc_toy.G / H) * q / (p.A * H * owc_toy.G), c=s * c, a=s * a,
                f=s * (a + float(owc_toy.a_pto(w, p))), cpto=s * cp,
                eta=float(owc_toy.capture_width_ratio(w, cp, p, backend=cb)))


def F(key, p):
    return lambda kh: feat(kh, p)[key]


def peaks(fn, grid, tol=1e-4):
    """Refined interior local maxima of fn on grid -> [(kh, value)]."""
    y = np.array([fn(k) for k in grid])
    out = []
    for i in range(1, len(grid) - 1):
        if y[i] > y[i - 1] and y[i] >= y[i + 1]:
            r = minimize_scalar(lambda k: -fn(k), bounds=(grid[i - 1], grid[i + 1]), method="bounded",
                                options=dict(xatol=tol))
            out.append((r.x, -r.fun))
    return out


def resonances(p, grid):
    """Sign changes of a + aPTO, refined: [(kh, |f| at root, |f| bracket sum)]; a pole jump keeps |f| large."""
    f = F("f", p)
    y = np.array([f(k) for k in grid])
    out = []
    for i in range(len(grid) - 1):
        if y[i] * y[i + 1] < 0:
            r = brentq(f, grid[i], grid[i + 1], xtol=1e-6)
            out.append((r, abs(f(r)), abs(y[i]) + abs(y[i + 1])))
    return out


def grid_with(lo, hi, n, fine=None):
    g = np.linspace(lo, hi, n)
    return np.union1d(g, np.linspace(*fine)) if fine else g


def _best(pk):
    return max(pk, key=lambda t: t[1]) if pk else (np.nan, np.nan)


def rung4():
    t0 = time.perf_counter()
    p = mk()
    g150 = grid_with(0.5, 6.5, 150, (4.6, 5.2, 31))
    rows = []

    print("== Qbar peaks on [0.5, 6.5] (150-pt grid + 31 fine pts in [4.6,5.2], refined)")
    pk = peaks(F("Q", p), g150)
    for k, v in pk:
        print(f"  kh={k:.4f} Qbar={v:.5f}")
    near = lambda x0: min(pk, key=lambda t: abs(t[0] - x0)) if pk else (np.nan, np.nan)
    rows += [("Qe peak 1 (kh)", 1.73, near(1.73)[0]), ("Qe peak 2 (kh)", 4.82, near(4.82)[0])]

    print("== PTO resonances a + aPTO = 0")
    rs = resonances(p, g150)
    for k, res, sc in rs:
        print(f"  kh={k:.4f} |f| at root={res:.2e} (bracket |f| sum {sc:.2e}){'  <-- POLE-LIKE' if res > 1e-3 * sc else ''}")
    for pap in (1.86, 2.90, 4.90):
        rows.append((f"PTO res (kh) near {pap}", pap, min(rs, key=lambda t: abs(t[0] - pap))[0] if rs else np.nan))

    print("== eta (optimal cPTO) on 1.6<kh<3.1 (31 pts)")
    g = np.linspace(1.6, 3.1, 31)
    e = np.array([F("eta", p)(k) for k in g])
    print(f"  min={e.min():.4f} at kh={g[e.argmin()]:.3f}; max={e.max():.4f} at kh={g[e.argmax()]:.3f}")
    rows += [("eta min [1.6,3.1]", 2.0, e.min()), ("eta max [1.6,3.1]", 2.3, e.max())]
    pc = _best(peaks(F("c", p), np.linspace(1.2, 2.6, 29)))
    print(f"  peak cbar in [1.2,2.6]: kh={pc[0]:.4f} cbar={pc[1]:.4f}")
    rows += [("peak cbar", 3.3, pc[1]), ("peak cbar (kh)", 1.8, pc[0])]
    gs = np.linspace(4.6, 5.2, 31)
    es = _best(peaks(F("eta", p), gs)) if peaks(F("eta", p), gs) else max((F("eta", p)(k), k) for k in gs)[::-1]
    print(f"  max eta on [4.6,5.2]: {es[1]:.4f} at kh={es[0]:.4f}")
    rows.append(("eta max [4.6,5.2]", 2.9, es[1]))

    print("== R/h sweep, (R-Ri)/h=0.1, d/h=0.2, beta=pi/2 (70-pt grid 0.3..6.5 + fine 4.6..5.2)")
    print(f"{'R/h':>5} {'res1':>8} {'res2':>8} {'dkh':>7} {'eta1':>7} {'eta2':>7}")
    sw = []
    for Rh in (0.3, 0.4, 0.5, 0.6, 0.7):
        q = mk(Rh)
        r = resonances(q, grid_with(0.3, 6.5, 70, (4.6, 5.2, 31)))
        if len(r) >= 2:
            k1, k2 = r[0][0], r[1][0]
            sw.append((Rh, k1, k2, k2 - k1))
            print(f"{Rh:5.1f} {k1:8.4f} {k2:8.4f} {k2-k1:7.4f} {F('eta', q)(k1):7.3f} {F('eta', q)(k2):7.3f}   all roots: {[round(x[0], 3) for x in r]}")
        else:
            print(f"{Rh:5.1f} fewer than 2 resonances: {[round(x[0], 3) for x in r]}")
    if len(sw) >= 2:
        rows += [(f"dkh R/h={sw[0][0]}", 1.19, sw[0][3]), (f"dkh R/h={sw[-1][0]}", 0.56, sw[-1][3])]

    print("== V0 = pi Ri^2 h (default geometry)")
    q = mk(V0_uses="Ri")
    r2 = resonances(q, g150)
    print("  resonances:", [round(x[0], 4) for x in r2], " baseline:", [round(x[0], 4) for x in rs])
    for (k, _, _), (k0, _, _) in zip(r2, rs):
        print(f"  shift {k0:.4f} -> {k:.4f}: {k-k0:+.4f}")
    e2 = np.array([F("eta", q)(k) for k in g])
    print(f"  eta [1.6,3.1]: min={e2.min():.4f} max={e2.max():.4f} (baseline {e.min():.4f}, {e.max():.4f})")

    print("\n== SUMMARY: feature | paper | this solver | difference")
    for n, pa, v in rows:
        print(f"{n:<26} | {pa:>6} | {v:10.4f} | {v-pa:+.4f}")
    print(f"\nrung4 time {time.perf_counter()-t0:.0f} s")


def rung5():
    t0 = time.perf_counter()
    xg, wg = np.polynomial.legendre.leggauss(48)
    betas = 0.5 * np.pi * (xg + 1)
    wg = 0.5 * np.pi * wg
    sub = (np.pi / 6, np.pi / 4, np.pi / 3, np.pi / 2)
    khs = [0.5, 0.9, 1.3, 1.73, 1.86, 2.3, 2.9, 3.5, 4.0, 4.6, 4.85, 6.5]
    print(f"{'kh':>5} {'<eta_max>':>10} | " + " | ".join(f"b={b/np.pi:.3f}pi: eta_opt  bound  ratio" for b in sub))
    worst, over = 0.0, []
    for kh in khs:
        w = float(oz.w_from_kh(kh, H))
        sol = oz.solve(w, P, betas)
        q2 = np.array([abs(oz._Q(sol, x, P)) ** 2 for x in sol["x_S"]])
        mean_q2 = np.sum(wg * q2) / np.pi
        c, _ = oz.c_a_direct(w, P)
        mean_eta = float(owc_toy.wavenumber(w, H)) * mean_q2 / (8 * c * float(owc_toy.incident_power(w, P)))
        cells = []
        for b in sub:
            p = dataclasses.replace(P, beta=b)
            eo = float(owc_toy.capture_width_ratio(w, owc_toy.optimal_c_pto(w, p, backend=B), p, backend=B))
            bound = 2 * abs(oz.excitation_flow_complex(w, p, b)) ** 2 / mean_q2
            worst = max(worst, eo / bound)
            cells.append(f"{eo:8.4f} {bound:7.4f} {eo/bound:7.4f}")
            if eo > 2:
                over.append((kh, b, eo, bound))
        print(f"{kh:5.2f} {mean_eta:10.5f} | " + " | ".join(cells))
    print(f"\nmax eta_opt/bound = {worst:.6f} (must be <= 1)")
    print("points with eta_opt > 2:", [(kh, round(b / np.pi, 3), round(e, 4), f"bound {bd:.4f}", "within bound" if e <= bd else "VIOLATES") for kh, b, e, bd in over] or "none")
    print(f"\nrung5 time {time.perf_counter()-t0:.0f} s")


def rung6():
    t0 = time.perf_counter()
    print("== beta dependence of Qbar (Fig 5a: weak)")
    bs = (0, np.pi / 6, np.pi / 4, np.pi / 3, np.pi / 2)
    for kh in (1.73, 2.9, 4.82):
        s = oz.solve(float(oz.w_from_kh(kh, H)), P, bs)
        q = np.array([abs(oz._Q(s, x, P)) for x in s["x_S"]]) * np.sqrt(owc_toy.G / H) / (H * owc_toy.G)
        print(f"  kh={kh}: Qbar(beta=0,30,45,60,90deg) = {np.round(q, 5)}  max/min = {q.max()/q.min():.4f}")

    def summary(p, n=60):
        r = resonances(p, grid_with(0.5, 6.5, n, (4.6, 5.2, 31)))
        e = np.array([F("eta", p)(k) for k in np.linspace(1.6, 3.1, 16)])
        return r, e, _best(peaks(F("c", p), np.linspace(0.8, 3.4, 27)))

    print("\n== d/h sweep (R/h 0.5, (R-Ri)/h 0.1); peak cbar searched in kh [0.8,3.4]")
    print(f"{'d/h':>5} {'res1':>8} {'eta@res1':>9} {'cbar_pk':>8} {'@kh':>6}  eta[1.6,3.1] min/max  all roots")
    for dh in (0.3, 0.2, 0.1, 0.05, 0.02):
        p = mk(dh=dh)
        r, e, pc = summary(p)
        k1 = r[0][0] if r else np.nan
        print(f"{dh:5.2f} {k1:8.4f} {F('eta', p)(k1) if r else np.nan:9.3f} {pc[1]:8.3f} {pc[0]:6.3f}  {e.min():.3f}/{e.max():.3f}  {[round(x[0], 3) for x in r]}")

    print("\n== thin-wall sweep (R/h 0.5, d/h 0.2)")
    print(f"{'t/h':>5} {'res1':>8} {'res2':>8} {'cbar_pk':>8} {'@kh':>6}  eta[1.6,3.1] min/max")
    for th in (0.1, 0.05, 0.02, 0.01):
        r, e, pc = summary(mk(th=th))
        k = [x[0] for x in r[:2]] + [np.nan, np.nan]
        print(f"{th:5.2f} {k[0]:8.4f} {k[1]:8.4f} {pc[1]:8.3f} {pc[0]:6.3f}  {e.min():.3f}/{e.max():.3f}")
    f = oz._factor(float(oz.w_from_kh(2.0, H)), mk(th=0.01))
    d = np.abs(np.diag(np.triu(f["lu"][0])))
    print(f"\nthin 0.01, kh=2, N={f['N']}: |U_ii| max/min = {d.max()/d.min():.3e} (cond lower-bound proxy; "
          "numpy.linalg.cond skipped because _factor keeps only the LU and owc_zheng.py must not change)")
    print(f"\nrung6 time {time.perf_counter()-t0:.0f} s")


def _root_in(p, lo, hi, n=8):
    """The single a+aPTO root in [lo, hi] (coarse n-pt bracket, then brentq); nan if none."""
    r = resonances(p, np.linspace(lo, hi, n))
    return r[0][0] if r else np.nan


def rung4b():
    """Targeted (windowed) re-evaluation of the rung-4 features plus the V0 switch, for a loaded machine.
    Same quantities as rung4, found by refining inside windows around the known features instead of full scans."""
    t0 = time.perf_counter()
    p, rows = mk(), []
    q1 = max(peaks(F("Q", p), np.linspace(1.5, 2.0, 5)))
    q2 = max(peaks(F("Q", p), np.linspace(4.7, 4.95, 9)))
    print(f"Qbar peaks: kh={q1[0]:.4f} ({q1[1]:.4f}), kh={q2[0]:.4f} ({q2[1]:.4f})")
    rows += [("Qe peak 1 (kh)", 1.73, q1[0]), ("Qe peak 2 (kh)", 4.82, q2[0])]
    r = [_root_in(p, 1.7, 2.1), _root_in(p, 2.7, 3.1), _root_in(p, 4.8, 4.95, 16)]
    print("PTO resonances:", np.round(r, 4))
    rows += [(f"PTO res (kh) near {x}", x, v) for x, v in zip((1.86, 2.90, 4.90), r)]
    g = np.linspace(1.6, 3.1, 16)
    e = np.array([F("eta", p)(k) for k in g])
    print(f"eta [1.6,3.1] (16 pts): min={e.min():.4f} at {g[e.argmin()]:.2f}, max={e.max():.4f} at {g[e.argmax()]:.2f}")
    rows += [("eta min [1.6,3.1]", 2.0, e.min()), ("eta max [1.6,3.1]", 2.3, e.max())]
    pc = _best(peaks(F("c", p), np.linspace(1.4, 2.2, 9)))
    print(f"peak cbar: kh={pc[0]:.4f} cbar={pc[1]:.4f}")
    rows += [("peak cbar", 3.3, pc[1]), ("peak cbar (kh)", 1.8, pc[0])]
    es = _best(peaks(F("eta", p), np.linspace(4.7, 4.95, 11)))
    print(f"max eta on [4.6,5.2]: {es[1]:.4f} at kh={es[0]:.4f}")
    rows.append(("eta max [4.6,5.2]", 2.9, es[1]))
    a = (_root_in(mk(0.3), 2.3, 2.7), _root_in(mk(0.3), 3.5, 4.0), _root_in(mk(0.7), 1.3, 1.7), _root_in(mk(0.7), 1.9, 2.4))
    print(f"R/h=0.3 roots {a[0]:.4f} {a[1]:.4f} dkh={a[1]-a[0]:.4f}; R/h=0.7 roots {a[2]:.4f} {a[3]:.4f} dkh={a[3]-a[2]:.4f}")
    rows += [("dkh R/h=0.3", 1.19, a[1] - a[0]), ("dkh R/h=0.7", 0.56, a[3] - a[2])]
    print("== V0 = pi Ri^2 h (default geometry)")
    q = mk(V0_uses="Ri")
    r2 = [_root_in(q, 1.7, 2.3), _root_in(q, 3.3, 4.5, 13), _root_in(q, 4.5, 5.0, 24)]
    print("  resonances:", np.round(r2, 4), " baseline:", np.round(r, 4), " shift:", np.round(np.array(r2) - r, 4))
    e2 = np.array([F("eta", q)(k) for k in g])
    print(f"  eta [1.6,3.1]: min={e2.min():.4f} max={e2.max():.4f} (baseline {e.min():.4f}, {e.max():.4f})")
    print("\n== SUMMARY: feature | paper | this solver | difference")
    for n, pa, v in rows:
        print(f"{n:<26} | {pa:>6} | {v:10.4f} | {v-pa:+.4f}")
    print(f"\nrung4b time {time.perf_counter()-t0:.0f} s")


def rung6b():
    """Thin-wall rows for (R-Ri)/h = 0.02, 0.01 with a lighter scan (loaded machine)."""
    t0 = time.perf_counter()
    for th in (0.02, 0.01):
        p = mk(th=th)
        r = resonances(p, grid_with(1.2, 4.0, 36))
        e = np.array([F("eta", p)(k) for k in np.linspace(1.6, 3.1, 8)])
        pc = _best(peaks(F("c", p), np.linspace(1.2, 2.4, 13)))
        k = [x[0] for x in r[:2]] + [np.nan, np.nan]
        print(f"{th:5.2f} {k[0]:8.4f} {k[1]:8.4f} {pc[1]:8.3f} {pc[0]:6.3f}  {e.min():.3f}/{e.max():.3f}  (36-pt scan of 1.2..4.0, 8-pt eta)")
    f = oz._factor(float(oz.w_from_kh(2.0, H)), mk(th=0.01))
    d = np.abs(np.diag(np.triu(f["lu"][0])))
    print(f"\nthin 0.01, kh=2, N={f['N']}: |U_ii| max/min = {d.max()/d.min():.3e} (cond lower-bound proxy; "
          "numpy.linalg.cond skipped because _factor keeps only the LU and owc_zheng.py must not change)")
    print(f"\nrung6b time {time.perf_counter()-t0:.0f} s")


if __name__ == "__main__":
    {"rung1": rung1, "rung2": rung2, "timing": timing, "rung4": rung4, "rung5": rung5, "rung6": rung6,
     "rung4b": rung4b, "rung6b": rung6b}[sys.argv[1]]()
