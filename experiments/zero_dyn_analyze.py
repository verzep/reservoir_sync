"""Summarize zero_dyn.jsonl: closed-loop spectrum vs source + zero dynamics on rate-test runs.

    python experiments/zero_dyn_analyze.py results/source_scan/zero_dyn.jsonl
"""
import collections
import json
import sys

import numpy as np

rows = [json.loads(l) for l in open(sys.argv[1])]
err = [r for r in rows if "error" in r]
ok = [r for r in rows if "error" not in r]
print(f"{len(rows)} runs, {len(err)} errors: {collections.Counter(r['error'][:40] for r in err).most_common(3)}")

top_diff, spec_diff, n_cmp = [], [], []
src_wins = 0
per_src = collections.defaultdict(lambda: [0, 0])
for r in ok:
    J = list(r["lam_J"])
    for lam in r["lam_source"]:  # remove every source exponent
        J.pop(int(np.argmin([abs(x - lam) for x in J])))
    Z = r["lam_zero"]
    m = min(len(J), len(Z), 4)
    top_diff.append(J[0] - Z[0])
    spec_diff.append(max(abs(a - b) for a, b in zip(J[:m], Z[:m])))
    # is the scan's lambda_perp the source's negative exponent rather than a transverse one?
    neg = [x for x in r["lam_source"] if x < -0.1]
    is_src = bool(neg) and Z[0] < r["perp"] - 0.05 and min(abs(r["perp"] - x) for x in neg) < 0.15
    src_wins += is_src
    per_src[r["config"]["source"]][0] += is_src
    per_src[r["config"]["source"]][1] += 1

td, sd = np.abs(top_diff), np.array(spec_diff)
print(f"top transverse: |closed loop minus zero dynamics| median {np.median(td):.3f}, 90% {np.quantile(td, .9):.3f}, max {td.max():.3f}")
print(f"top four, worst pair: median {np.median(sd):.3f}, 90% {np.quantile(sd, .9):.3f}")
print(f"fraction within 0.1 (top): {(td < 0.1).mean():.3f}")
d = np.array([r["defect"] for r in ok])
print(f"|N^T F - I| median {np.median(d):.4f}, 90% {np.quantile(d, .9):.4f}, max {d.max():.3f}")
print(f"scan lambda_perp is the source's negative exponent in {src_wins}/{len(ok)} runs")
for s, (a, b) in sorted(per_src.items()):
    print(f"  {s:16s} {a}/{b}")
rec = np.array([r["perp"] - r["perp_scan"] for r in ok])
print(f"recomputed lambda_perp vs scan: median abs diff {np.median(np.abs(rec)):.3f}")
z0 = np.array([r["lam_zero"][0] for r in ok])
print(f"zero-dynamics top exponent: median {np.median(z0):.2f}; positive in {(z0 > 0).sum()}")

# by exactness of the readout along the orbit, |N^T F - I| (paper Sec. 5.6)
perp = np.array([r["perp"] for r in ok])
print("by |N^T F - I|: runs, median |top closed-loop minus top zero dynamics|, fraction within 0.1, same sign as lambda_perp")
for lo, hi in [(0, .01), (.01, .03), (.03, .1), (.1, .3), (.3, 1), (1, np.inf)]:
    m = (d >= lo) & (d < hi)
    if m.sum():
        print(f"  [{lo}, {hi}): n={m.sum():3d}  median {np.median(td[m]):.3f}  within 0.1 {(td[m] < .1).mean():.2f}  "
              f"same sign {int((np.sign(perp[m]) == np.sign(z0[m])).sum())}/{m.sum()}")
print(f"  beyond 0.1: {int((d >= .1).sum())}/{len(ok)}; sources within 0.01: "
      f"{sorted(set(r['config']['source'] for r, x in zip(ok, d) if x < .01))}")
big = np.argsort(-td)[:5]
for i in big:
    r = ok[i]
    print("  worst:", r["config"]["source"], r["config"]["gamma"], r["config"]["spectral_radius"], "J", [round(x, 2) for x in r["lam_J"][:6]],
          "Z", [round(x, 2) for x in r["lam_zero"][:4]], "src", [round(x, 2) for x in r["lam_source"]], "defect", round(r["defect"], 3))
