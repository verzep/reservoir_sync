"""Test of the necessary consequence of Hara-Kokubu hypothesis (H): L_s ||N^T on the normal space of M|| against the contraction margin."""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np

from reservoir_sync.driven import drive, settle_source
from reservoir_sync.readout import fit_readout
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES


def run(name, sig, seed, gamma=20.0, rho=0.5, T_settle=30.0, T=20.0):
    source = SOURCES[name]()
    dt = min(0.01, 0.25 / gamma)
    res = random_reservoir(200, 3, "tanh", rho, sig, 0.5, gamma, None, seed)
    s0 = settle_source(source, dt, 50.0, seed=seed)
    nw, nt = int(20 / dt), int(100 / dt)
    tr = drive(source, res, s0, np.zeros(200), dt, nw + nt)[nw:]
    N = fit_readout(tr.R, tr.S, 1e-6)
    d = 3
    F = N @ np.linalg.inv(N.T @ N)
    z = np.concatenate([tr.S[-1], tr.R[-1]])
    fld = lambda z: np.concatenate([source.g(z[:d]), res.f(z[d:], z[:d])])
    Fo = lambda z, F: res.A_c(z[d:], z[:d]) @ F + res.B(z[d:], z[:d]) - F @ source.Dg(z[:d])
    g_n, g_all, Ls, mu, m = 0.0, 0.0, 0.0, 0.0, 0
    n1 = int(T_settle / dt)
    for i in range(n1 + int(T / dt)):
        a1, b1 = fld(z), Fo(z, F)
        a2, b2 = fld(z + dt / 2 * a1), Fo(z + dt / 2 * a1, F + dt / 2 * b1)
        a3, b3 = fld(z + dt / 2 * a2), Fo(z + dt / 2 * a2, F + dt / 2 * b2)
        a4, b4 = fld(z + dt * a3), Fo(z + dt * a3, F + dt * b3)
        z = z + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        F = F + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        if i > n1 and i % 20 == 0:
            U = np.linalg.qr(F)[0]
            g_n += np.linalg.norm(N.T - (N.T @ U) @ U.T, 2)  # ||N^T (I - U U^T)||
            g_all += np.linalg.norm(N, 2)
            Ls = max(Ls, np.linalg.norm(res.B(z[d:], z[:d]), 2))
            A = res.A_c(z[d:], z[:d])
            mu += np.linalg.eigvalsh((A + A.T) / 2).max()
            m += 1
    gn, ga, mu = g_n / m, g_all / m, mu / m
    print(f"{name} sig={sig} seed={seed}: |N|={ga:.1f} |N on normal|={gn:.1f} L_s={Ls:.2f} mu_2(A)={mu:.2f} L_s|N_n|={Ls * gn:.1f} F finite={np.isfinite(F).all()}", flush=True)


for name, sigs in [("rossler", [0.02, 0.05, 0.1]), ("lorenz", [0.1])]:
    for sig in sigs:
        for seed in range(2):
            run(name, sig, seed)
