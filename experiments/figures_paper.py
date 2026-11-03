"""Figures of the paper, as vector PDFs.

    python experiments/figures_paper.py --results results/night_2026-10-20 \\
        --source-scan results/source_scan --out figures

Without --results / --source-scan only the figures that need no results are made.
fig_failure_end_state.pdf comes from figure_night.py; experiments/paper_figures.sh
makes all of them, and REPRODUCE.md maps them to the paper.

1. fig_counterexample: the 2-d counterexample (needs no results).
2. fig_tangent_survival: closed-loop exponents nearest the source's positive and
   zero exponents vs the largest CLE, in transversely stable runs.
3. fig_predictors: median valid time vs training error, largest CLE and lambda_perp.
4. fig_gap: lambda_perp vs the largest CLE.
5. fig_opening: two reservoirs alike in training, opposite in free run (needs no results;
   recomputes lambda_perp over 2000 time units, a few minutes).
6. fig_overview: schematic of training and closing the loop (needs no results).
7. fig_sources: the 19-system scan (needs --source-scan).
8. fig_family: the exact chaotic family, lambda_perp against the conditional exponents (needs no results).
9. fig_bubbling: bursts at a negative lambda_perp in the same family (needs no results).
"""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")  # before numpy: same BLAS threading as the scans

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm
from scipy.stats import spearmanr

from reservoir_sync.plotting import GAMMA_COLORS, GRID, INK, MUTED, col, style, use_paper_style
from reservoir_sync.plotting import load as load_records

SCANS = {"Lorenz": "lorenz_long.jsonl", "Rössler": "rossler_long.jsonl"}
STABLE = -0.05

use_paper_style()


def load(path):
    return load_records(path, keep=lambda r: r["lambda_perp_driven"] is not None)


def within_gamma_rho(x, y, gamma):
    return float(np.mean([spearmanr(x[gamma == g], y[gamma == g])[0] for g in np.unique(gamma)]))


def scatter_by_gamma(ax, x, y, gamma):
    for g, c in GAMMA_COLORS.items():
        m = gamma == g
        ax.scatter(x[m], y[m], s=7, color=c, lw=0.2, edgecolor="white", label=f"γ = {g:g}")


