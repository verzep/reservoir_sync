"""Figures of the paper, as vector PDFs.

    python experiments/figures_paper.py --results results/night_2026-10-20 --out figures

1. fig_counterexample: the 2-d counterexample (needs no results).
2. fig_tangent_survival: closed-loop exponents nearest the source's positive and
   zero exponents vs the largest CLE, in transversely stable runs.
3. fig_predictors: median valid time vs training error, largest CLE and lambda_perp.
4. fig_gap: lambda_perp vs the largest CLE.
"""

import argparse
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    fig_counterexample(a.out)
    data = {name: load(a.results / f) for name, f in SCANS.items()}
    fig_tangent_survival(data, a.out)
    fig_predictors(data, a.out)
    fig_gap(data, a.out)
    print(sorted(x.name for x in a.out.glob("*.pdf")))


if __name__ == "__main__":
    main()
