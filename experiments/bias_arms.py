"""Paired comparison of the four bias arms of the source scan.

Paper Sec. 5.2. Needs pandas, which is not a project dependency:

    uv run --locked --with pandas python experiments/bias_arms.py results/source_scan
"""
import json, math, sys
import numpy as np, pandas as pd

D = sys.argv[1] if len(sys.argv) > 1 else "results/source_scan"
ARMS = {"b0": f"{D}/scan_bias0.jsonl", "b.5": f"{D}/scan_lambda.jsonl", "off": f"{D}/scan_lambdaoff.jsonl", "big": f"{D}/scan_bias.jsonl"}
KEY = ["source", "rho", "sigma", "gamma", "seed"]


def load(path):
    rows = []
    for line in open(path):
        r = json.loads(line)
        c = r["config"]
        if c["source"] == "sprott_jerk" and c["seed"] == 3:
            continue
        cle = r.get("lyap_cle") or [np.nan]
        rows.append(dict(source=c["source"], rho=c["spectral_radius"], sigma=c["input_scale"], gamma=c["gamma"],
                         seed=c["seed"], perp=r.get("lambda_perp_driven", np.nan), free=r.get("lambda_perp_free", np.nan),
                         valid=r.get("valid_time_lyap", np.nan), gain=r.get("feedback_gain_train", np.nan),
                         nrmse=r.get("train_nrmse", np.nan), cle=cle[0], bias=c["bias_scale"], off=c.get("offset", c.get("input_offset", -1))))
    return pd.DataFrame(rows).set_index(KEY)


d = {a: load(f) for a, f in ARMS.items()}
for a, x in d.items():
    print(a, len(x), "bias", sorted(x.bias.unique()), "off", sorted(x.off.unique()), "sources", x.index.get_level_values(0).nunique())
idx = d["b0"].index
for x in d.values():
    idx = idx.intersection(x.index)
print("paired", len(idx))
d = {a: x.loc[idx] for a, x in d.items()}
for a, x in d.items():
    x["uns"] = np.where(x.perp.notna(), x.perp >= -0.05, np.nan)
    print(a, "missing perp", int(x.perp.isna().sum()))

print("\n=== overall: mean over sources of unstable; medians over runs")
for a, x in d.items():
    print(f"{a:4s} uns {x.groupby('source').uns.mean().mean():.3f} perp {x.perp.median():+.3f} cle {x.cle.median():+.3f} "
          f"gain {x.gain.median():6.1f} nrmse med {x.nrmse.median():.4f} p90 {x.nrmse.quantile(.9):.4f} valid med {x.valid.median():.2f} "
          f"fail(<1) {(x.valid<1).mean():.3f}")

print("\n=== per source: unstable | median valid | median nrmse")
t = pd.DataFrame({f"u_{a}": x.groupby("source").uns.mean() for a, x in d.items()})
for a, x in d.items():
    t[f"v_{a}"] = x.groupby("source").valid.median()
t["n_b0"] = d["b0"].groupby("source").nrmse.median()
t["n_b.5"] = d["b.5"].groupby("source").nrmse.median()
pd.set_option("display.width", 220)
print(t.round(3).to_string())
print("b0 vs b.5 sources lower/higher:", int((t["u_b0"] < t["u_b.5"]).sum()), int((t["u_b0"] > t["u_b.5"]).sum()))
print("mean diff b0-b.5", round((t["u_b0"] - t["u_b.5"]).mean(), 3))

for lev in ["rho", "sigma", "gamma"]:
    print(f"\n=== by {lev}: mean over sources of unstable; median nrmse, gain")
    for v in sorted(idx.get_level_values(lev).unique()):
        s = f"{v:5}"
        for a, x in d.items():
            y = x[x.index.get_level_values(lev) == v]
            s += f" | {a} {y.groupby('source').uns.mean().mean():.2f} n{y.nrmse.median():.4f} g{y.gain.median():6.1f} v{y.valid.median():.2f}"
        print(s)

print("\n=== zero-bias runs: is training itself the problem? unstable and valid by nrmse tercile within b0")
x = d["b0"]
x["q"] = pd.qcut(x.nrmse, 3, labels=["low", "mid", "high"])
print(x.groupby("q", observed=True).agg(nrmse=("nrmse", "median"), uns=("uns", "mean"), valid=("valid", "median"), perp=("perp", "median")).round(3).to_string())
good = d["b0"].nrmse < 0.01
print(f"\nrestricted to runs with b0 nrmse<0.01: n={int(good.sum())}")
for a, y in d.items():
    y = y[good.values]
    print(f"{a:4s} uns {y.uns.mean():.3f} perp {y.perp.median():+.3f} valid {y.valid.median():.2f} gain {y.gain.median():.1f}")

print("\nbootstrap over seeds, b0 minus b.5 in mean-over-source unstable")
seeds = sorted(idx.get_level_values("seed").unique())
rng = np.random.default_rng(0)
u0 = d["b0"].groupby(["seed", "source"]).uns.mean().unstack()
u5 = d["b.5"].groupby(["seed", "source"]).uns.mean().unstack()
diffs = []
for _ in range(2000):
    s = rng.choice(seeds, len(seeds))
    diffs.append((u0.loc[s].mean() - u5.loc[s].mean()).mean())
print(np.percentile(diffs, [2.5, 50, 97.5]).round(3))