def fig_overview(out):
    # the two phases, with the attractors of the two Rossler reservoirs of fig_opening
    from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

    from reservoir_sync.closed_loop import run_autonomous
    from reservoir_sync.driven import drive, settle_source
    from reservoir_sync.readout import fit_readout
    from reservoir_sync.reservoirs import random_reservoir
    from reservoir_sync.sources import SOURCES

    source = SOURCES["rossler"]()
    dt, n_wash, n_train, n_pred = 0.01, 2000, 10000, 30000

    def trained(seed):
        res = random_reservoir(200, source.dim, "tanh", 0.5, 0.05, 0.5, 5.0, None, seed)
        s0 = settle_source(source, dt, 50.0, seed=seed)
        full = drive(source, res, s0, np.zeros(res.n), dt, n_wash + n_train)
        train = full[n_wash:]
        N = fit_readout(train.R, train.S, 1e-6)
        return train, train.R @ N, run_autonomous(res, N, train.R[-1], dt, n_pred) @ N

    train, decoded, free_stable = trained(1)
    free_unstable = trained(21)[2]
    W, H = 6.5, 3.3
    blue, orange = GAMMA_COLORS[1.0], GAMMA_COLORS[5.0]
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, W), ylim=(0, H))
    ax.axis("off")
    S = train.S[::2]
    lo, hi = S.min(axis=0), S.max(axis=0)

    def attractor(cx, cy, size, curves, title=None, title_color=INK):
        a = fig.add_axes([(cx - size / 2) / W, (cy - size / 2) / H, size / W, size / H], projection="3d")
        for X, col, lw, alpha in curves:
            X = X[np.all(np.isfinite(X), axis=1)]
            X = X[np.all((X > lo - 0.6 * (hi - lo)) & (X < hi + 0.6 * (hi - lo)), axis=1)]
            a.plot(X[:, 0], X[:, 1], X[:, 2], color=col, lw=lw, alpha=alpha)
        a.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), zlim=(lo[2], hi[2]))
        a.view_init(elev=22, azim=-60)
        a.set_axis_off()
        a.patch.set_alpha(0)
        if title:
            label(cx, cy + size / 2 - 0.12, title, fontsize=7.5, color=title_color)

    def arrow(points, color=INK, ls="-", lw=1.0):
        if len(points) > 2:
            ax.plot(*zip(*points[:-1]), color=color, ls=ls, lw=lw, solid_capstyle="butt")
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>", mutation_scale=8,
                                     color=color, ls=ls, lw=lw, shrinkA=0, shrinkB=0))

    def surrogate(cx, cy, r=0.36):
        ax.add_patch(Circle((cx, cy), r, fc="#f1f0ec", ec=MUTED, lw=0.8))
        rng = np.random.default_rng(3)
        angles = np.arange(7) * 2 * np.pi / 7 + 0.3
        pts = np.c_[cx + 0.24 * np.cos(angles), cy + 0.24 * np.sin(angles)]
        for i, j in rng.integers(0, 7, (11, 2)):
            if i != j:
                ax.plot(*zip(pts[i], pts[j]), color=MUTED, lw=0.4)
        ax.scatter(*pts.T, s=12, fc="white", ec=INK, lw=0.6, zorder=3)

    def label(x, y, text, **kw):
        ax.text(x, y, text, ha=kw.pop("ha", "center"), va=kw.pop("va", "center"), **kw)

    def panel(y0, y1, title):
        ax.add_patch(FancyBboxPatch((0.08, y0), W - 0.16, y1 - y0, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc="none", ec=GRID, lw=0.8))
        label(0.18, y1 - 0.13, title, ha="left", fontweight="bold", fontsize=8)

    xs, xr, xo = 1.15, 3.25, 5.35  # columns: source, surrogate, output
    y1, y2 = 2.35, 0.78  # row centres
    panel(1.68, 3.24, "1  Listening and fitting: the source drives the surrogate")
    panel(0.06, 1.6, "2  Autonomous: the decoded output replaces the source")

    # row 1
    attractor(xs, y1 - 0.02, 1.45, [(S, INK, 0.45, 0.9)])
    label(xs, y1 - 0.66, r"source $\dot{\mathbf{s}}=\mathbf{g}(\mathbf{s})$", fontsize=7.5)
    arrow([(xs + 0.62, y1), (xr - 0.42, y1)])
    label((xs + xr) / 2 + 0.08, y1 + 0.12, r"$\mathbf{s}(t)$", fontsize=7.5)
    surrogate(xr, y1)
    label(xr, y1 - 0.53, r"surrogate $\dot{\mathbf{r}}=\mathbf{f}(\mathbf{r},\mathbf{s})$", fontsize=7.5)
    arrow([(xr + 0.42, y1), (xo - 0.62, y1)], ls="--")
    label((xr + xo) / 2 - 0.08, y1 + 0.12, r"fit $\boldsymbol{\psi}$", fontsize=7.5)
    attractor(xo, y1 - 0.02, 1.45, [(S, GRID, 1.6, 1.0), (decoded[::2], blue, 0.45, 0.9)])
    label(xo, y1 - 0.66, r"decoded $\hat{\mathbf{s}}=\boldsymbol{\psi}(\mathbf{r})\approx\mathbf{s}$", fontsize=7.5)

    # row 2
    attractor(xs, y2 - 0.05, 1.3, [(S, GRID, 0.45, 1.0)])
    label(xs, y2 - 0.6, "source disconnected", fontsize=7.5, color=MUTED)
    surrogate(xr, y2 - 0.05)
    xl, yb = xr + 0.62, y2 - 0.5
    arrow([(xr + 0.38, y2 - 0.05), (xl, y2 - 0.05), (xl, yb), (xr - 0.62, yb), (xr - 0.62, y2 - 0.05),
           (xr - 0.38, y2 - 0.05)], lw=1.1)
    label(xr, yb - 0.11, r"$\boldsymbol{\psi}(\mathbf{r})$ fed back as input", fontsize=7.5)
    label(xr, y2 + 0.48, r"$\dot{\mathbf{r}}=\mathbf{f}(\mathbf{r},\boldsymbol{\psi}(\mathbf{r}))$", fontsize=7.5)
    arrow([(xl, y2 - 0.05), (xo - 0.95, y2 - 0.05)])
    attractor(xo - 0.5, y2 - 0.12, 1.2, [(S, GRID, 1.6, 1.0), (free_stable[::2], blue, 0.45, 0.9)],
              title="stays on the attractor", title_color=blue)
    attractor(xo + 0.62, y2 - 0.12, 1.2, [(S, GRID, 1.6, 1.0), (free_unstable[::2], orange, 0.45, 0.9)],
              title="leaves it", title_color=orange)
    fig.savefig(out / "fig_overview.pdf")


