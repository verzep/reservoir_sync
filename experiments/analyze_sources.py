"""Does the unstable fraction follow a law in the source's exponents?

    python experiments/analyze_sources.py results/source_scan --arms raw lambda freq

Expects <dir>/calibration.json and <dir>/scan_<arm>.jsonl. Prints, per arm, a
per-source table and the candidate laws, and writes <dir>/sources_<arm>.csv,
<dir>/laws.csv and <dir>/source_laws.png.

Laws are tested across sources (the source is the unit: runs of one source are
not independent evidence about a law between sources). Each candidate gets a
Spearman correlation with a bootstrap interval over sources, a permutation p
with Holm correction across the candidates of that arm, and an out-of-sample
test: logit(unstable fraction) ~ log(x) fitted on the discovery sources and
scored on the held-out ones (HELD_OUT, fixed before the scan ran).
"""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from analyze_night import FAIL, UNSTABLE, load, table, within_gamma

# every third source by lambda_1 / |lambda_min|, Lorenz and Rossler kept for
# discovery since they motivated the question; set by select_held_out, frozen here
HELD_OUT: tuple = ()

AMBIGUOUS = 0.1  # lambda_perp within this fraction of lambda_1 from 0 or lambda_1
N_BOOT = 10000
N_PERM = 10000


def kaplan_yorke(lam):
    lam = np.sort(lam)[::-1]
    c = np.cumsum(lam)
    j = int(np.max(np.flatnonzero(c >= 0)))
    return float(j + 1 + c[j] / abs(lam[j + 1])) if j + 1 < len(lam) else float(len(lam))


def select_held_out(calibration):
    """Every third source by lambda_1 / |lambda_min|, without Lorenz and Rossler."""
    names = [n for n in calibration if n not in ("lorenz", "rossler")]
    ratio = lambda n: calibration[n]["lyap"][0] / abs(calibration[n]["lyap"][-1])
    return tuple(sorted(sorted(names, key=ratio)[1::3]))


def wilson(k, n, z=1.96):
    p, d = k / n, 1 + z**2 / n
    c, h = (p + z**2 / (2 * n)) / d, z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h


def source_row(name, recs, cal):
    """One source of one arm: fractions, correlations with the valid time, end states."""
    T = table(recs)
    lam = np.array(cal["lyap"])
    scale = np.median([r["config"]["time_scale"] for r in recs])
    l1, lmin = scale * lam[0], scale * lam[-1]
    perp = T["perp"]
    known = np.isfinite(perp)
    k = int(np.sum(perp[known] >= UNSTABLE))
    ends = Counter(r["end_state"]["class"] for r in recs)
    on = sum(bool(r["end_state"].get("on_source")) for r in recs)
    near = (np.abs(perp) < AMBIGUOUS * l1) | (np.abs(perp - l1) < AMBIGUOUS * l1)
    clear = known & ~near
    gain = T["gain_NB"]
    row = {
        "source": name, "d": len(lam), "runs": len(recs), "lambda_1": l1, "lambda_min": lmin,
        "ratio": l1 / abs(lmin), "d_ky": kaplan_yorke(lam),
        "lam1_period": float(lam[0] * cal["period"]),
        "unstable": k / max(known.sum(), 1), "unstable_lo": wilson(k, max(known.sum(), 1))[0],
        "unstable_hi": wilson(k, max(known.sum(), 1))[1],
        "unstable_rel": float(np.mean(perp[known] / l1 >= UNSTABLE)),
        "unstable_clear": float(np.mean(perp[clear] >= UNSTABLE)) if clear.any() else np.nan,
        "ambiguous": float(np.mean(near[known])), "unidentified": float(np.mean(~known)),
        "perp_median": float(np.nanmedian(perp)), "fail": float(np.nanmean(T["fail_frac"])),
        "valid_median": float(np.nanmedian(T["valid_med"])),
        "cle_median": float(np.nanmedian(T["cle_max"])),
        "cle_over_l1": float(np.nanmedian(T["cle_max"]) / l1),
        "cle_over_lmin": float(np.nanmedian(T["cle_max"]) / abs(lmin)),
        "gain_median": float(np.nanmedian(gain)), "nrmse_median": float(np.nanmedian(T["train_nrmse"])),
    }
    for key, x in [("rho_perp", "perp"), ("rho_nrmse", "train_nrmse"), ("rho_cle", "cle_max")]:
        rhos = within_gamma(T, x, "valid_med")
        row[key] = float(np.nanmean(rhos)) if len(rhos) else np.nan
    for cls in ("fixed_point", "periodic", "chaotic", "diverged"):
        row[f"end_{cls}"] = ends[cls] / len(recs)
    row["end_on_source"] = on / len(recs)
    return row


