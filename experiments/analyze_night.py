"""Analysis of the scans with multi-start valid times and free-run end states.

    python experiments/analyze_night.py results/night_2026-10-20/rossler_long.jsonl --source rossler

1. Failure rate vs lambda_perp: valid times over the test starts, binned by the
   transverse exponent along the synchronized trajectory.
2. Within-gamma Spearman correlations with the median valid time (and partial
   ones given the training error).
3. Where the free run from the synchronized state ends up, for transversely
   stable and unstable runs, and the sign of the free-run lambda_perp per class.
4. Closed-loop dynamics error (attractor distance, top free-run exponent vs the
   source's) against e, e_dot and the feedback term N^T d.
5. Variants: medians per readout / reservoir variant (kind, n, beta, penalties)
   and gamma; for the penalty and one-at-a-time scans.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

UNSTABLE = -0.05  # lambda_perp threshold, as in analyze_scan.py
FAIL = 1.0  # a start "fails" if its valid time is below one Lyapunov time


def load(paths, source):
    recs = []
    for p in paths:
        for line in Path(p).read_text().splitlines():
            r = json.loads(line)
            if "error" not in r and r["config"]["source"] == source and "valid_times_lyap" in r:
                recs.append(r)
    return recs


def _num(x):
    return np.nan if x is None else float(x)


def _attr_dist(r):
    e = r["end_state"]
    if e["class"] == "diverged":
        return np.inf
    return max(e["nn_to_source"], e["nn_from_source"])


def table(recs):
    col = lambda f: np.array([_num(f(r)) for r in recs])
    tf = lambda r: r["train_field"]
    return {
        "gamma": col(lambda r: r["config"]["gamma"]),
        "valid_med": col(lambda r: r["valid_median_lyap"]),
        "valid_mean": col(lambda r: r["valid_mean_lyap"]),
        "valid_single": col(lambda r: r["valid_time_lyap"]),
        "fail_frac": col(lambda r: np.mean(np.array(r["valid_times_lyap"]) < FAIL)),
        "train_nrmse": col(lambda r: r["train_nrmse"]),
        "e": col(lambda r: tf(r)["e_rms"]),
        "e_dot": col(lambda r: tf(r)["e_dot_rms"]),
        "feedback": col(lambda r: tf(r)["feedback_rms"]),
        "field": col(lambda r: tf(r)["field_error_rel"]),
        "cle_max": col(lambda r: r["lyap_cle"][0]),
        "perp": col(lambda r: r["lambda_perp_driven"]),
        "perp_free": col(lambda r: r["lambda_perp_free"]),
        "free_l1_err": col(lambda r: abs(r["lyap_closed_free"][0] - r["lyap_source"][0])
                           if r["lyap_closed_free"][0] is not None else np.nan),
        "attr_dist": col(_attr_dist),
        "gain_NB": col(lambda r: r.get("feedback_gain_train")),
        "gain_NAc": col(lambda r: r.get("readout_jacobian_train")),
        "leak": col(lambda r: r["invariance_leak"]),
        "N_norm": col(lambda r: r.get("N_norm")),
    }


def within_gamma(T, x, y, mask=None):
    rhos = []
    for g in np.unique(T["gamma"]):
        m = (T["gamma"] == g) & np.isfinite(T[x]) & np.isfinite(T[y])
        if mask is not None:
            m &= mask
        if m.sum() > 5:
            rhos.append(spearmanr(T[x][m], T[y][m])[0])
    return np.array(rhos)


def partial_within_gamma(T, x, y, z):
    def resid(a, b):
        a, b = rankdata(a), rankdata(b)
        return a - np.polyval(np.polyfit(b, a, 1), b)

    rhos = []
    for g in np.unique(T["gamma"]):
        m = (T["gamma"] == g) & np.isfinite(T[x]) & np.isfinite(T[y]) & np.isfinite(T[z])
        if m.sum() > 5:
            rhos.append(spearmanr(resid(T[x][m], T[z][m]), resid(T[y][m], T[z][m]))[0])
    return np.array(rhos)


def _fmt(rhos):
    return " ".join(f"{v:+.2f}" for v in rhos) + f"  | mean {np.nanmean(rhos):+.2f}"


def failure_vs_perp(T, recs):
    print("\n1. Failure rate vs lambda_perp (valid times over the test starts, in Lyapunov times)")
    edges = [-np.inf, -1.0, -0.3, UNSTABLE, 0.3, 1.0, np.inf]
    vts = [np.array(r["valid_times_lyap"]) for r in recs]
    cap = np.median([r["valid_cap_lyap"] for r in recs])
    print(f"   (start fails: valid < {FAIL:g}; cap per start ~{cap:.1f})")
    print("  gamma  lambda_perp bin     runs  fail frac  median valid   q25    q75")
    for g in list(np.unique(T["gamma"])) + [None]:
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (T["perp"] >= lo) & (T["perp"] < hi)
            if g is not None:
                m &= T["gamma"] == g
            if not m.any():
                continue
            v = np.concatenate([vts[i] for i in np.flatnonzero(m)])
            gs = "all" if g is None else f"{g:g}"
            print(f"  {gs:>5}  [{lo:+5.2f}, {hi:+5.2f})  {m.sum():6d}  {np.mean(v < FAIL):9.2f}"
                  f"  {np.median(v):12.2f} {np.quantile(v, .25):6.2f} {np.quantile(v, .75):6.2f}")
    nan = ~np.isfinite(T["perp"])
    if nan.any():
        print(f"  lambda_perp not identified in {nan.sum()} runs (median valid {np.nanmedian(T['valid_med'][nan]):.2f})")


def correlations(T):
    print("\n2. Within-gamma Spearman with the median valid time (per gamma | mean)")
    for x in ["perp", "cle_max", "train_nrmse", "field", "e_dot", "feedback", "perp_free",
              "gain_NB", "gain_NAc", "leak", "N_norm"]:
        if np.isfinite(T[x]).sum() > 10:
            print(f"  {x:12s} {_fmt(within_gamma(T, x, 'valid_med'))}")
    print("  partial given train_nrmse:")
    for x in ["perp", "cle_max", "gain_NAc", "leak"]:
        if np.isfinite(T[x]).sum() > 10:
            print(f"  {x:12s} {_fmt(partial_within_gamma(T, x, 'valid_med', 'train_nrmse'))}")
    print("  single start vs median of 20 (Spearman, within gamma): "
          f"{_fmt(within_gamma(T, 'valid_single', 'valid_med'))}")


def end_states(T, recs):
    print("\n3. End state of the free run from the synchronized state")
    unst = T["perp"] >= UNSTABLE
    for name, m in [("stable", ~unst & np.isfinite(T["perp"])), ("unstable", unst)]:
        c = Counter(r["end_state"]["class"] for r, k in zip(recs, m) if k)
        on = sum(bool(r["end_state"].get("on_source")) for r, k in zip(recs, m) if k)
        print(f"  {name:9s} ({m.sum():4d} runs): " + ", ".join(f"{k} {v}" for k, v in sorted(c.items()))
              + f"; chaotic on the source attractor: {on}")
    print("  per class: runs, median lambda_perp (driven), median lambda_perp (free), frac free > driven,"
          " median valid")
    for cls in ["fixed_point", "periodic", "chaotic", "diverged"]:
        m = np.array([r["end_state"]["class"] == cls for r in recs])
        if not m.any():
            continue
        pf, pd = T["perp_free"][m], T["perp"][m]
        both = np.isfinite(pf) & np.isfinite(pd)
        print(f"  {cls:12s} {m.sum():5d}  {np.nanmedian(pd):+7.2f}  {np.nanmedian(pf) if np.isfinite(pf).any() else np.nan:+7.2f}"
              f"  {np.mean(pf[both] > pd[both]) if both.any() else np.nan:5.2f}  {np.nanmedian(T['valid_med'][m]):6.2f}")
    fp = [np.abs(r["end_state"]["mean_shift"]) for r in recs if r["end_state"]["class"] == "fixed_point"]
    if fp:
        inside = sum(bool(np.all(s < 3)) for s in fp)
        print(f"    fixed points inside the source range (|mean shift| < 3 std per component): {inside}/{len(fp)}")
    for cls in ["chaotic"]:
        m = np.array([r["end_state"]["class"] == cls for r in recs])
        on = np.array([bool(r["end_state"].get("on_source")) for r in recs])
        for name, k in [("on source", m & on), ("elsewhere", m & ~on)]:
            if k.any():
                print(f"    chaotic {name:9s} {k.sum():5d}  attractor dist {np.median(T['attr_dist'][k]):.3f},"
                      f" |lambda1 free - source| {np.nanmedian(T['free_l1_err'][k]):.3f},"
                      f" lambda_perp {np.nanmedian(T['perp'][k]):+.2f}")


def dynamics_error(T):
    print("\n4. Closed-loop dynamics error vs e, e_dot, N^T d (within-gamma Spearman | mean),"
          " runs whose free run stays chaotic and bounded")
    m = np.isfinite(T["attr_dist"]) & np.isfinite(T["free_l1_err"])
    for y in ["attr_dist", "free_l1_err"]:
        for x in ["e", "e_dot", "feedback"]:
            print(f"  {y:11s} ~ {x:8s} {_fmt(within_gamma(T, x, y, m))}")
        print(f"  {y:11s} ~ e_dot | e      {_fmt(partial_within_gamma({k: v[m] for k, v in T.items()}, 'e_dot', y, 'e'))}")
        print(f"  {y:11s} ~ feedback | e   {_fmt(partial_within_gamma({k: v[m] for k, v in T.items()}, 'feedback', y, 'e'))}")


VARIANT_KEYS = ["kind", "n", "beta", "feedback_penalty", "transverse_penalty", "spectral_radius", "input_scale"]


def variants(T, recs):
    keys = [k for k in VARIANT_KEYS if len({r["config"].get(k, 0.0) for r in recs}) > 1]
    if not keys:
        return
    print(f"\n5. Variants ({', '.join(keys)}), per gamma: medians")
    groups = defaultdict(list)
    for i, r in enumerate(recs):
        groups[(r["config"]["gamma"],) + tuple(r["config"].get(k, 0.0) for k in keys)].append(i)
    print(f"  {'gamma':>5} " + " ".join(f"{k[:12]:>12}" for k in keys)
          + "   runs     nrmse  |NB|   |NAc|  perp  unst  fail  valid")
    for key in sorted(groups, key=lambda k: tuple(str(x) for x in k)):
        i = np.array(groups[key])
        unst = np.mean(T["perp"][i] >= UNSTABLE)
        print(f"  {key[0]:5g} " + " ".join(f"{str(v):>12}" for v in key[1:])
              + f"  {len(i):5d}  {np.median(T['train_nrmse'][i]):8.1e}  {np.nanmedian(T['gain_NB'][i]):5.2g}"
              f"  {np.nanmedian(T['gain_NAc'][i]):6.3g}  {np.nanmedian(T['perp'][i]):+5.2f}  {unst:4.2f}"
              f"  {np.mean(T['fail_frac'][i]):4.2f}  {np.median(T['valid_med'][i]):5.2f}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("paths", nargs="+")
    p.add_argument("--source", required=True)
    p.add_argument("--sections", default="12345")
    a = p.parse_args()
    recs = load(a.paths, a.source)
    T = table(recs)
    print(f"{len(recs)} runs ({a.source}); lambda_1 median {np.median([r['lyap_source'][0] for r in recs]):.3f}")
    if "1" in a.sections:
        failure_vs_perp(T, recs)
    if "2" in a.sections:
        correlations(T)
    if "3" in a.sections:
        end_states(T, recs)
    if "4" in a.sections:
        dynamics_error(T)
    if "5" in a.sections:
        variants(T, recs)


if __name__ == "__main__":
    main()