def opening_diagnostics(source, res, N, train, test, dt, t_lyap, k=10, n_starts=20):
    """The numbers the paper quotes for the opening example, computed as in
    reservoir_sync.experiment.run with the scan's settings (t_test = 300, so 20 free
    runs of 150 time units): training error, largest CLE, lambda_perp (field
    lambda_perp_driven) and the median valid time in Lyapunov times (uncentred norm,
    closed_loop.valid_time)."""
    from reservoir_sync.closed_loop import valid_times
    from reservoir_sync.lyapunov import (closed_loop_exponents_driven, conditional_exponents, extra_exponents,
                                         source_exponents)
    from reservoir_sync.readout import nrmse

    n = int(round(t_lyap / dt))
    s_sync, r_sync = train.S[-1], train.R[-1]
    lam_src = source_exponents(source, s_sync, dt, n)
    lam_cle = conditional_exponents(source, res, s_sync, r_sync, dt, n, k)
    lam_cl = closed_loop_exponents_driven(source, res, N, s_sync, r_sync, dt, n, k)
    n_pred = (len(test.S) - 1) // 2  # t_pred = t_test / 2, run()'s default
    starts = np.linspace(0, len(test.S) - n_pred - 1, n_starts).astype(int)
    vts = valid_times(res, N, test, starts, n_pred) * float(lam_src[0])
    return {"train_nrmse": nrmse(train.S, train.R @ N), "cle_max": float(lam_cle[0]),
            "perp": float(extra_exponents(lam_cl, lam_src)[0]), "valid_median_lyap": float(np.median(vts))}


# the values the paper's text quotes, printed next to the recomputed ones
OPENING_PAPER = {1: "5.75e-5, -2.97, -1.00, 4.8", 21: "5.76e-5, -2.98, +0.25, 0.5"}


def fig_opening(out, t_lyap=2000.0):
    # two runs of the Rossler scan with the same hyperparameters, chosen to match in
    # training error and largest CLE, with opposite lambda_perp; lambda_perp is
    # recomputed here over t_lyap, the exponent window of that scan (Sec. 5)
    from reservoir_sync.closed_loop import run_autonomous
    from reservoir_sync.driven import drive, settle_source
    from reservoir_sync.readout import fit_readout
    from reservoir_sync.reservoirs import random_reservoir
    from reservoir_sync.sources import SOURCES

    source = SOURCES["rossler"]()
    dt, n_wash, n_train, n_pred = 0.01, 2000, 10000, 30000
    fig, axes = plt.subplots(2, 2, figsize=(6.5, 3.6), constrained_layout=True,
                             width_ratios=[2.4, 1], sharex="col")
    runs = [(1, GAMMA_COLORS[1.0], "(a) λ⊥ = {}: the free run follows the source"),
            (21, GAMMA_COLORS[5.0], "(b) λ⊥ = {}: the free run leaves it")]
    for (seed, color, title), (a, b) in zip(runs, axes):
        res = random_reservoir(200, source.dim, "tanh", 0.5, 0.05, 0.5, 5.0, None, seed)
        s0 = settle_source(source, dt, 50.0, seed=seed)
        full = drive(source, res, s0, np.zeros(res.n), dt, n_wash + n_train + n_pred)
        train = full[n_wash : n_wash + n_train + 1]
        N = fit_readout(train.R, train.S, 1e-6)
        test = full[n_wash + n_train :]
        d = opening_diagnostics(source, res, N, train, test, dt, t_lyap)
        title = title.format(f"{d['perp']:+.2f}".replace("-", "−"))
        print(f"fig_opening seed {seed}: training error {d['train_nrmse']:.3g}, largest CLE {d['cle_max']:+.3f},"
              f" lambda_perp {d['perp']:+.3f}, median valid time {d['valid_median_lyap']:.2f} Lyapunov times"
              f" (paper: {OPENING_PAPER[seed]})")
        out_free = run_autonomous(res, N, train.R[-1], dt, n_pred) @ N
        truth = full.S[n_wash + n_train :]
        t = np.arange(len(out_free)) * dt
        m = t <= 100
        a.plot(t[m], truth[: len(t)][m, 0], color=MUTED, lw=2.4, label="source")
        a.plot(t[m], out_free[m, 0], color=color, lw=1.0, label="free run")
        a.set_ylabel("$s_1$")
        a.set_ylim(-11, 18)
        a.set_title(title, loc="left", fontsize=8)
        a.legend(frameon=False, ncol=2, loc="upper left")
        b.plot(truth[:, 0], truth[:, 1], color=MUTED, lw=0.5)
        b.plot(out_free[:, 0], out_free[:, 1], color=color, lw=0.5)
        b.set_ylabel("$s_2$")
        for ax in (a, b):
            style(ax)
    axes[1, 0].set_xlabel("time since the loop was closed")
    axes[1, 1].set_xlabel("$s_1$")
    fig.savefig(out / "fig_opening.pdf")