def logit_fraction(row, field="unstable"):
    """Logit with a Jeffreys correction, so that 0 and 1 stay finite."""
    k = row[field] * row["runs"]
    return np.log((k + 0.5) / (row["runs"] - k + 0.5))


# (name, column, take the log, exploratory: added after the task's list)
CANDIDATES = [
    ("lambda_1", "lambda_1", True, False),
    ("|lambda_min|", "abs_lambda_min", True, False),
    ("lambda_1/|lambda_min|", "ratio", True, False),
    ("D_KY", "d_ky", False, False),
    ("CLE/lambda_1", "cle_over_l1", False, False),
    ("CLE/|lambda_min|", "cle_over_lmin", False, False),
    ("loop gain |N^T B|", "gain_median", True, False),
    ("lambda_1 x period", "lam1_period", True, True),
]


def holm(ps):
    order = np.argsort(ps)
    out, top = np.empty(len(ps)), 0.0
    for i, j in enumerate(order):
        top = max(top, min(1.0, (len(ps) - i) * ps[j]))
        out[j] = top
    return out


def _fit_predict(x, y, x_new):
    return np.polyval(np.polyfit(x, y, 1), x_new)


def law_tests(rows, y_field="unstable", seed=0):
    """One record per candidate that varies across the sources of this arm."""
    rng = np.random.default_rng(seed)
    y = np.array([logit_fraction(r, y_field) for r in rows])
    held = np.array([r["source"] in HELD_OUT for r in rows])
    out = []
    for name, col, take_log, exploratory in CANDIDATES:
        x = np.array([abs(r["lambda_min"]) if col == "abs_lambda_min" else r[col] for r in rows], float)
        if take_log:
            x = np.log(x)
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() < 6 or np.ptp(x[ok]) < 1e-6:  # e.g. lambda_1 when it is normalized away
            continue
        xo, yo, ho = x[ok], y[ok], held[ok]
        rho = spearmanr(xo, yo)[0]
        idx = rng.integers(0, len(xo), (N_BOOT, len(xo)))
        boot = np.array([spearmanr(xo[i], yo[i])[0] for i in idx if np.ptp(xo[i]) > 0 and np.ptp(yo[i]) > 0])
        perm = np.array([spearmanr(xo, rng.permutation(yo))[0] for _ in range(N_PERM)])
        p = (1 + np.sum(np.abs(perm) >= abs(rho))) / (N_PERM + 1)
        loso = np.array([_fit_predict(np.delete(xo, i), np.delete(yo, i), xo[i]) for i in range(len(xo))])
        rec = {
            "law": name, "exploratory": exploratory, "n": int(len(xo)), "rho": float(rho),
            "rho_lo": float(np.nanquantile(boot, 0.025)), "rho_hi": float(np.nanquantile(boot, 0.975)), "p": float(p),
            "r2_loso": float(1 - np.sum((yo - loso) ** 2) / np.sum((yo - np.array(
                [np.delete(yo, i).mean() for i in range(len(yo))])) ** 2)),
        }
        if ho.sum() >= 3 and (~ho).sum() >= 3:
            pred = _fit_predict(xo[~ho], yo[~ho], xo[ho])
            rec["rho_discovery"] = float(spearmanr(xo[~ho], yo[~ho])[0])
            rec["rho_held_out"] = float(spearmanr(pred, yo[ho])[0]) if np.ptp(pred) > 0 else np.nan
            base = yo[~ho].mean()
            rec["r2_held_out"] = float(1 - np.sum((yo[ho] - pred) ** 2) / np.sum((yo[ho] - base) ** 2))
        out.append(rec)
    if out:
        for rec, q in zip(out, holm([r["p"] for r in out])):
            rec["p_holm"] = float(q)
    return out


