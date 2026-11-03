"""Dose response of closed-loop stability to the input bias, 0 to 0.5 plus the matched larger bias.

Paper Sec. 5.2. Needs pandas, which is not a project dependency:

    uv run --locked --with pandas python experiments/bias_dose.py results/source_scan
"""
import json
import sys
import numpy as np, pandas as pd

D = sys.argv[1] if len(sys.argv) > 1 else "results/source_scan"
KEY = ["source", "rho", "sigma", "gamma", "seed"]


def load(path):
    rows = []
    for line in open(path):
        r = json.loads(line)
        c = r["config"]
        if c["source"] == "sprott_jerk" and c["seed"] == 3:
            continue
        rows.append(dict(source=c["source"], rho=c["spectral_radius"], sigma=c["input_scale"], gamma=c["gamma"],
                         seed=c["seed"], bias=c["bias_scale"], perp=r["lambda_perp_driven"],
                         valid=r["valid_time_lyap"], gain=r["feedback_gain_train"], nrmse=r["train_nrmse"], N=r["N_norm"],
                         cle=(r.get("lyap_cle") or [np.nan])[0]))
    return pd.DataFrame(rows)


x = pd.concat([load(f"{D}/scan_bias0.jsonl"), load(f"{D}/scan_smallbias.jsonl"), load(f"{D}/scan_lambda.jsonl"), load(f"{D}/scan_bias.jsonl")])
x["level"] = np.where(x.bias > 0.55, "big", x.bias.map(lambda b: f"{b:g}"))
x["uns"] = (x.perp >= -0.05).astype(float)
order = ["0", "0.01", "0.03", "0.1", "0.2", "0.5", "big"]
n = x.groupby("level").size()
print("runs per level", n.reindex(order).to_dict())

print("\nlevel | unstable (mean over sources) | sources lower than b=0 | median perp | median CLE | median gain | median nrmse | median valid | fail<1 | median readout norm")
u0 = x[x.level == "0"].groupby("source").uns.mean()
for lv in order:
    y = x[x.level == lv]
    us = y.groupby("source").uns.mean()
    print(f"{lv:5s} | {us.mean():.3f} | {(us < u0).sum():2d}/19 | {y.perp.median():+.3f} | {y.cle.median():+.3f} | "
          f"{y.gain.median():6.1f} | {y.nrmse.median():.4f} | {y.valid.median():.2f} | {(y.valid < 1).mean():.3f} | {y.N.median():.0f}")

print("\nper source unstable")
t = x.pivot_table(index="source", columns="level", values="uns", aggfunc="mean")[order]
print(t.round(2).to_string())

for lev in ["sigma", "rho", "gamma"]:
    print(f"\nunstable by {lev}")
    print(x.pivot_table(index=lev, columns="level", values="uns", aggfunc="mean")[order].round(2).to_string())

print("\nlow training error only (nrmse<0.01 in that run)")
y = x[x.nrmse < 0.01]
print(y.groupby("level").agg(n=("uns", "size"), uns=("uns", "mean"), perp=("perp", "median"), valid=("valid", "median")).reindex(order).round(3).to_string())

# bias relative to input drive: does the effect scale with bias/sigma?
print("\nunstable by bias/sigma (small and 0.5 levels)")
z = x[x.level.isin(["0.01", "0.03", "0.1", "0.2", "0.5"])].copy()
z["ratio"] = z.bias / z.sigma
print(z.groupby("ratio").agg(n=("uns", "size"), uns=("uns", "mean"), cle=("cle", "median"), gain=("gain", "median")).round(3).to_string())
