"""Loading of scan results and the plot style shared by the analysis and figure scripts.

Scans are JSON lines, one record per run (experiments/scan.py). Failed runs carry
an "error" field and are dropped by load().
"""

import json
from pathlib import Path

import numpy as np

GAMMA_COLORS = {1.0: "#2a78d6", 5.0: "#eb6834", 20.0: "#1baf7a"}  # validated (all pairs, light)
INK, MUTED, GRID = "#222220", "#6b6b66", "#e4e3de"

PAPER_RC = {
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 9, "legend.fontsize": 7.5,
    "pdf.fonttype": 42, "axes.labelcolor": INK, "text.color": INK,
}


def read_jsonl(path):
    """All records of a JSON-lines file, failed runs included."""
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def load(paths, source=None, keep=None):
    """Records without an error from one path or several, optionally only those of
    one source and those for which keep(record) is true."""
    if isinstance(paths, (str, Path)):
        paths = [paths]
    recs = []
    for p in paths:
        for r in read_jsonl(p):
            if "error" in r or (source is not None and r["config"]["source"] != source):
                continue
            if keep is None or keep(r):
                recs.append(r)
    return recs


def col(recs, f):
    """f over the records as a float array (None becomes nan)."""
    return np.array([f(r) for r in recs], dtype=float)


def use_paper_style():
    import matplotlib.pyplot as plt

    plt.rcParams.update(PAPER_RC)


def style(ax, labelsize=7, grid_axis="both", grid_lw=0.6):
    """Open axes, muted spines and ticks, light grid behind the data."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=labelsize)
    ax.grid(True, axis=grid_axis, color=GRID, lw=grid_lw)
    ax.set_axisbelow(True)