def fig_counterexample(out):
    A = np.array([[1.0, 10.0], [-1.0, -3.0]])
    V = np.array([[-10.0], [2.0]])
    N = np.array([[0.0], [1.0]])
    J = A + V @ N.T
    t = np.linspace(0, 10, 401)
    d0 = np.array([1e-3, 0.0])
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.5, 2.4), constrained_layout=True)
    driven = [np.linalg.norm(expm(A * x) @ d0) for x in t]
    closed = [np.linalg.norm(expm(J * x) @ d0) for x in t]
    a.semilogy(t, driven, color=GAMMA_COLORS[1.0], lw=1.6, label="driven (same input)")
    a.semilogy(t, closed, color=GAMMA_COLORS[5.0], lw=1.6, label="closed loop")
    a.set_xlabel("time")
    a.set_ylabel("perturbation norm")
    a.set_title("(a) Perturbations decay when driven, grow in closed loop", loc="left", fontsize=8)
    a.legend(frameon=False)
    r_on = np.array([expm(J * x) @ np.array([0.0, 1.0]) for x in t])
    r_off = np.array([expm(J * x) @ np.array([1e-3, 1.0]) for x in t])
    b.plot(t, np.exp(-t), color=MUTED, lw=3, label="source s(t)")
    b.plot(t, r_on[:, 1], color=GAMMA_COLORS[1.0], lw=1.2, label="closed loop, on the manifold")
    b.plot(t, r_off[:, 1], color=GAMMA_COLORS[5.0], lw=1.6, label="closed loop, offset 10⁻³")
    b.set_ylim(-1.5, 1.2)
    b.set_xlabel("time")
    b.set_ylabel("decoded output Nᵀr")
    b.set_title("(b) A small offset destroys the free run", loc="left", fontsize=8)
    b.legend(frameon=False)
    for ax in (a, b):
        style(ax)
    fig.savefig(out / "fig_counterexample.pdf")


def fig_tangent_survival(data, out):
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.5), constrained_layout=True)
    for ax, (name, recs) in zip(axes, data.items()):
        stable = [r for r in recs if r["lambda_perp_driven"] < STABLE]
        cle = col(stable, lambda r: r["lyap_cle"][0])
        src = np.median([r["lyap_source"] for r in recs], axis=0)
        near = lambda r, s: min(r["lyap_closed_driven"], key=lambda c: abs(c - s))
        ax.scatter(cle, col(stable, lambda r: near(r, r["lyap_source"][0])), s=6, lw=0,
                   color=GAMMA_COLORS[1.0], label="nearest to λ₁")
        ax.scatter(cle, col(stable, lambda r: near(r, r["lyap_source"][1])), s=6, lw=0,
                   color=GAMMA_COLORS[5.0], label="nearest to 0")
        ax.axhline(src[0], color=MUTED, lw=0.8, ls="--")
        ax.axhline(0, color=MUTED, lw=0.8, ls="--")
        ax.axvline(src[2], color=INK, lw=0.8)
        ax.text(src[2], 1.02, " λ_min of the source", transform=ax.get_xaxis_transform(),
                fontsize=7, color=INK, ha="center", va="bottom")
        ax.set_xlabel("largest conditional exponent")
        ax.set_ylabel("closed-loop exponent")
        ax.set_title(f"{name} ({len(stable)} stable runs)", loc="left", pad=12)
        ax.legend(frameon=False, loc="center", bbox_to_anchor=(0.5, 0.45), ncol=2, markerscale=2.5)
        style(ax)
    fig.savefig(out / "fig_tangent_survival.pdf")


