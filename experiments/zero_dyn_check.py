"""Does lambda_perp equal the top exponent of the zero dynamics where the synchronization map is smooth?

For each scan run passing the rate test (largest conditional exponent below the source's most negative one),
rebuild the reservoir and readout exactly as the scan did, then integrate along the driven orbit:

- the source and reservoir;
- F, the candidate derivative of the synchronization map: dF/dt = A_c F + B - F Dg (converges forward under the rate test);
- k tangent vectors of the closed loop J = A_c + B N^T, giving lambda_perp after removing the source's
  positive and zero exponents (as in the scan);
- k vectors in ker N^T under the zero dynamics d eta/dt = P A_c eta, with P = I - F (N^T F)^{-1} N^T,
  the projection onto ker N^T along range F (equal to Q = I - F N^T when N^T F = I).

Smooth exact theory: spectrum(J) = spectrum(source) + spectrum(zero dynamics).

Paper Sec. 5.6 (zero-dynamics check); from the repository root:

    python experiments/zero_dyn_check.py results/source_scan/scan_lambda.jsonl results/source_scan/zero_dyn.jsonl 40
    python experiments/zero_dyn_analyze.py results/source_scan/zero_dyn.jsonl
"""

import json
import multiprocessing as mp
import os
import sys
import time

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[var] = "1"

import numpy as np

from reservoir_sync.driven import drive, settle_source
from reservoir_sync.experiment import Config, _steps, rate_test_passes
from reservoir_sync.lyapunov import extra_exponents
from reservoir_sync.readout import fit_readout
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import make_source

T_SETTLE, T_MEASURE, K_J, K_Z, REORTHO = 30.0, 150.0, 10, 8, 10


def rebuild(cfg):
    source = make_source(cfg.source, cfg.amplitude, cfg.time_scale, cfg.offset)
    dt = min(cfg.dt, 0.25 / cfg.gamma)
    res = random_reservoir(cfg.n, source.dim, cfg.kind, cfg.spectral_radius, cfg.input_scale,
                           cfg.bias_scale, cfg.gamma, cfg.density, cfg.seed)
    s0 = settle_source(source, dt, cfg.t_settle, seed=cfg.seed)
    n_wash, n_train = _steps(cfg.t_washout, dt), _steps(cfg.t_train, dt)
    full = drive(source, res, s0, np.zeros(res.n), dt, n_wash + n_train)
    train = full[n_wash:]
    N = fit_readout(train.R, train.S, cfg.beta)
    return source, res, N, dt, train.S[-1], train.R[-1]


def compare(rec):
    t0 = time.time()
    c = dict(rec["config"])
    cfg = Config(**{k: v for k, v in c.items() if k in Config.__dataclass_fields__})
    source, res, N, dt, s, r = rebuild(cfg)
    d, n = source.dim, res.n
    rng = np.random.default_rng(0)
    F = N @ np.linalg.inv(N.T @ N)
    Y = np.linalg.qr(rng.normal(size=(n, K_J)))[0]
    K = np.linalg.svd(N.T)[2][d:].T  # orthonormal basis of ker N^T
    Z = np.linalg.qr(K @ rng.normal(size=(n - d, K_Z)))[0]
    S = np.linalg.qr(rng.normal(size=(d, d)))[0]

    def rhs(s, r, F, Y, Z, S, measure):
        A, B, G = res.A_c(r, s), res.B(r, s), source.Dg(s)
        dF = A @ F + B - F @ G
        if not measure:
            return source.g(s), res.f(r, s), dF, None, None, None
        u = r @ N
        Au, Bu = res.A_c(r, u), res.B(r, u)  # closed loop is evaluated at the decoded input
        P = np.eye(n) - F @ np.linalg.solve(N.T @ F, N.T)
        return source.g(s), res.f(r, s), dF, Au @ Y + Bu @ (N.T @ Y), P @ (A @ Z), G @ S

    def step(state, measure):
        k1 = rhs(*state, measure)
        st = lambda k, h: [x + h * dx if dx is not None else x for x, dx in zip(state, k)]
        k2 = rhs(*st(k1, dt / 2), measure)
        k3 = rhs(*st(k2, dt / 2), measure)
        k4 = rhs(*st(k3, dt), measure)
        return [x + dt / 6 * (a + 2 * b + 2 * cc + e) if a is not None else x
                for x, a, b, cc, e in zip(state, k1, k2, k3, k4)]

    state = [s, r, F, Y, Z, S]
    for _ in range(_steps(T_SETTLE, dt)):
        state = step(state, False)
    logs_y, logs_z, logs_s = np.zeros(K_J), np.zeros(K_Z), np.zeros(d)
    defect, m = 0.0, 0
    n_meas = _steps(T_MEASURE, dt)
    with np.errstate(all="ignore"):
        for i in range(n_meas):
            state = step(state, True)
            if (i + 1) % REORTHO == 0:
                s_, r_, F_, Y_, Z_, S_ = state
                if not all(np.all(np.isfinite(x)) for x in state):
                    return dict(config=c, error="nonfinite", at=i * dt)
                Y_, Ry = np.linalg.qr(Y_); logs_y += np.log(np.abs(np.diag(Ry)))
                Z_ = K @ (K.T @ Z_)  # remove round-off drift out of ker N^T
                Z_, Rz = np.linalg.qr(Z_); logs_z += np.log(np.abs(np.diag(Rz)))
                S_, Rs = np.linalg.qr(S_); logs_s += np.log(np.abs(np.diag(Rs)))
                defect += np.linalg.norm(N.T @ F_ - np.eye(d), 2); m += 1
                state = [s_, r_, F_, Y_, Z_, S_]
    T = n_meas * dt
    lam_J = np.sort(logs_y / T)[::-1]
    lam_Z = np.sort(logs_z / T)[::-1]
    lam_S = np.sort(logs_s / T)[::-1]
    extra = extra_exponents(lam_J, lam_S)
    left_all = list(lam_J)
    for lam in lam_S:  # remove all source exponents, negative ones included
        j = int(np.argmin([abs(x - lam) for x in left_all])); left_all.pop(j)
    return dict(config=c, lam_source=lam_S.tolist(), lam_J=lam_J.tolist(), lam_zero=lam_Z.tolist(),
                perp=float(extra[0]), perp_all_removed=float(left_all[0]), perp_scan=rec["lambda_perp_driven"],
                cle_scan=rec["lyap_cle"][0], defect=defect / m, F_norm=float(np.linalg.norm(state[2], 2)),
                seconds=time.time() - t0)


def safe(rec):
    try:
        return compare(rec)
    except Exception as e:  # keep the pool alive
        return dict(config=rec["config"], error=repr(e))


if __name__ == "__main__":
    scan, out = sys.argv[1], sys.argv[2]
    recs = [json.loads(l) for l in open(scan)]
    recs = [r for r in recs if rate_test_passes(r) and r.get("lambda_perp_driven") is not None]
    print(f"{len(recs)} runs", flush=True)
    with mp.Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 40) as p, open(out, "w") as f:
        for i, row in enumerate(p.imap_unordered(safe, recs)):
            f.write(json.dumps(row) + "\n"); f.flush()
            print(f"[{i + 1}/{len(recs)}] {row.get('error', '')} {row.get('seconds', 0):.0f}s", flush=True)
    print("ZERODYN DONE", flush=True)
