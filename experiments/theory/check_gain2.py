"""Sharper restricted small gain with shift M (section 3.2) and long bubbling runs (section 4.6)."""

import multiprocessing as mp
import sys

import numpy as np
from scipy.linalg import expm

from check_lorenz import Fam, free_chi, g, rk4, settle


def gain_Q0(fam, T=60.0, dt=0.01):
    s = settle()
    Fs = []
    for _ in range(int(T / dt)):
        s = rk4(g, s, dt)
        Fs.append(fam.F(s))
    Fs = np.array(Fs)
    Q0 = np.eye(4) - fam.N @ fam.N.T
    M = fam.N.T @ fam.A @ Q0
    lags = np.arange(0, 3000)
    P = np.array([expm(fam.A * l * dt) for l in lags])
    MP = M @ P
    kappa = -np.linalg.eigvals(fam.A).real.max()
    out = []
    for frac in [0.0, 0.25, 0.5, 0.75, 0.9]:
        sigma = frac * kappa
        vals = []
        for t in range(len(Fs) - 1, len(Fs) - 1 - 2000, -40):
            ls = lags[lags <= t]
            nrm = np.linalg.norm(MP[ls] @ Fs[t - ls], 2, axis=(1, 2))
            vals.append(np.sum(nrm * np.exp(sigma * ls * dt)) * dt)
        out.append((round(sigma, 3), round(max(vals), 3)))
    print(f"E={fam.E} amp={fam.amp} D={fam.D[2]} kappa={kappa:.3f} sup a={fam.E + fam.amp:.3f}: (sigma, gain) {out}")


if __name__ == "__main__":
    for E, amp, D in [(-3.0, 0.5, 0.3), (-1.0, 0.5, 0.3), (-1.0, 3.0, 0.3), (2.0, 0.5, -3.0), (0.5, 0.2, -3.0)]:
        fam = Fam(E=E, amp=amp, D=D)
        gain_Q0(fam)
    tasks = [(-1.0, 3.0, eps, 8000.0, seed) for eps in [1e-5, 1e-4, 1e-3, 1e-2] for seed in [0]] + [(-1.0, 0.5, eps, 8000.0, 0) for eps in [1e-4, 1e-2]]
    with mp.Pool(2) as p:
        for r in p.imap(free_chi, tasks):
            print({k: (np.round(v, 6).tolist() if k == "qs" else v) for k, v in r.items()}, flush=True)