def fig_predictors(data, out):
    panels = [("training NRMSE", lambda r: r["train_nrmse"], True),
              ("largest conditional exponent", lambda r: r["lyap_cle"][0], False),
              ("λ⊥ (driven base)", lambda r: r["lambda_perp_driven"], False)]
    fig, axes = plt.subplots(2, 3, figsize=(6.5, 4.0), constrained_layout=True, sharey="row")
    for i, (name, recs) in enumerate(data.items()):
        gamma = col(recs, lambda r: r["config"]["gamma"])
        valid = col(recs, lambda r: r["valid_median_lyap"])
        for j, (label, f, logx) in enumerate(panels):
            ax = axes[i, j]
            x = col(recs, f)
            scatter_by_gamma(ax, x, valid, gamma)
            if logx:
                ax.set_xscale("log")
            ax.set_title(f"ρ = {within_gamma_rho(x, valid, gamma):+.2f}", loc="left")
            if i == 1:
                ax.set_xlabel(label)
            if j == 0:
                ax.set_ylabel(f"{name}\nmedian valid time")
            style(ax)
    axes[0, 2].legend(frameon=False, markerscale=1.5)
    fig.savefig(out / "fig_predictors.pdf")


def fig_gap(data, out):
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.7), constrained_layout=True)
    for ax, (name, recs) in zip(axes, data.items()):
        gamma = col(recs, lambda r: r["config"]["gamma"])
        cle = col(recs, lambda r: r["lyap_cle"][0])
        perp = col(recs, lambda r: r["lambda_perp_driven"])
        scatter_by_gamma(ax, cle, perp, gamma)
        lim = [cle.min(), 0]
        ax.plot(lim, lim, color=MUTED, lw=0.8, ls="--", label="λ⊥ = largest CLE")
        ax.axhline(0, color=INK, lw=0.6)
        ax.set_xlabel("largest conditional exponent")
        ax.set_ylabel("λ⊥ (driven base)")
        ax.set_title(f"{name}: above the line in {int((perp > cle).sum())}/{len(perp)}", loc="left")
        ax.legend(frameon=False, markerscale=1.5)
        style(ax)
    fig.savefig(out / "fig_gap.pdf")


def fig_sources(scan, out):
    read = lambda arm: {r["source"]: r for r in csv.DictReader((scan / f"sources_{arm}.csv").open())}
    base, offset = read("lambda"), read("lambdaoff")
    names = {"rossler": "Rössler", "lu_chen": "Lu–Chen", "lorenz": "Lorenz", "thomas": "Thomas", "aizawa": "Aizawa"}
    blue, orange = GAMMA_COLORS[1.0], GAMMA_COLORS[5.0]
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.5, 2.6), constrained_layout=True)
    rho = sorted(float(r["rho_perp"]) for r in base.values())
    a.scatter(rho, np.arange(len(rho)), s=12, color=blue, lw=0)
    a.axvline(0, color=INK, lw=0.6)
    a.set_xlim(-1, 0.05)
    a.set_yticks([])
    a.set_xlabel("ρ(λ⊥, valid time)")
    a.set_ylabel("the 19 systems, sorted")
    a.set_title("(a) λ⊥ predicts in every system", loc="left", fontsize=8)
    rows = list(base.values())
    x, y = col(rows, lambda r: r["ratio"]), col(rows, lambda r: r["unstable"])
    lo, hi = col(rows, lambda r: r["unstable_lo"]), col(rows, lambda r: r["unstable_hi"])
    b.errorbar(x, y, yerr=[y - lo, hi - y], fmt="o", ms=3, color=blue, ecolor=GRID, elinewidth=1)
    b.set_xscale("log")
    b.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5], ["0.02", "0.05", "0.1", "0.2", "0.5"])
    b.minorticks_off()
    b.set_ylim(0, 1)
    b.set_xlabel("λ₁ / |λ_min|")
    b.set_ylabel("unstable fraction")
    b.set_title("(b) The source does not set it", loc="left", fontsize=8)
    for key, shift in [("rossler", 0.05), ("lu_chen", -0.07), ("thomas", -0.08), ("lorenz", -0.07)]:
        r = base[key]
        b.text(float(r["ratio"]), float(r["unstable"]) + shift, names[key], fontsize=6.5, color=MUTED)
    u, v = col(rows, lambda r: r["unstable"]), col(rows, lambda r: offset[r["source"]]["unstable"])
    c.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls="--")
    c.scatter(u, v, s=12, color=orange, lw=0)
    c.set(xlim=(0, 1), ylim=(0, 1))
    c.set_xlabel("unstable fraction, no offset")
    c.set_ylabel("with constant offset")
    c.set_title("(c) An offset stabilizes", loc="left", fontsize=8)
    for key, dy in [("lorenz", 0.03), ("thomas", -0.07)]:
        c.text(u[list(base).index(key)] + 0.02, v[list(base).index(key)] + dy, names[key], fontsize=6.5, color=MUTED)
    for ax in (a, b, c):
        style(ax)
    fig.savefig(out / "fig_sources.pdf")


