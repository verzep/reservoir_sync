"""On trained tanh reservoirs: where N^T F - I lives, Lip(e) on data, stable closed-loop fixed points near source fixed points."""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import itertools
import json
import multiprocessing as mp
import sys

import numpy as np
from scipy.optimize import fsolve
from scipy.spatial import cKDTree

from check_tanh import FIXED
from reservoir_sync.driven import drive, settle_source
from reservoir_sync.readout import fit_readout
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES


def lip_e(S, R, N, dt):
    """|e(s)-e(s')|/|s-s'| over nearest neighbours separated in time by > 1 time unit."""
    e = R @ N - S
    idx = np.arange(0, len(S), 5)
    X = S[idx]
    tree = cKDTree(X)
    d, nb = tree.query(X, k=30)
    sep = np.abs(idx[nb] - idx[:, None]) * dt > 1.0
    d2 = np.where(sep, d, np.inf)
    j = np.argmin(d2, axis=1)
    ok = np.isfinite(d2[np.arange(len(X)), j]) & (d2[np.arange(len(X)), j] > 0)
    pairs = nb[np.arange(len(X)), j][ok]
    a = idx[ok]
    b = idx[pairs]
    ratio = np.linalg.norm(e[a] - e[b], axis=1) / np.linalg.norm(S[a] - S[b], axis=1)
    return float(np.median(ratio)), float(np.quantile(ratio, 0.99)), float(ratio.max()), float(np.median(np.linalg.norm(S[a] - S[b], axis=1)))


def defect(source, res, N, s, r, dt, T_settle=30.0, T=60.0):
    """Integrate F forward with a source tangent frame. Report |(N^T F - I) Q| for Q the top-2 and bottom directions."""
    d = source.dim
    F = N @ np.linalg.inv(N.T @ N)
    z = np.concatenate([s, r])
    fld = lambda z: np.concatenate([source.g(z[:d]), res.f(z[d:], z[:d])])
    Fo = lambda z, F: res.A_c(z[d:], z[:d]) @ F + res.B(z[d:], z[:d]) - F @ source.Dg(z[:d])
    Q = np.linalg.qr(np.random.default_rng(0).normal(size=(d, d)))[0]
    To = lambda z, Q: source.Dg(z[:d]) @ Q
    top, bot, flow, fro, m = 0.0, 0.0, 0.0, 0.0, 0
    n1 = int(T_settle / dt)
    for i in range(n1 + int(T / dt)):
        a1, b1, c1 = fld(z), Fo(z, F), To(z, Q)
        z2, F2, Q2 = z + dt / 2 * a1, F + dt / 2 * b1, Q + dt / 2 * c1
        a2, b2, c2 = fld(z2), Fo(z2, F2), To(z2, Q2)
        z3, F3, Q3 = z + dt / 2 * a2, F + dt / 2 * b2, Q + dt / 2 * c2
        a3, b3, c3 = fld(z3), Fo(z3, F3), To(z3, Q3)
        z4, F4, Q4 = z + dt * a3, F + dt * b3, Q + dt * c3
        a4, b4, c4 = fld(z4), Fo(z4, F4), To(z4, Q4)
        z = z + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        F = F + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        Q = Q + dt / 6 * (c1 + 2 * c2 + 2 * c3 + c4)
        if (i + 1) % 10 == 0:
            Q = np.linalg.qr(Q)[0]  # Q[:,:2] spans the leading directions, cu in the hyperbolic picture
        if i > n1 and i % 20 == 0:
            D = N.T @ F - np.eye(d)
            g = source.g(z[:d])
            top += np.linalg.norm(D @ Q[:, :2], 2)
            bot += np.linalg.norm(D @ Q[:, 2:], 2)
            flow += np.linalg.norm(D @ g) / np.linalg.norm(g)
            fro += np.linalg.norm(F, 2)
            m += 1
    return dict(D_top2=top / m, D_rest=bot / m, D_flow=flow / m, F_norm=fro / m)


def closed_fp(name, source, res, N):
    out = []
    G = lambda r: res.f(r, r @ N)
    for s0 in FIXED[name]:
        r = np.zeros(res.n)
        for _ in range(4000):
            r = r + min(0.01, 0.1 / res.gamma) * res.f(r, s0)
        r2, info, ier, _ = fsolve(G, r, xtol=1e-10, full_output=True)
        if ier != 1:
            out.append(dict(found=False))
            continue
        lam = np.linalg.eigvals(res.A_c(r2, r2 @ N) + res.B(r2, r2 @ N) @ N.T)
        out.append(dict(found=True, shift=float(np.linalg.norm(r2 @ N - s0)), maxre=float(lam.real.max())))
    return out


def task(args):
    name, gamma, rho, sig, seed = args
    source = SOURCES[name]()
    dt = min(0.01, 0.25 / gamma)
    res = random_reservoir(200, 3, "tanh", rho, sig, 0.5, gamma, None, seed)
    s0 = settle_source(source, dt, 50.0, seed=seed)
    nw, nt = int(20 / dt), int(100 / dt)
    run = drive(source, res, s0, np.zeros(200), dt, nw + nt)
    train = run[nw:]
    N = fit_readout(train.R, train.S, 1e-6)
    rec = dict(source=name, gamma=gamma, rho=rho, sigma=sig, seed=seed)
    rec["lip"] = lip_e(train.S, train.R, N, dt)
    rec["fp"] = closed_fp(name, source, res, N)
    rec["rate_flag"] = bool(gamma == 20.0 and rho == 0.5)
    if rec["rate_flag"]:
        rec["defect"] = defect(source, res, N, train.S[-1], train.R[-1], dt)
    return rec


if __name__ == "__main__":
    grid = list(itertools.product(["rossler", "lorenz"], [1.0, 5.0, 20.0], [0.5, 0.9, 1.2], [0.02, 0.05, 0.1], range(4)))
    with mp.Pool(8) as p, open("defect.jsonl", "w") as f:
        for r in p.imap_unordered(task, grid):
            f.write(json.dumps(r) + "\n")
            f.flush()
