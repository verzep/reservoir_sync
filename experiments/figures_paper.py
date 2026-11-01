"""Figures of the paper, as vector PDFs.

    python experiments/figures_paper.py --results results/night_2026-10-20 --out figures

1. fig_counterexample: the 2-d counterexample (needs no results).
2. fig_tangent_survival: closed-loop exponents nearest the source's positive and
   zero exponents vs the largest CLE, in transversely stable runs.
3. fig_predictors: median valid time vs training error, largest CLE and lambda_perp.
4. fig_gap: lambda_perp vs the largest CLE.
5. fig_opening: two reservoirs alike in training, opposite in free run (needs no results).
6. fig_overview: schematic of training and closing the loop (needs no results).
7. fig_sources: the 19-system scan (needs --source-scan).
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm
from scipy.stats import spearmanr

GAMMA_COLORS = {1.0: "#2a78d6", 5.0: "#eb6834", 20.0: "#1baf7a"}
INK, MUTED, GRID = "#222220", "#6b6b66", "#e4e3de"
SCANS = {"Lorenz": "lorenz_long.jsonl", "Rössler": "rossler_long.jsonl"}
STABLE = -0.05

plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 9, "legend.fontsize": 7.5,
    "pdf.fonttype": 42, "axes.labelcolor": INK, "text.color": INK,
})


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def load(path):
    recs = [json.loads(l) for l in Path(path).read_text().splitlines()]
    return [r for r in recs if "error" not in r and r["lambda_perp_driven"] is not None]


def col(recs, f):
    return np.array([f(r) for r in recs], dtype=float)


def within_gamma_rho(x, y, gamma):
    return float(np.mean([spearmanr(x[gamma == g], y[gamma == g])[0] for g in np.unique(gamma)]))


def scatter_by_gamma(ax, x, y, gamma):
    for g, c in GAMMA_COLORS.items():
        m = gamma == g
        ax.scatter(x[m], y[m], s=7, color=c, lw=0.2, edgecolor="white", label=f"γ = {g:g}")


def fig_overview(out):
    # the three phases, drawn with the data of the stable reservoir of fig_opening
    from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

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
    W, H = 6.5, 3.5
    blue, orange = GAMMA_COLORS[1.0], GAMMA_COLORS[5.0]
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, W), ylim=(0, H))
    ax.axis("off")

    def thumb(x0, y0, x1, y1, curves, muted=False):
        a = fig.add_axes([x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H])
        for xs, ys, c, lw in curves:
            a.plot(xs, ys, color=c, lw=lw)
        a.set(xticks=[], yticks=[])
        for s in a.spines.values():
            s.set_color(GRID if muted else MUTED)
            s.set_linewidth(0.6)
            s.set_linestyle("--" if muted else "-")
        a.margins(0.06)

    def arrow(points, color=INK, ls="-", lw=1.0):
        ax.plot(*zip(*points[:-1]), color=color, ls=ls, lw=lw, solid_capstyle="butt")
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>", mutation_scale=8,
                                     color=color, ls=ls, lw=lw, shrinkA=0, shrinkB=0))

    def surrogate(cx, cy, r=0.42):
        ax.add_patch(Circle((cx, cy), r, fc="#f1f0ec", ec=MUTED, lw=0.8))
        rng = np.random.default_rng(3)
        angles = np.arange(7) * 2 * np.pi / 7 + 0.3
        pts = np.c_[cx + 0.28 * np.cos(angles), cy + 0.28 * np.sin(angles)]
        for i, j in rng.integers(0, 7, (11, 2)):
            if i != j:
                ax.plot(*zip(pts[i], pts[j]), color=MUTED, lw=0.4)
        ax.scatter(*pts.T, s=16, fc="white", ec=INK, lw=0.6, zorder=3)

    def label(x, y, text, **kw):
        ax.text(x, y, text, ha=kw.pop("ha", "center"), va="center", **kw)

    y1, y2 = 2.42, 0.72  # row centers
    Sx, Sy = train.S[:, 0], train.S[:, 1]
    t = np.arange(4000) * dt
    scale = train.S.max(axis=0) - train.S.min(axis=0)
    mid = train.S.min(axis=0)

    def signals(x):  # the three coordinates, stacked
        return [(t, (x[:4000, i] - mid[i]) / scale[i] * 0.85 + 2 - i, c, 0.6) for i, c in
                enumerate((blue, INK, orange))]

    label(1.05, 3.37, "Source", fontweight="bold")
    label(3.75, 3.37, "Surrogate", fontweight="bold")
    label(5.5, 3.37, "Output", fontweight="bold")
    label(0.2, y1, "Listening\nand fitting", rotation=90, fontweight="bold")
    label(0.2, y2, "Autonomous", rotation=90, fontweight="bold")
    ax.plot([0.05, W - 0.05], [1.5, 1.5], color=GRID, lw=0.8)

    # listening and fitting: the full state drives the surrogate
    label(1.05, 3.14, r"$\dot{\mathbf{s}}=\mathbf{g}(\mathbf{s})$")
    thumb(0.55, y1 - 0.5, 1.55, y1 + 0.5, [(Sx, Sy, MUTED, 0.4)])
    arrow([(1.55, y1), (1.95, y1)])
    label(2.5, 3.14, r"$\mathbf{s}(t)$")
    thumb(1.95, y1 - 0.5, 3.0, y1 + 0.5, signals(train.S))
    arrow([(3.0, y1), (3.33, y1)])
    label(3.75, 3.14, r"$\dot{\mathbf{r}}=\mathbf{f}(\mathbf{r},\mathbf{s})$")
    surrogate(3.75, y1)
    label(5.5, 3.14, r"$\hat{\mathbf{s}}=\boldsymbol{\psi}(\mathbf{r})\approx\mathbf{s}$")
    thumb(4.95, y1 - 0.5, 6.05, y1 + 0.5, signals(decoded))
    arrow([(4.17, y1), (4.95, y1)], ls="--")
    label(4.56, y1 + 0.12, r"fit $\boldsymbol{\psi}$", fontsize=7.5)

    # closed loop: same training, two possible fates
    thumb(0.55, y2 - 0.5, 1.55, y2 + 0.5, [(Sx, Sy, GRID, 0.4)], muted=True)
    label(1.05, 0.1, "disconnected", fontsize=7.5, color=MUTED)
    surrogate(3.75, y2)
    label(3.75, y2 + 0.56, r"$\dot{\mathbf{r}}=\mathbf{f}(\mathbf{r},\boldsymbol{\psi}(\mathbf{r}))$")
    thumb(4.75, y2 - 0.36, 5.5, y2 + 0.39, [(Sx, Sy, GRID, 0.5), (free_stable[:, 0], free_stable[:, 1], blue, 0.4)])
    thumb(5.6, y2 - 0.36, 6.35, y2 + 0.39, [(Sx, Sy, GRID, 0.5), (free_unstable[:, 0], free_unstable[:, 1], orange, 0.5)])
    label(5.125, y2 + 0.5, "stays", fontsize=7.5, color=blue)
    label(5.975, y2 + 0.5, "leaves", fontsize=7.5, color=orange)
    arrow([(4.17, y2), (4.75, y2)])
    label(4.46, y2 + 0.12, r"$\boldsymbol{\psi}$", fontsize=7.5)
    arrow([(4.46, y2), (4.46, 0.1), (2.85, 0.1), (2.85, y2), (3.33, y2)], color=INK, lw=1.2)
    label(3.65, 0.19, "output fed back as input", fontsize=7.5)
    label(5.55, 0.12, "what decides?", fontsize=8, fontstyle="italic")
    fig.savefig(out / "fig_overview.pdf")


def fig_opening(out):
    # two runs of the Rossler scan with the same hyperparameters, chosen to match in
    # training error and largest CLE, with opposite lambda_perp
    from reservoir_sync.closed_loop import run_autonomous
    from reservoir_sync.driven import drive, settle_source
    from reservoir_sync.readout import fit_readout
    from reservoir_sync.reservoirs import random_reservoir
    from reservoir_sync.sources import SOURCES

    source = SOURCES["rossler"]()
    dt, n_wash, n_train, n_pred = 0.01, 2000, 10000, 30000
    fig, axes = plt.subplots(2, 2, figsize=(6.5, 3.6), constrained_layout=True,
                             width_ratios=[2.4, 1], sharex="col")
    runs = [(1, GAMMA_COLORS[1.0], "(a) λ⊥ = −1.00: the free run follows the source"),
            (21, GAMMA_COLORS[5.0], "(b) λ⊥ = +0.25: the free run leaves it")]
    for (seed, color, title), (a, b) in zip(runs, axes):
        res = random_reservoir(200, source.dim, "tanh", 0.5, 0.05, 0.5, 5.0, None, seed)
        s0 = settle_source(source, dt, 50.0, seed=seed)
        full = drive(source, res, s0, np.zeros(res.n), dt, n_wash + n_train + n_pred)
        train = full[n_wash : n_wash + n_train + 1]
        N = fit_readout(train.R, train.S, 1e-6)
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source-scan", type=Path, help="results/source_scan, for fig_sources")
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    fig_counterexample(a.out)
    fig_overview(a.out)
    fig_opening(a.out)
    data = {name: load(a.results / f) for name, f in SCANS.items()}
    fig_tangent_survival(data, a.out)
    fig_predictors(data, a.out)
    fig_gap(data, a.out)
    if a.source_scan:
        fig_sources(a.source_scan, a.out)
    print(sorted(x.name for x in a.out.glob("*.pdf")))


if __name__ == "__main__":
    main()
