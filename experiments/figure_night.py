"""Failure rate and free-run end state vs lambda_perp, one column per scan.

    python experiments/figure_night.py results/night_2026-10-20/lorenz_long.jsonl:lorenz \\
        results/night_2026-10-20/rossler_long.jsonl:rossler --out results/night_2026-10-20/fig_perp.png
"""

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyze_night import FAIL, load

EDGES = np.array([-np.inf, -2.0, -1.0, -0.3, -0.05, 0.3, 1.0, 3.0, np.inf])
LABELS = ["< −2", "−2…−1", "−1…−0.3", "−0.3…−0.05", "−0.05…0.3", "0.3…1", "1…3", "> 3"]
GAMMA_COLORS = {1.0: "#2a78d6", 5.0: "#eb6834", 20.0: "#1baf7a"}  # validated (all pairs, light)
CLASSES = [("chaotic", "#2a78d6"), ("periodic", "#1baf7a"), ("fixed_point", "#eb6834"), ("diverged", "#9a9a94")]
INK, MUTED, GRID = "#222220", "#6b6b66", "#e4e3de"


def _bin(perp):
    return np.searchsorted(EDGES, perp, side="right") - 1


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scans", nargs="+", help="path:source")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    fig, axes = plt.subplots(2, len(a.scans), figsize=(5.2 * len(a.scans), 7), squeeze=False,
                             constrained_layout=True)
    x = np.arange(len(LABELS))
    for j, spec in enumerate(a.scans):
        path, source = spec.rsplit(":", 1)
        recs = [r for r in load([path], source) if r["lambda_perp_driven"] is not None]
        perp = np.array([r["lambda_perp_driven"] for r in recs])
        gam = np.array([r["config"]["gamma"] for r in recs])
        b = _bin(perp)
        ax = axes[0, j]
        for g, c in GAMMA_COLORS.items():
            ys = []
            for k in range(len(LABELS)):
                m = (b == k) & (gam == g)
                v = np.concatenate([r["valid_times_lyap"] for r, mm in zip(recs, m) if mm]) if m.sum() >= 3 else []
                ys.append(np.mean(np.asarray(v) < FAIL) if len(v) else np.nan)
            ax.plot(x, ys, "-o", color=c, lw=2, ms=6, mec="white", mew=1.5, label=f"γ = {g:g}")
        ax.set_ylim(-0.03, 1.03)
        ax.set_xticks(x, [])
        ax.set_ylabel(f"fraction of starts with valid time < {FAIL:g} Lyapunov time", color=INK, fontsize=8)
        ax.set_title(f"{source.capitalize()}  ({len(recs)} runs)", color=INK, fontsize=10, loc="left")
        ax.legend(frameon=False, fontsize=8, labelcolor=INK)
        style(ax)
        ax = axes[1, j]
        counts = np.array([[sum(1 for r, k in zip(recs, b) if k == kk and r["end_state"]["class"] == cls)
                            for kk in range(len(LABELS))] for cls, _ in CLASSES], float)
        tot = counts.sum(0)
        frac = np.divide(counts, tot, out=np.zeros_like(counts), where=tot > 0)
        bottom = np.zeros(len(LABELS))
        for (cls, c), f in zip(CLASSES, frac):
            ax.bar(x, f, bottom=bottom, color=c, width=0.7, edgecolor="white", linewidth=2,
                   label=cls.replace("_", " "))
            bottom += f
        for k, t in enumerate(tot):
            ax.text(k, 1.02, f"{int(t)}", ha="center", va="bottom", fontsize=7, color=MUTED)
        ax.set_ylim(0, 1.1)
        ax.set_xticks(x, LABELS, rotation=35, ha="right")
        ax.set_xlabel("λ⊥ along the synchronized trajectory (bin; count above)", color=INK, fontsize=8)
        ax.set_ylabel("end state of the free run (fraction)", color=INK, fontsize=8)
        ax.legend(frameon=False, fontsize=8, labelcolor=INK, ncol=4, loc="upper left", bbox_to_anchor=(0, -0.32))
        style(ax)
    fig.savefig(a.out, dpi=140, facecolor="white")
    print(a.out)


if __name__ == "__main__":
    main()
