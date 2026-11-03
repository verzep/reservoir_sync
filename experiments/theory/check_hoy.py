"""Pointwise rate condition of Hunt, Ott, Yorke at embedded fixed points; persistence of -14.57 in perturbed family (F)."""

import json
import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")

import numpy as np

from check_lorenz import Dg, Fam, g, rk4, settle
from check_tanh import FIXED
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import SOURCES


def fixed_point_rate():
    for name, f in [("rossler", "tanh_rossler.jsonl"), ("lorenz", "tanh_lorenz.jsonl")]:
        source = SOURCES[name]()
        R = [json.loads(l) for l in open(f)]
        rr = [r for r in R if r["cle"][0] < r["lams"][-1]]
        n_ok = 0
        for r in rr:
            res = random_reservoir(200, 3, "tanh", r["rho"], r["sigma"], 0.5, r["gamma"], None, r["seed"])
            ok = True
            out = []
            for s0 in FIXED[name]:
                x = np.zeros(200)
                for _ in range(3000):
                    x = x + 0.002 * res.f(x, s0)
                hr = -np.linalg.eigvals(res.A_c(x, s0)).real.max()
                hd = -np.linalg.eigvals(source.Dg(s0)).real.min()
                out.append((round(hr, 2), round(hd, 2)))
                ok &= hr > hd
            n_ok += ok
            print(f" {name} g={r['gamma']} rho={r['rho']} sig={r['sigma']} seed={r['seed']} cle1={r['cle'][0]:.2f}: (h_r, h_d) at fixed points {out}")
        print(f"{name}: typical-point rate condition {len(rr)}/{len(R)}; also holding at every source fixed point {n_ok}")


def perturbed(eps, T=400.0, dt=0.002):
    fam = Fam(E=-1.0, amp=0.5)
    s = settle(dt)
    Y = np.eye(4)
    logs = np.zeros(4)
    for i in range(int(T / dt)):
        B = fam.B(s).copy()
        # f + eps (cos(0.3 s_2), 0, 0, sin(0.3 s_1)): adds a non-matched forcing, so phi is generically Holder
        B[0, 1] += -eps * 0.3 * np.sin(0.3 * s[1])
        B[3, 0] += eps * 0.3 * np.cos(0.3 * s[0])
        J = fam.A + B @ fam.N.T
        Y = Y + dt * J @ (Y + dt / 2 * J @ (Y + dt / 3 * J @ (Y + dt / 4 * J @ Y)))
        s = rk4(g, s, dt)
        if (i + 1) % 25 == 0:
            Y, R = np.linalg.qr(Y)
            logs += np.log(np.abs(np.diag(R)))
    print(f"eps={eps}: J exponents {np.round(np.sort(logs / T)[::-1], 3)}", flush=True)


if __name__ == "__main__":
    fixed_point_rate()
    for eps in [0.0, 0.1, 1.0, 5.0]:
        perturbed(eps)
