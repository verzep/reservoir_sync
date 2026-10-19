"""Analysis of claim_a.py: does e_dot matter at a fixed state error?

    python experiments/analyze_claim_a.py results/claim_a.jsonl

1. Direction perturbations: per reservoir and eps, Spearman rho of omega with
   e_dot, field error, valid time and lambda_perp (averaged over seeds), and how
   constant the state error stays.
2. Within-reservoir regression of log valid time on log e and log e_dot
   (reservoir fixed effects), with and without lambda_perp.
3. The ridge (beta) scan.
Writes a figure next to the input.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


def load(path):
    recs = [json.loads(l) for l in Path(path).read_text().splitlines()]
    bad = [r for r in recs if "error" in r]
    if bad:
        print(f"{len(bad)} failed tasks, first error:\n{bad[0]['error']}")
    return [r for r in recs if "error" not in r]


def get(r, key):
    t, f = r["task"], r["train_field"]
    return {
        "omega": r["omega"], "e": f["e_rms"], "e_dot": f["e_dot_rms"],
        "field": r["test_field"]["field_error_rel"], "valid": r["valid_mean"],
        "perp": r["lambda_perp"], "dN": r["delta_N_norm"], "nrmse": r["train_nrmse"],
        "beta": t["beta"], "eps": t["eps"],
    }[key]


def arr(rs, key):
    return np.array([np.nan if get(r, key) is None else get(r, key) for r in rs], dtype=float)


def directions_table(recs):
    groups = defaultdict(list)
    for r in recs:
        if r["task"]["kind"] == "direction":
            t = r["task"]
            groups[(t["gamma"], t["eps"], t["seed"])].append(r)
    keys = ["e_dot", "field", "valid", "perp", "dN"]
    print("\n1. Direction perturbations: Spearman rho with omega (mean over seeds)")
    print(f"  {'gamma':>5} {'eps':>7}  {'e cv':>6}  " + "  ".join(f"{k:>6}" for k in keys) + "   valid slow -> fast")
    summary = defaultdict(lambda: defaultdict(list))
    for (g, eps, seed), rs in sorted(groups.items()):
        om, e = arr(rs, "omega"), arr(rs, "e")
        summary[(g, eps)]["e_cv"].append(e.std() / e.mean())
        for k in keys:
            y = arr(rs, k)
            m = np.isfinite(y)
            summary[(g, eps)][k].append(spearmanr(om[m], y[m])[0] if m.sum() > 3 else np.nan)
        order = np.argsort(om)
        summary[(g, eps)]["slow"].append(arr(rs, "valid")[order[0]])
        summary[(g, eps)]["fast"].append(arr(rs, "valid")[order[-1]])
    for (g, eps), d in sorted(summary.items()):
        print(f"  {g:>5g} {eps:>7.0e}  {np.mean(d['e_cv']):6.2f}  "
              + "  ".join(f"{np.nanmean(d[k]):+6.2f}" for k in keys)
              + f"   {np.mean(d['slow']):5.2f} -> {np.mean(d['fast']):5.2f}")
    return groups


def fixed_effects(groups):
    """OLS of log valid on log e, log e_dot (and lambda_perp), demeaned per reservoir."""
    print("\n2. Within-reservoir regression of log valid time (direction runs, all eps)")
    by_res = defaultdict(list)
    for (g, eps, seed), rs in groups.items():
        by_res[(g, seed)] += rs
    for with_perp in (False, True):
        X, y = [], []
        for rs in by_res.values():
            cols = [np.log(arr(rs, "e")), np.log(arr(rs, "e_dot"))]
            if with_perp:
                cols.append(arr(rs, "perp"))
            Z = np.column_stack(cols)
            v = np.log(np.maximum(arr(rs, "valid"), 1e-3))
            m = np.all(np.isfinite(Z), 1) & np.isfinite(v)
            X.append(Z[m] - Z[m].mean(0))
            y.append(v[m] - v[m].mean())
        X, y = np.vstack(X), np.concatenate(y)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        r2 = 1 - np.sum((y - X @ coef) ** 2) / np.sum(y**2)
        names = ["log e", "log e_dot"] + (["lambda_perp"] if with_perp else [])
        print("  " + ", ".join(f"{n} {c:+.3f}" for n, c in zip(names, coef)) + f"   (within R^2 {r2:.2f}, {len(y)} runs)")


def beta_table(recs):
    print("\n3. Ridge scan (no perturbation): medians over seeds")
    print(f"  {'gamma':>5} {'beta':>7}  {'nrmse':>8} {'e_dot/e':>8} {'field':>8} {'perp':>6} {'valid':>6}")
    groups = defaultdict(list)
    for r in recs:
        if r["task"]["kind"] in ("beta", "baseline"):
            groups[(r["task"]["gamma"], r["task"]["beta"])].append(r)
    for (g, b), rs in sorted(groups.items()):
        print(f"  {g:>5g} {b:>7.0e}  {np.median(arr(rs, 'nrmse')):8.1e} "
              f"{np.median(arr(rs, 'e_dot') / arr(rs, 'e')):8.1f} {np.median(arr(rs, 'field')):8.1e} "
              f"{np.nanmedian(arr(rs, 'perp')):+6.2f} {np.median(arr(rs, 'valid')):6.2f}")


def figure(groups, path):
    eps_list = sorted({k[1] for k in groups})
    gammas = sorted({k[0] for k in groups})
    colors = dict(zip(gammas, plt.cm.viridis(np.linspace(0.1, 0.85, len(gammas)))))
    rows = [("e", "rms e"), ("e_dot", "rms e_dot"), ("valid", "valid time (Lyap.)"), ("perp", "lambda_perp")]
    fig, axes = plt.subplots(len(rows), len(eps_list), figsize=(4 * len(eps_list), 2.6 * len(rows)),
                             constrained_layout=True, squeeze=False)
    for (g, eps, seed), rs in groups.items():
        j = eps_list.index(eps)
        om = arr(rs, "omega")
        order = np.argsort(om)
        for i, (k, label) in enumerate(rows):
            ax = axes[i, j]
            ax.plot(om[order], arr(rs, k)[order], "-o", ms=3, lw=0.8, color=colors[g], alpha=0.8)
            ax.set_xscale("log")
            if k in ("e", "e_dot"):
                ax.set_yscale("log")
            ax.set_ylabel(label)
            if i == 0:
                ax.set_title(f"eps = {eps:g} sigma_s")
            if i == len(rows) - 1:
                ax.set_xlabel("omega of the perturbation direction")
    for g in gammas:
        axes[0, 0].plot([], [], color=colors[g], label=f"gamma {g:g}")
    axes[0, 0].legend(fontsize=8)
    fig.savefig(path, dpi=130)
    print(f"\nfigure: {path}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path")
    a = p.parse_args()
    recs = load(a.path)
    print(f"{len(recs)} runs")
    groups = directions_table(recs)
    fixed_effects(groups)
    beta_table(recs)
    figure(groups, Path(a.path).with_name("analysis_claim_a.png"))


if __name__ == "__main__":
    main()
