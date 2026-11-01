"""Summaries of check_tanh output."""

import json
import sys

import numpy as np
from scipy.stats import spearmanr


def auc(x, y):
    x, y = np.asarray(x, float), np.asarray(y, bool)
    ok = np.isfinite(x)
    x, y = x[ok], y[ok]
    if y.sum() == 0 or (~y).sum() == 0:
        return float("nan")
    r = np.argsort(np.argsort(x)) + 1
    return (r[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum())


for path in sys.argv[1:]:
    R = [json.loads(l) for l in open(path)]
    R = [r for r in R if r["lambda_perp"] is not None]
    lp = np.array([r["lambda_perp"] for r in R])
    gam = np.array([r["gamma"] for r in R])
    fail = np.array([not r["on_source"] for r in R])
    print(f"== {path}: {len(R)} runs, unstable {np.sum(lp > 0)}, not on source {fail.sum()}")
    stats = {k: np.array([r["stats"][k] for r in R]) for k in R[0]["stats"]}
    cle = np.array([r["cle"][0] for r in R])
    feats = {"cle1": cle, "train": np.log10([r["train_nrmse"] for r in R]), **stats,
             "NAK/gamma": stats["NAK"] / gam, "NB/gamma": stats["NB"] / gam, "trNB/gamma": stats["trNB"] / gam, "mu2/gamma": stats["mu2"] / gam}
    for g in [None, 1.0, 5.0, 20.0]:
        m = np.ones(len(R), bool) if g is None else gam == g
        txt = " ".join(f"{k}:{spearmanr(v[m], lp[m])[0]:+.2f}" for k, v in feats.items())
        print(f" gamma={g} n={m.sum()} Spearman with lambda_perp: {txt}")
    # gap
    print(f" gap lambda_perp - cle1: median {np.median(lp - cle):+.2f}, positive {np.sum(lp > cle)}/{len(R)}")
    st = lp < 0
    print(f" transversely stable {st.sum()}, of which fail {fail[st].sum()}")
    L = {q: np.array([r["L"][q] for r in R]) for q in ["1", "2", "4", "8"]}
    fp = np.array([max(x["rate"] for x in r["fp"]) if r["fp"] else np.nan for r in R])
    ftm = np.array([r["ft_max"] for r in R])
    fts = np.array([r["ft_std"] for r in R])
    for name, x in [("lambda_perp", lp), *[(f"L({q})", L[q]) for q in L], ("ft_max", ftm), ("ft_std", fts), ("fp_rate", fp), ("cle1", cle), ("train", feats["train"])]:
        print(f"  AUC for failure among stable: {name}: {auc(x[st], fail[st]):.3f}")
    print(f"  stable: fp_rate>0 {np.sum(fp[st] > 0)}, fail given fp>0 {fail[st][fp[st] > 0].mean() if np.any(fp[st] > 0) else np.nan:.2f}, fail given fp<=0 {fail[st][fp[st] <= 0].mean() if np.any(fp[st] <= 0) else np.nan:.2f}")
    print(f"  stable: L(2)>0 {np.sum(L['2'][st] > 0)}, fail given L2>0 {fail[st][L['2'][st] > 0].mean() if np.any(L['2'][st] > 0) else np.nan:.2f}, fail given L2<=0 {fail[st][L['2'][st] <= 0].mean() if np.any(L['2'][st] <= 0) else np.nan:.2f}")
    vt = np.array([r["valid_median_lyap"] for r in R])
    for g in [1.0, 5.0, 20.0]:
        m = gam == g
        print(f"  gamma={g} valid time Spearman: lp {spearmanr(lp[m], vt[m])[0]:+.2f} L2 {spearmanr(L['2'][m], vt[m])[0]:+.2f} fp {spearmanr(fp[m], vt[m])[0]:+.2f}")
    # sum-rule certificate on the top exponents is not available here (k = 6); rate-condition runs:
    for r in R:
        if "rate" in r:
            ra = r["rate"]
            print(f"  rate run g={r['gamma']} rho={r['rho']} sig={r['sigma']} seed={r['seed']}: J {np.round(r['lam'][:4], 3)} QA {np.round(ra['lam_QA'][:3], 3)} |N^TF-I| {ra['NF_err']:.2e} loop rel {ra['loop_id_rel']:.2e} |F| {ra['F_norm']:.1f}")
