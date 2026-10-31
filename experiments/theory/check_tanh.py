"""Tanh-reservoir checks (section 3, 4.6): loop identity and QA in rate-condition runs,
predictors of failure among transversely stable runs (fixed-point rate, moment exponents).

    python check_tanh.py rossler 54 out.jsonl
"""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import itertools
import json
import multiprocessing as mp
import sys

import numpy as np
from scipy.optimize import fsolve

from reservoir_sync.closed_loop import free_run_end_state, valid_times
from reservoir_sync.driven import drive, settle_source
from reservoir_sync.lyapunov import extra_exponents, source_exponents
from reservoir_sync.readout import fit_readout, nrmse
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES

FIXED = {
    "lorenz": [np.array([0.0, 0.0, 0.0]),
               np.array([np.sqrt(8 / 3 * 27), np.sqrt(8 / 3 * 27), 27.0]),
               np.array([-np.sqrt(8 / 3 * 27), -np.sqrt(8 / 3 * 27), 27.0])],
    "rossler": [np.array([0.0070262, -0.0351310, 0.0351310])],
}
SRC_T = {"lorenz": (0.906, -14.57), "rossler": (0.071, -5.39)}


def qr_exponents(source, res, N, s, r, dt, T, k, window=10.0):
    """Top k exponents of J along the driven orbit with window-wise logs of each QR diagonal."""
    n = res.n
    rng = np.random.default_rng(0)
    Y = np.linalg.qr(rng.normal(size=(n, k)))[0]
    d = source.dim
    Ycle = np.linalg.qr(rng.normal(size=(n, k)))[0]
    logs, logs_c = np.zeros(k), np.zeros(k)
    z = np.concatenate([s, r])
    F = lambda z: np.concatenate([source.g(z[:d]), res.f(z[d:], z[:d])])
    steps = int(T / dt)
    win = int(window / dt)
    W_logs = []
    acc = np.zeros(k)
    tan = lambda z, Y: res.jvp_r(z[d:], z[:d], Y) + res.jvp_s(z[d:], z[:d], N.T @ Y)
    tan_c = lambda z, Y: res.jvp_r(z[d:], z[:d], Y)
    stats = dict(NB=0.0, trNB=0.0, NAK=0.0, ND=0.0, mu2=0.0)
    U = np.linalg.svd(N, full_matrices=True)[0]
    K = U[:, d:]
    m = 0
    for i in range(steps):
        def rhs(z, Y, Yc):
            return F(z), tan(z, Y), tan_c(z, Yc)
        a1, b1, c1 = rhs(z, Y, Ycle)
        a2, b2, c2 = rhs(z + dt / 2 * a1, Y + dt / 2 * b1, Ycle + dt / 2 * c1)
        a3, b3, c3 = rhs(z + dt / 2 * a2, Y + dt / 2 * b2, Ycle + dt / 2 * c2)
        a4, b4, c4 = rhs(z + dt * a3, Y + dt * b3, Ycle + dt * c3)
        z = z + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        Y = Y + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        Ycle = Ycle + dt / 6 * (c1 + 2 * c2 + 2 * c3 + c4)
        if (i + 1) % 10 == 0:
            Y, R = np.linalg.qr(Y)
            l = np.log(np.abs(np.diag(R)))
            logs += l
            acc += l
            Ycle, R = np.linalg.qr(Ycle)
            logs_c += np.log(np.abs(np.diag(R)))
        if (i + 1) % win == 0:
            W_logs.append(acc / window)
            acc = np.zeros(k)
        if i % 100 == 0:
            s_, r_ = z[:d], z[d:]
            B = res.B(r_, s_)
            NB = N.T @ B
            A = res.A_c(r_, s_)
            stats["NB"] += np.linalg.norm(NB)
            stats["trNB"] += np.trace(NB)
            stats["NAK"] += np.linalg.norm(N.T @ A @ K, 2)
            stats["ND"] += np.linalg.norm(N.T * res._dtanh(r_, s_)) * res.gamma
            stats["mu2"] += np.linalg.eigvalsh(K.T @ (A + A.T) @ K / 2).max()
            m += 1
    return (logs / T, logs_c / T, np.array(W_logs), {k_: v / m for k_, v in stats.items()})


