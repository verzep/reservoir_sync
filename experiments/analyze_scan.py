"""Test the three claims of the draft on a scan (JSON lines from scan.py).

    python experiments/analyze_scan.py results/scan_first.jsonl --source lorenz

A. The field error, not the state error, predicts free-running performance
   (and e_dot dominates e).
B. The transverse exponent, not the largest CLE, predicts free-running
   performance, within each gamma.
C. Without a smooth synchronization map, the closed-loop spectrum along the
   synchronized trajectory still contains the source's unstable and neutral
   exponents.

Correlations are Spearman, within each gamma (gamma moves every quantity
together), plus their mean over gammas. Writes a figure next to the input.
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


def load(paths, source):
    recs = []
    for p in paths:
        for line in Path(p).read_text().splitlines():
            r = json.loads(line)
            if "error" not in r and r["config"]["source"] == source:
                recs.append(r)
    return recs


def _num(x):
    return np.nan if x is None else float(x)


def table(recs):
    col = lambda f: np.array([_num(f(r)) for r in recs])
    return {
        "gamma": col(lambda r: r["config"]["gamma"]),
        "valid": col(lambda r: r["valid_time_lyap"]),
        "train_nrmse": col(lambda r: r["train_nrmse"]),
        "test_nrmse_driven": col(lambda r: r["test_nrmse_driven"]),
        "field_train": col(lambda r: r["train_field"]["field_error_rel"]),
        "field_test": col(lambda r: r["test_field"]["field_error_rel"]),
        "edot_over_e": col(lambda r: r["train_field"]["e_dot_rms"] / r["train_field"]["e_rms"]),
        "feedback_over_edot": col(lambda r: r["train_field"]["feedback_rms"] / r["train_field"]["e_dot_rms"]),
        "cle_max": col(lambda r: r["lyap_cle"][0]),
        "perp_driven": col(lambda r: r["lambda_perp_driven"]),
        "perp_free": col(lambda r: r["lambda_perp_free"]),
        "smooth": col(lambda r: r["smooth_sync_condition"]),
        "gs_ok": col(lambda r: r["gs_distance_final"] < 1e-6),
        "leak": col(lambda r: r["invariance_leak"]),
    }


def within_gamma(T, x, y="valid"):
    """Spearman rho of x vs y in each gamma, and the mean over gammas."""
    out = {}
    for g in np.unique(T["gamma"]):
        m = (T["gamma"] == g) & np.isfinite(T[x]) & np.isfinite(T[y])
        out[g] = spearmanr(T[x][m], T[y][m])[0] if m.sum() > 3 else np.nan
    pooled = spearmanr(T[x], T[y], nan_policy="omit")[0]
    return out, float(np.nanmean(list(out.values()))), float(pooled)


def report_corr(T, names, title):
    gammas = np.unique(T["gamma"])
    print(f"\n{title}")
    print(f"  {'predictor':<20}" + "".join(f"  g={g:<5g}" for g in gammas) + "   mean     pooled")
    for x in names:
        per, mean, pooled = within_gamma(T, x)
        print(f"  {x:<20}" + "".join(f"  {per[g]:+.2f}  " for g in gammas) + f"  {mean:+.2f}    {pooled:+.2f}")


def claim_c(recs, tol=0.1):
    """Fraction of runs whose top closed-loop (driven) exponents match the
    source's non-negative exponents, split by the smoothness condition."""
    rows = {True: [], False: []}
    for r in recs:
        src = [l for l in r["lyap_source"] if l > -tol]
        cl = r["lyap_closed_driven"][: len(src)]
        ok = all(c is not None and abs(c - s) < tol for c, s in zip(cl, src))
        rows[bool(r["smooth_sync_condition"])].append(ok)
    for smooth, oks in rows.items():
        if oks:
            print(f"  smooth condition {'holds' if smooth else 'fails'}: "
                  f"source exponents recovered in {sum(oks)}/{len(oks)} runs")


def figure(T, path):
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    panels = [
        ("train_nrmse", "train NRMSE (state error)", True),
        ("field_train", "rel. field error, train", True),
        ("edot_over_e", "rms(e_dot) / rms(e)", True),
        ("cle_max", "largest CLE", False),
        ("perp_driven", "lambda_perp (driven base)", False),
        ("perp_free", "lambda_perp (free run)", False),
    ]
    gammas = np.unique(T["gamma"])
    colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(gammas)))
    for ax, (x, label, logx) in zip(axes.flat, panels):
        for g, c in zip(gammas, colors):
            m = T["gamma"] == g
            ax.scatter(T[x][m], T["valid"][m], s=18, color=c, label=f"gamma {g:g}")
        _, mean, _ = within_gamma(T, x)
        ax.set_title(f"{label}\nwithin-gamma rho = {mean:+.2f}", fontsize=10)
        ax.set_xscale("log" if logx else "linear")
        ax.set_ylabel("valid time (Lyapunov times)")
    axes[0, 0].legend(fontsize=8)
    fig.savefig(path, dpi=130)
    print(f"\nfigure: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--source", default="lorenz")
    args = parser.parse_args()
    recs = load(args.paths, args.source)
    T = table(recs)
    print(f"{args.source}: {len(recs)} runs; GS ok {int(T['gs_ok'].sum())}; "
          f"smooth sync condition {int(T['smooth'].sum())}; "
          f"valid time median {np.median(T['valid']):.2f}, max {T['valid'].max():.2f} Lyapunov times")

    print("\nA. State error vs field error")
    print(f"  rms(e_dot)/rms(e): median {np.median(T['edot_over_e']):.1f} "
          f"(range {T['edot_over_e'].min():.1f}-{T['edot_over_e'].max():.1f})")
    print(f"  rms(feedback)/rms(e_dot): median {np.median(T['feedback_over_edot']):.2f}")
    report_corr(T, ["train_nrmse", "test_nrmse_driven", "field_train", "field_test"],
                "  Spearman rho with valid time (negative = predicts good runs)")

    print("\nB. Conditional vs transverse exponents")
    d = T["perp_driven"] - T["cle_max"]
    print(f"  lambda_perp(driven) - CLE_max: median {np.nanmedian(d):+.2f}, "
          f"> 0 in {int(np.nansum(d > 0))}/{len(d)} runs; lambda_perp >= -0.05 in "
          f"{int(np.nansum(T['perp_driven'] >= -0.05))} runs")
    report_corr(T, ["cle_max", "perp_driven", "perp_free", "leak"],
                "  Spearman rho with valid time")
    per, mean, _ = within_gamma(T, "perp_driven", "cle_max")
    print(f"  rho(lambda_perp, CLE_max) within gamma: mean {mean:+.2f}")

    print("\nC. Closed-loop spectrum without a smooth sync map")
    claim_c(recs)

    figure(T, Path(args.paths[0]).with_name(f"analysis_{args.source}.png"))


if __name__ == "__main__":
    main()
