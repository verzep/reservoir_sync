"""Claim A: at a fixed state error, a faster-changing error gives a worse closed loop.

For each reservoir (gamma, seed), the readout is trained and then perturbed:

- "direction": N = N0 + eps * sigma_s * u w^T, with u a readout direction of
  frequency omega (reservoir_sync.perturbation) and w a fixed unit vector.
  The added state error has rms eps * sigma_s for every omega; its derivative
  scales with omega.
- "beta": no perturbation, ridge parameter beta varied (natural variation).
- "baseline": the trained readout.

Per run: e, e_dot, feedback and field error (train and test), valid time over
many test starts, the closed-loop transverse exponent and ||Delta N||.

    python experiments/claim_a.py --workers 32 --out results/claim_a.jsonl
"""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import argparse
import dataclasses
import itertools
import json
import multiprocessing as mp
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from reservoir_sync.closed_loop import field_errors, free_run_end_state, summarize_field_errors, valid_times
from reservoir_sync.driven import drive, settle_source
from reservoir_sync.lyapunov import (
    closed_loop_exponents_driven,
    closed_loop_exponents_free,
    extra_exponents,
    source_exponents,
)
from reservoir_sync.perturbation import pick_directions, readout_directions
from reservoir_sync.readout import fit_readout, nrmse
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES


@dataclass
class Task:
    kind: str  # "baseline", "direction" or "beta"
    gamma: float
    seed: int
    eps: float = 0.0  # perturbation rms, relative to the source std
    rank: int = 0  # which of the picked directions (slow -> fast)
    beta: float = 1e-6
    source: str = "lorenz"
    n: int = 200
    spectral_radius: float = 0.9
    input_scale: float = 0.05
    bias_scale: float = 0.5
    n_directions: int = 8
    dt: float = 0.01
    t_washout: float = 20.0
    t_train: float = 100.0
    t_test: float = 320.0
    n_starts: int = 30
    t_pred: float = 20.0
    t_lyap: float = 100.0
    k: int = 6
    t_attractor: float = 0.0  # > 0: free run from the synchronized state, end state and exponents


def run_task(t: Task) -> dict:
    t0 = time.time()
    source = SOURCES[t.source]()
    dt = min(t.dt, 0.25 / t.gamma)
    steps = lambda x: int(round(x / dt))
    res = random_reservoir(t.n, source.dim, "tanh", t.spectral_radius, t.input_scale,
                           t.bias_scale, t.gamma, None, t.seed)
    s0 = settle_source(source, dt, 50.0, seed=t.seed)
    n_wash, n_train, n_test = steps(t.t_washout), steps(t.t_train), steps(t.t_test)
    full = drive(source, res, s0, np.zeros(res.n), dt, n_wash + n_train + n_test)
    train, test = full[n_wash : n_wash + n_train + 1], full[n_wash + n_train :]

    N = fit_readout(train.R, train.S, t.beta)
    out = {"task": dataclasses.asdict(t)}
    sigma_s = float(np.mean(train.S.std(axis=0)))
    out["sigma_s"] = sigma_s
    out["source_omega"] = float(np.sqrt(np.mean(np.sum(source.g(train.S) ** 2, 1)))
                                / np.sqrt(np.mean(np.sum((train.S - train.S.mean(0)) ** 2, 1))))
    out["omega"], out["delta_N_norm"] = None, 0.0
    if t.kind == "direction":
        U, omega = readout_directions(train.R, res.f(train.R, train.S))
        idx = pick_directions(omega, t.n_directions)[t.rank]
        w = np.random.default_rng(10_000 + t.seed).normal(size=source.dim)
        w /= np.linalg.norm(w)
        dN = t.eps * sigma_s * np.outer(U[:, idx], w)
        N = N + dN
        out["omega"] = float(omega[idx])
        out["delta_N_norm"] = float(np.linalg.norm(dN))
    out["N_norm"] = float(np.linalg.norm(N))

    out["train_nrmse"] = nrmse(train.S, train.R @ N)
    out["train_field"] = summarize_field_errors(field_errors(source, res, N, train))
    out["test_field"] = summarize_field_errors(field_errors(source, res, N, test))

    n_pred = steps(t.t_pred)
    starts = np.linspace(0, len(test.S) - n_pred - 1, t.n_starts).astype(int)
    vt = valid_times(res, N, test, starts, n_pred)
    lam_src = source_exponents(source, train.S[-1], dt, steps(t.t_lyap))
    out["lambda_1"] = float(lam_src[0])
    vt_lyap = vt * lam_src[0]
    out["valid_mean"], out["valid_median"] = float(vt_lyap.mean()), float(np.median(vt_lyap))
    out["valid_all"] = vt_lyap.tolist()

    lam_cl = closed_loop_exponents_driven(source, res, N, train.S[-1], train.R[-1], dt,
                                          steps(t.t_lyap), t.k)
    extra = extra_exponents(lam_cl, lam_src)
    out["lyap_closed_driven"] = [float(x) for x in lam_cl]
    out["lambda_perp"] = float(extra[0]) if extra.size and np.isfinite(extra[0]) else None
    if t.t_attractor > 0:
        n_attr = steps(t.t_attractor)
        out["end_state"] = free_run_end_state(res, N, train.R[-1], dt, n_attr, test.S)
        with np.errstate(all="ignore"):
            lam_free = closed_loop_exponents_free(res, N, train.R[-1], dt, n_attr, 3)
        out["lyap_closed_free"] = [float(x) if np.isfinite(x) else None for x in lam_free]
    out["seconds"] = time.time() - t0
    return out


def _safe(t):
    try:
        return run_task(t)
    except Exception:
        return {"task": dataclasses.asdict(t), "error": traceback.format_exc()}


def build_tasks(gammas, seeds, eps_list, betas, n_directions, t_attractor=0.0):
    tasks = []
    for g, s in itertools.product(gammas, seeds):
        tasks.append(Task("baseline", g, s, t_attractor=t_attractor))
        tasks += [Task("beta", g, s, beta=b, t_attractor=t_attractor) for b in betas]
        tasks += [Task("direction", g, s, eps=e, rank=r, n_directions=n_directions, t_attractor=t_attractor)
                  for e in eps_list for r in range(n_directions)]
    return tasks


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--gamma", type=float, nargs="+", default=[1.0, 5.0, 20.0])
    p.add_argument("--seed", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--eps", type=float, nargs="+", default=[3e-4, 3e-3, 3e-2])
    p.add_argument("--beta", type=float, nargs="+", default=[1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1.0])
    p.add_argument("--n-directions", type=int, default=8)
    p.add_argument("--t-attractor", type=float, default=0.0,
                   help="> 0: also the free run's end state and exponents over this time")
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    tasks = build_tasks(a.gamma, a.seed, a.eps, a.beta, a.n_directions, a.t_attractor)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if a.out.exists():
        for line in a.out.read_text().splitlines():
            rec = json.loads(line)
            if "error" not in rec:
                done.add(json.dumps(rec["task"], sort_keys=True))
    todo = [t for t in tasks if json.dumps(dataclasses.asdict(t), sort_keys=True) not in done]
    print(f"{len(tasks)} tasks, {len(tasks) - len(todo)} done, {len(todo)} to run on {a.workers} workers", flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool, a.out.open("a") as fh:
        for i, rec in enumerate(pool.imap_unordered(_safe, todo), 1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            msg = "ERROR" if "error" in rec else f"{rec['task']['kind']} valid {rec['valid_mean']:.2f}, {rec['seconds']:.0f}s"
            print(f"[{i}/{len(todo)}] {msg}", flush=True)


if __name__ == "__main__":
    main()