def fixed_point_rates(source_name, source, res, N):
    """Max Re of closed-loop Jacobian at phi(s0), source eigenvalues removed; returns per fixed point."""
    out = []
    for s0 in FIXED[source_name]:
        r = np.zeros(res.n)
        for _ in range(4000):
            r = r + 0.01 * res.f(r, s0) if res.gamma < 20 else r + 0.002 * res.f(r, s0)
        r = fsolve(lambda r: res.f(r, s0), r, xtol=1e-10)
        J = res.A_c(r, s0) + res.B(r, s0) @ N.T
        lam = list(np.linalg.eigvals(J))
        for mu in np.linalg.eigvals(source.Dg(s0)):
            j = int(np.argmin(np.abs(np.array(lam) - mu)))
            lam.pop(j)
        e = (N.T @ r - s0)
        out.append(dict(rate=float(np.max(np.real(lam))), e=float(np.linalg.norm(e))))
    return out


def rate_part(source, res, N, s, r, dt, T=150.0, k=4):
    """Rate-condition runs: F forward, QA on ker N^T versus J; the loop identity."""
    n, d = res.n, source.dim
    F = np.linalg.lstsq(np.eye(n)[:d], np.eye(d), rcond=None)[0] * 0  # n x d zeros
    F = N @ np.linalg.inv(N.T @ N)
    z = np.concatenate([s, r])
    fld = lambda z: np.concatenate([source.g(z[:d]), res.f(z[d:], z[:d])])
    Fode = lambda z, F: res.A_c(z[d:], z[:d]) @ F + res.B(z[d:], z[:d]) - F @ source.Dg(z[:d])
    for _ in range(int(40.0 / dt)):
        a1, b1 = fld(z), Fode(z, F)
        a2, b2 = fld(z + dt / 2 * a1), Fode(z + dt / 2 * a1, F + dt / 2 * b1)
        a3, b3 = fld(z + dt / 2 * a2), Fode(z + dt / 2 * a2, F + dt / 2 * b2)
        a4, b4 = fld(z + dt * a3), Fode(z + dt * a3, F + dt * b3)
        z = z + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        F = F + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
    K = np.linalg.svd(N, full_matrices=True)[0][:, d:]
    Y = np.linalg.qr(np.random.default_rng(1).normal(size=(n - d, k)))[0]
    logs = np.zeros(k)
    NF_err, id_err, Fn, gdiff, bound, m = 0.0, 0.0, 0.0, 0.0, 0.0, 0
    def QAt(z, F, Y):
        A = res.A_c(z[d:], z[:d])
        Ft = F @ np.linalg.inv(N.T @ F)
        return K.T @ (A @ (K @ Y) - Ft @ (N.T @ (A @ (K @ Y))))
    for i in range(int(T / dt)):
        a1, b1, c1 = fld(z), Fode(z, F), QAt(z, F, Y)
        a2, b2, c2 = fld(z + dt / 2 * a1), Fode(z + dt / 2 * a1, F + dt / 2 * b1), QAt(z + dt / 2 * a1, F + dt / 2 * b1, Y + dt / 2 * c1)
        a3, b3, c3 = fld(z + dt / 2 * a2), Fode(z + dt / 2 * a2, F + dt / 2 * b2), QAt(z + dt / 2 * a2, F + dt / 2 * b2, Y + dt / 2 * c2)
        a4, b4, c4 = fld(z + dt * a3), Fode(z + dt * a3, F + dt * b3), QAt(z + dt * a3, F + dt * b3, Y + dt * c3)
        z = z + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        F = F + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        Y = Y + dt / 6 * (c1 + 2 * c2 + 2 * c3 + c4)
        if (i + 1) % 10 == 0:
            Y, R = np.linalg.qr(Y)
            logs += np.log(np.abs(np.diag(R)))
        if i % 50 == 0:
            s_, r_ = z[:d], z[d:]
            A, B = res.A_c(r_, s_), res.B(r_, s_)
            G = source.Dg(s_)
            NF_err += np.linalg.norm(N.T @ F - np.eye(d))
            # N^T F' = N^T A F + N^T B - N^T F G, exact for any N; with N^T F = I this is the loop identity
            id_err += np.linalg.norm(N.T @ A @ F + N.T @ B - G) / max(np.linalg.norm(G), 1e-9)
            Fn += np.linalg.norm(F, 2)
            m += 1
    return dict(lam_QA=np.sort(logs / T)[::-1].tolist(), NF_err=NF_err / m, loop_id_rel=id_err / m, F_norm=Fn / m)