# --- the exact chaotic family of Sec. 4 (Lorenz source, phi(s) = (s, h(s_3)), N^T = (I, 0)) ---

def lorenz(s):
    return np.array([10.0 * (s[1] - s[0]), s[0] * (28.0 - s[2]) - s[1], s[0] * s[1] - 8 / 3 * s[2]])


class Family:
    """y' = g(s) - k(y - s) + c (z - h(s3)),  z' = h'(s3) g3(s) + D.(y - s) + E (z - h(s3)).

    h' = a0 sech^2((s3 - 27)/4), c = (0, 0, -1). In closed loop chi = z - h(y3) obeys
    chi' = (E + h'(y3)) chi, so lambda_perp = <E + h'>.
    """

    def __init__(self, E=-1.0, a0=3.0, k=5.0, D=0.3):
        self.E, self.a0, self.k = E, a0, k
        self.c = np.array([0.0, 0.0, -1.0])
        self.D = np.array([0.0, 0.0, D])
        A = np.zeros((4, 4))
        A[:3, :3], A[:3, 3], A[3, :3], A[3, 3] = -k * np.eye(3), self.c, self.D, E
        self.A = A  # Jacobian of the driven surrogate: constant, so the CLEs are its eigenvalues

    def h(self, s3):
        return self.a0 * 4.0 * np.tanh((s3 - 27.0) / 4.0)

    def dh(self, s3):
        return self.a0 / np.cosh((s3 - 27.0) / 4.0) ** 2

    def rate(self, s3):
        return self.E + self.dh(s3)

    def f(self, x, s):
        y, z = x[:3], x[3]
        gs, hs = lorenz(s), self.h(s[2])
        return np.concatenate([gs - self.k * (y - s) + self.c * (z - hs),
                               [self.dh(s[2]) * gs[2] + self.D @ (y - s) + self.E * (z - hs)]])


def rk4(fun, x, dt):
    k1 = fun(x); k2 = fun(x + dt / 2 * k1); k3 = fun(x + dt / 2 * k2); k4 = fun(x + dt * k3)
    return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def lorenz_orbit(T, dt=0.002, seed=0, T_settle=50.0):
    s = np.array([1.0, 1.0, 20.0]) + np.random.default_rng(seed).normal(size=3)
    for _ in range(int(T_settle / dt)):
        s = rk4(lorenz, s, dt)
    out = np.empty((int(T / dt), 3))
    for i in range(len(out)):
        s = rk4(lorenz, s, dt)
        out[i] = s
    return out


