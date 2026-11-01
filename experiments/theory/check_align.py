"""Is the leading transverse direction readout-invisible? Representative zeta in ker(L N^T), ratio |N^T zeta| / (|N|_2 |zeta|)."""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import itertools

import numpy as np

from reservoir_sync.driven import drive, settle_source
from reservoir_sync.readout import fit_readout
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES


def one(name, gamma, rho, sig, seed, T=120.0):
    source = SOURCES[name]()
    dt = min(0.01, 0.25 / gamma)
    res = random_reservoir(200, 3, "tanh", rho, sig, 0.5, gamma, None, seed)
    s0 = settle_source(source, dt, 50.0, seed=seed)
    nw, nt = int(20 / dt), int(100 / dt)
    run = drive(source, res, s0, np.zeros(200), dt, nw + nt)
    N = fit_readout(run.R[nw:], run.S[nw:], 1e-6)
    d = 3
    z = np.concatenate([run.S[-1], run.R[-1]])
    F = lambda z: np.concatenate([source.g(z[:d]), res.f(z[d:], z[:d])])
    tan = lambda z, Y: res.jvp_r(z[d:], z[:d], Y) + res.jvp_s(z[d:], z[:d], N.T @ Y)
    Y = np.linalg.qr(np.random.default_rng(0).normal(size=(200, 3)))[0]
    logs = np.zeros(3)
    nn = np.linalg.norm(N, 2)
    ratios, cond = [], []
    n = int(T / dt)
    for i in range(n):
        k1, K1 = F(z), tan(z, Y)
        z2, Y2 = z + dt / 2 * k1, Y + dt / 2 * K1
        k2, K2 = F(z2), tan(z2, Y2)
        z3, Y3 = z + dt / 2 * k2, Y + dt / 2 * K2
        k3, K3 = F(z3), tan(z3, Y3)
        z4, Y4 = z + dt * k3, Y + dt * K3
        k4, K4 = F(z4), tan(z4, Y4)
        z = z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        Y = Y + dt / 6 * (K1 + 2 * K2 + 2 * K3 + K4)
        if (i + 1) % 10 == 0:
            Y, R = np.linalg.qr(Y)
            logs += np.log(np.abs(np.diag(R)))
            if i > n / 2:
                E, q3 = Y[:, :2], Y[:, 2]
                Xi = N.T @ E
                L = np.linalg.pinv(Xi)
                zeta = q3 - E @ (L @ (N.T @ q3))
                ratios.append(np.linalg.norm(N.T @ zeta) / (nn * np.linalg.norm(zeta)))
                cond.append(np.linalg.norm(zeta))
    return logs / (n * dt), float(np.median(ratios)), float(np.median(cond))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    for name, (gamma, rho, sig), seed in itertools.product(["rossler", "lorenz"], [(1.0, 0.9, 0.05), (5.0, 0.9, 0.05), (20.0, 0.5, 0.05), (20.0, 0.9, 0.05)], range(3)):
        lam, r, c = one(name, gamma, rho, sig, seed)
        print(f"{name} g={gamma} rho={rho} seed={seed}: lam {np.round(lam, 3)} |N^T zeta|/(|N||zeta|) {r:.3f} |zeta| {c:.2f}", flush=True)
    print("random-vector baseline for this ratio is about sqrt(3/200)/... ~ 0.1")