def task(args):
    name, gamma, rho, sig, seed = args
    source = SOURCES[name]()
    dt = min(0.01, 0.25 / gamma)
    res = random_reservoir(200, 3, "tanh", rho, sig, 0.5, gamma, None, seed)
    s0 = settle_source(source, dt, 50.0, seed=seed)
    nw, nt, nx = int(20 / dt), int(100 / dt), int(100 / dt)
    run = drive(source, res, s0, np.zeros(200), dt, nw + nt + nx)
    train = run[nw : nw + nt + 1]
    test = run[nw + nt :]
    N = fit_readout(train.R, train.S, 1e-6)
    lam, cle, wins, st = qr_exponents(source, res, N, train.S[-1], train.R[-1], dt, 600.0, 6)
    lams = source_exponents(source, train.S[-1], dt, int(300 / dt))
    extra = extra_exponents(lam, lams)
    # transverse index: largest-in-time QR diagonal not matched to a source exponent
    i_perp = None
    used = set()
    for l in lams:
        if l < -0.1:
            continue
        j = min((j for j in range(6) if j not in used), key=lambda j: abs(lam[j] - l))
        used.add(j)
    order = np.argsort(-wins.mean(0))
    candidates = [j for j in order if np.argmin(np.abs(lam - wins.mean(0)[j])) not in used]
    i_perp = candidates[0] if candidates else order[-1]
    ft = wins[:, i_perp]
    L = {}
    for q in [1, 2, 4, 8]:
        mx = (q * 10 * ft).max()
        L[str(q)] = float((mx + np.log(np.mean(np.exp(q * 10 * ft - mx)))) / 10)
    rec = dict(source=name, gamma=gamma, rho=rho, sigma=sig, seed=seed, train_nrmse=nrmse(train.S, train.R @ N),
               lam=lam.tolist(), cle=cle.tolist(), lams=lams.tolist(), lambda_perp=float(extra[0]) if extra.size else None,
               ft_mean=float(ft.mean()), ft_std=float(ft.std()), ft_max=float(ft.max()), L=L, stats=st,
               fp=fixed_point_rates(name, source, res, N))
    starts = np.linspace(0, len(test.S) - int(25 / dt) - 1, 20).astype(int)
    vt = valid_times(res, N, test, starts, int(25 / dt))
    rec["valid_median_lyap"] = float(np.median(vt) * lams[0])
    with np.errstate(all="ignore"):
        end = free_run_end_state(res, N, train.R[-1], dt, int(1000 / dt), test.S)
    rec["end_class"] = end["class"]
    rec["on_source"] = bool(end["class"] == "bounded" and max(end["nn_to_source"], end["nn_from_source"]) < 0.05)
    rec["end_nn"] = end.get("nn_to_source")
    if cle[0] < lams[-1] and seed < 2:
        rec["rate"] = rate_part(source, res, N, train.S[-1], train.R[-1], dt)
    return rec


if __name__ == "__main__":
    name, seeds, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    grid = list(itertools.product([name], [1.0, 5.0, 20.0], [0.5, 0.9, 1.2], [0.02, 0.05, 0.1], range(seeds)))
    with mp.Pool(4) as p, open(out, "w") as f:
        for r in p.imap_unordered(task, grid):
            f.write(json.dumps(r) + "\n")
            f.flush()