def family_free_run(E, a0, eps, T, chi0=0.0, dt=0.002, seed=0, stride=5):
    """Closed loop with decoder psi = y + eps b z (exact at eps = 0); returns t, |chi|, y."""
    fam = Family(E=E, a0=a0)
    b = np.ones(3) / np.sqrt(3)
    s = np.array([1.0, 1.0, 20.0]) + np.random.default_rng(seed).normal(size=3)
    for _ in range(int(50.0 / dt)):
        s = rk4(lorenz, s, dt)
    x = np.concatenate([s, [fam.h(s[2]) + chi0]])
    fun = lambda x: fam.f(x, x[:3] + eps * b * x[3])
    n = int(T / dt) // stride
    chi, ys = np.full(n, np.nan), np.full((n, 3), np.nan)
    for i in range(n * stride):
        x = rk4(fun, x, dt)
        if not np.all(np.isfinite(x)) or np.abs(x).max() > 1e4:
            break
        if i % stride == 0:
            chi[i // stride] = abs(x[3] - fam.h(x[2]))
            ys[i // stride] = x[:3]
    return np.arange(n) * dt * stride, chi, ys


def _family_task(args):
    return args, family_free_run(*args)


def fig_family(out, workers=8):
    import multiprocessing as mp

    orbit = lorenz_orbit(1000.0)
    mean_sech2 = float(np.mean(1.0 / np.cosh((orbit[:, 2] - 27.0) / 4.0) ** 2))
    cle = float(np.linalg.eigvals(Family().A).real.max())  # the same for every a0
    a0s = np.linspace(0, 8, 81)
    perp = -1.0 + a0s * mean_sech2
    tasks = [(-1.0, a0, 0.0, 40.0, 1e-3) for a0 in (3.0, 6.0)]
    with mp.Pool(min(workers, len(tasks))) as p:
        runs = dict(p.map(_family_task, tasks))
    blue, orange = GAMMA_COLORS[1.0], GAMMA_COLORS[5.0]
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.5, 2.35), constrained_layout=True,
                                  width_ratios=[1.1, 1.1, 1])
    a.plot(a0s, perp, color=INK, lw=1.4, label=r"transverse")
    a.axhline(cle, color=MUTED, lw=1.4, ls="--", label="conditional")
    a.axhline(0, color=GRID, lw=1.0)
    for a0, col in ((3.0, blue), (6.0, orange)):
        a.plot(a0, -1.0 + a0 * mean_sech2, "o", color=col, ms=5, zorder=3)
    a.set(xlabel=r"$a_0$", ylabel="exponent")
    a.set_title("(a) Same conditional exponents, zero\nerror, any transverse exponent", loc="left", fontsize=8)
    a.legend(frameon=False, loc="upper left", handlelength=1.6)
    for (args, (t, chi, ys)), col in zip(runs.items(), (blue, orange)):
        m = np.isfinite(chi)
        w = 50  # running maximum over 0.5 time units, which hides the dips where chi changes sign
        env = np.array([chi[m][max(0, i - w):i + 1].max() for i in range(m.sum())])
        b.semilogy(t[m], env, color=col, lw=0.9, label=f"$a_0={args[1]:g}$")
    b.set(xlabel="time since the loop was closed", ylabel=r"invisible mode $|\chi|$", ylim=(1e-7, 1e3))
    b.set_title("(b) Exact readout, offset $10^{-3}$:\none decays, one grows", loc="left", fontsize=8)
    b.legend(frameon=False, loc="lower left")
    c.plot(orbit[::10, 0], orbit[::10, 2], color=GRID, lw=0.5)
    for (args, (t, chi, ys)), col, lw in reversed(list(zip(runs.items(), (blue, orange), (0.6, 0.35)))):
        m = np.isfinite(ys[:, 0])
        c.plot(ys[m, 0], ys[m, 2], color=col, lw=lw)
    c.set(xlabel="$y_1$", ylabel="$y_3$", xlim=(-25, 25), ylim=(-5, 60))
    c.set_title("(c) Decoded free runs", loc="left", fontsize=8)
    for ax in (a, b, c):
        style(ax)
    fig.savefig(out / "fig_family.pdf")
    print(f"fig_family: <sech^2> = {mean_sech2:.4f}, largest CLE = {cle:.3f}, "
          f"lambda_perp(3) = {-1 + 3 * mean_sech2:.3f}, zero at a0 = {1 / mean_sech2:.2f}")