def gamma_cells(recs_by_source, calibration):
    """Unstable fraction per (source, gamma), with gamma in units of the source's rates."""
    cells = []
    for name, recs in recs_by_source.items():
        cal = calibration[name]
        for g in sorted({r["config"]["gamma"] for r in recs}):
            sub = [r for r in recs if r["config"]["gamma"] == g]
            tau = sub[0]["config"]["time_scale"]
            perp = np.array([np.nan if r["lambda_perp_driven"] is None else r["lambda_perp_driven"] for r in sub])
            cells.append({"source": name, "gamma": g, "gamma_over_l1": g / (tau * cal["lyap"][0]),
                          "gamma_period": g * cal["period"] / tau,
                          "unstable": float(np.mean(perp[np.isfinite(perp)] >= UNSTABLE)), "runs": len(sub)})
    return cells


def cell_law(cells, column, seed=0):
    """Spearman of unstable fraction with a gamma-based predictor; bootstrap over sources."""
    rng = np.random.default_rng(seed)
    names = sorted({c["source"] for c in cells})
    by = {n: [c for c in cells if c["source"] == n] for n in names}

    def rho(sample):
        rows = [c for n in sample for c in by[n]]
        return spearmanr([c[column] for c in rows], [c["unstable"] for c in rows])[0]

    boot = [rho(rng.choice(names, len(names))) for _ in range(2000)]
    return rho(names), float(np.nanquantile(boot, 0.025)), float(np.nanquantile(boot, 0.975))


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(rows)


def print_sources(arm, rows):
    print(f"\n=== {arm}: per source (unstable: lambda_perp >= {UNSTABLE}; fail: valid < {FAIL:g} Lyapunov time)")
    print("source            d runs   l1     lmin   l1/|lmin| D_KY  unst [95% CI]      rel  clear ambig  perp   fail valid"
          "  rho:perp nrmse  cle   fp   per  cha  on  div")
    for r in sorted(rows, key=lambda r: r["ratio"]):
        mark = "*" if r["source"] in HELD_OUT else " "
        print(f"{r['source']:16s}{mark}{r['d']:1d} {r['runs']:4d} {r['lambda_1']:6.3f} {r['lambda_min']:7.2f} {r['ratio']:7.3f}"
              f" {r['d_ky']:5.2f}  {r['unstable']:.2f} [{r['unstable_lo']:.2f},{r['unstable_hi']:.2f}]"
              f"  {r['unstable_rel']:.2f} {r['unstable_clear']:5.2f} {r['ambiguous']:5.2f} {r['perp_median']:+6.2f}"
              f"  {r['fail']:.2f} {r['valid_median']:5.1f}   {r['rho_perp']:+.2f}  {r['rho_nrmse']:+.2f} {r['rho_cle']:+.2f}"
              f"  {r['end_fixed_point']:.2f} {r['end_periodic']:.2f} {r['end_chaotic']:.2f} {r['end_on_source']:.2f} {r['end_diverged']:.2f}")


def print_laws(laws):
    print("  law                     n   rho [95% CI]        p      Holm   LOSO R2 | discovery rho, held-out rho, held-out R2")
    for r in laws:
        star = " (exploratory)" if r["exploratory"] else ""
        print(f"  {r['law']:22s} {r['n']:2d}  {r['rho']:+.2f} [{r['rho_lo']:+.2f},{r['rho_hi']:+.2f}]  {r['p']:.4f} {r['p_holm']:.4f}"
              f"  {r['r2_loso']:+6.2f} | {r.get('rho_discovery', np.nan):+.2f} {r.get('rho_held_out', np.nan):+.2f}"
              f" {r.get('r2_held_out', np.nan):+6.2f}{star}")