def fig_bubbling(out, workers=8):
    import multiprocessing as mp

    from matplotlib.colors import TwoSlopeNorm

    eps_list = [1e-5, 1e-4, 1e-3, 1e-2]
    T = 8000.0  # as in the table of Sec. 4
    tasks = [(-1.0, a0, eps, T, 0.0) for a0 in (3.0, 0.5) for eps in eps_list]
    with mp.Pool(min(workers, len(tasks))) as p:
        runs = dict(p.map(_family_task, tasks))
    orbit = lorenz_orbit(60.0)
    fam = Family(E=-1.0, a0=3.0)
    mean_rate = float(np.mean(fam.rate(lorenz_orbit(1000.0)[:, 2])))
    blue, orange = GAMMA_COLORS[1.0], GAMMA_COLORS[5.0]
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.5, 2.4), constrained_layout=True, width_ratios=[1.05, 1.1, 1])
    rate = fam.rate(orbit[:, 2])
    sc = a.scatter(orbit[::4, 0], orbit[::4, 2], c=rate[::4], s=0.6, cmap="RdBu_r",
                   norm=TwoSlopeNorm(0.0, rate.min(), rate.max()), lw=0)
    for x in (np.sqrt(72.0), -np.sqrt(72.0)):
        a.plot(x, 27.0, "k+", ms=6, mew=1.0)
    fig.colorbar(sc, ax=a, shrink=0.8, label="local transverse rate")
    a.set(xlabel="$s_1$", ylabel="$s_3$")
    a.set_title(f"(a) Local rate: average {mean_rate:.2f},\npositive for $s_3$ near 27", loc="left", fontsize=8)
    for a0, col, lab in ((3.0, orange, "bubbling"), (0.5, blue, "uniform contraction")):
        t, chi, _ = runs[(-1.0, a0, 1e-4, T, 0.0)]
        w = int(10 / (t[1] - t[0]))  # maximum over blocks of 10 time units, over the whole run
        n = len(chi) // w * w
        b.semilogy(t[:n:w], chi[:n].reshape(-1, w).max(axis=1), color=col, lw=0.7, label=f"{lab} ($a_0={a0:g}$)")
    b.set(xlabel="time", ylabel=r"max $|\chi|$ over 10 time units")
    b.set_title(r"(b) Decoder error $\varepsilon=10^{-4}$: bursts", loc="left", fontsize=8)
    b.legend(frameon=False, loc="upper left")
    b.set_ylim(1e-6, 1e3)
    for a0, col in ((0.5, blue), (3.0, orange)):
        med, sup = [], []
        for eps in eps_list:
            chi = runs[(-1.0, a0, eps, T, 0.0)][1]
            chi = chi[len(chi) // 10:]
            chi = chi[np.isfinite(chi)]
            med.append(np.median(chi)); sup.append(chi.max())
        c.loglog(eps_list, med, "o-", color=col, ms=3, lw=1.0)
        c.loglog(eps_list, sup, "s--", color=col, ms=3, lw=1.0)
    c.plot([], [], "k-o", ms=3, lw=1.0, label="median"); c.plot([], [], "k--s", ms=3, lw=1.0, label="maximum")
    c.set(xlabel=r"decoder error $\varepsilon$", ylabel=r"$|\chi|$")
    c.set_title("(c) Median scales,\nmaximum does not", loc="left", fontsize=8)
    c.legend(frameon=False, loc="upper left")
    for ax in (a, b, c):
        style(ax)
    fig.savefig(out / "fig_bubbling.pdf")
    for a0 in (3.0, 0.5):
        for eps in eps_list:
            chi = runs[(-1.0, a0, eps, T, 0.0)][1]
            chi = chi[len(chi) // 10:]
            fin = chi[np.isfinite(chi)]
            print(f"fig_bubbling a0={a0} eps={eps:g}: median {np.median(fin):.2e} sup {fin.max():.2e} "
                  f"finite {np.isfinite(chi).mean():.2f}")


NO_RESULTS = ("counterexample", "overview", "opening", "family", "bubbling")
LONG_SCANS = ("tangent_survival", "predictors", "gap")  # need --results


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, help="directory with lorenz_long.jsonl and rossler_long.jsonl")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source-scan", type=Path,
                   help="directory with sources_lambda.csv and sources_lambdaoff.csv, for fig_sources")
    p.add_argument("--only", nargs="*", choices=NO_RESULTS + LONG_SCANS + ("sources",),
                   help="make only these figures, e.g. overview family bubbling")
    a = p.parse_args()
    names = a.only or list(NO_RESULTS) + (list(LONG_SCANS) if a.results else []) + (["sources"] if a.source_scan else [])
    if any(n in LONG_SCANS for n in names) and a.results is None:
        p.error("these figures need --results: " + " ".join(n for n in names if n in LONG_SCANS))
    if "sources" in names and a.source_scan is None:
        p.error("fig_sources needs --source-scan")
    a.out.mkdir(parents=True, exist_ok=True)
    data = {name: load(a.results / f) for name, f in SCANS.items()} if a.results else None
    for name in names:
        fig = globals()[f"fig_{name}"]
        if name in LONG_SCANS:
            fig(data, a.out)
        elif name == "sources":
            fig(a.source_scan, a.out)
        else:
            fig(a.out)
    print(sorted(x.name for x in a.out.glob("*.pdf")))


if __name__ == "__main__":
    main()