COLORS = {"discovery": "#2a78d6", "held-out": "#eb6834"}  # distinguished by marker shape too
INK, MUTED = "#26262a", "#8a8a90"


def figure(path, per_arm):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    arms = list(per_arm)
    panels = [("ratio", r"$\lambda_1/|\lambda_{\min}|$", True), ("d_ky", r"Kaplan-Yorke dimension", False),
              ("lam1_period", r"$\lambda_1 \times$ dominant period", True)]
    fig, axes = plt.subplots(len(arms), len(panels), figsize=(10, 2.9 * len(arms)), sharey=True, squeeze=False)
    for i, arm in enumerate(arms):
        for ax, (col, label, logx) in zip(axes[i], panels):
            for group, color, marker in [("discovery", COLORS["discovery"], "o"), ("held-out", COLORS["held-out"], "s")]:
                rows = [r for r in per_arm[arm] if (r["source"] in HELD_OUT) == (group == "held-out")]
                x = [r[col] for r in rows]
                y = [r["unstable"] for r in rows]
                err = [[r["unstable"] - r["unstable_lo"] for r in rows], [r["unstable_hi"] - r["unstable"] for r in rows]]
                ax.errorbar(x, y, yerr=err, fmt=marker, ms=5, color=color, ecolor=color, elinewidth=1, capsize=0,
                            mec="white", mew=0.8, label=group, zorder=3)
            for r in per_arm[arm]:
                if r["source"] in ("lorenz", "rossler"):
                    ax.annotate(r["source"].capitalize(), (r[col], r["unstable"]), xytext=(5, 5),
                                textcoords="offset points", fontsize=8, color=INK)
            if logx:
                ax.set_xscale("log")
            ax.set_ylim(-0.04, 1.04)
            ax.grid(color="#e6e6ea", lw=0.6)
            ax.set_axisbelow(True)
            ax.spines[["top", "right"]].set_visible(False)
            ax.spines[["left", "bottom"]].set_color(MUTED)
            ax.tick_params(colors=MUTED, labelcolor=INK, labelsize=8)
            ax.set_xlabel(label, fontsize=9, color=INK)
        axes[i, 0].set_ylabel(f"{arm} arm\nunstable fraction", fontsize=9, color=INK)
    axes[0, 0].legend(frameon=False, fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("dir", type=Path)
    p.add_argument("--arms", nargs="+", default=["raw", "lambda", "freq"])
    a = p.parse_args()
    calibration = json.loads((a.dir / "calibration.json").read_text())
    per_arm, all_laws, all_cells = {}, [], {}
    for arm in a.arms:
        path = a.dir / f"scan_{arm}.jsonl"
        recs_by_source = {}
        for name in calibration:
            recs = load([path], name)
            if recs:
                recs_by_source[name] = recs
        rows = [source_row(n, recs, calibration[n]) for n, recs in recs_by_source.items()]
        per_arm[arm] = rows
        write_csv(a.dir / f"sources_{arm}.csv", rows)
        print_sources(arm, rows)
        for field, label in [("unstable", "absolute threshold"), ("unstable_rel", "threshold relative to lambda_1")]:
            laws = law_tests(rows, field)
            print(f"\n  {arm}, {label}: laws for logit(unstable fraction) across sources")
            print_laws(laws)
            all_laws += [{"arm": arm, "threshold": field, **r} for r in laws]
        cells = gamma_cells(recs_by_source, calibration)
        all_cells[arm] = cells
        for col in ("gamma_over_l1", "gamma_period"):
            print(f"  {arm}: cells (source, gamma), {col}: rho %+.2f [%+.2f, %+.2f]" % cell_law(cells, col))
    pooled = [c for cells in all_cells.values() for c in cells]
    if len(all_cells) > 1:
        for col in ("gamma_over_l1", "gamma_period"):
            print(f"pooled over arms, {col}: rho %+.2f [%+.2f, %+.2f]" % cell_law(pooled, col))
    write_csv(a.dir / "laws.csv", all_laws)
    figure(a.dir / "source_laws.png", per_arm)


if __name__ == "__main__":
    main()
