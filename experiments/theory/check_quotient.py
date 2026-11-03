"""Non-differentiable quotient form Q_E J on ker(L N^T), with k < d; forecast bound with the transverse split."""

import numpy as np
from scipy.linalg import null_space

from check_lorenz import Fam, g, rk4, settle


def quotient_linear(rng, trials=200):
    worst, worst_sum = 0.0, 0.0
    for _ in range(trials):
        n = rng.integers(5, 13)
        W = rng.normal(size=(n, n)) / np.sqrt(n)
        W -= (np.linalg.eigvals(W).real.max() + 0.5) * np.eye(n)
        # source: oscillator (D) + stable mode -mu (S), stable mode not reconstructed
        mu = rng.uniform(0.5, 20)
        L0 = np.zeros((3, 3)); L0[0, 1] = 1; L0[1, 0] = -1; L0[2, 2] = -mu
        T = rng.normal(size=(3, 3))
        Ls = T @ L0 @ np.linalg.inv(T)
        Xi, S = T[:, :2], T[:, 2:]
        Li = np.linalg.inv(T)[:2, :]  # L Xi = I, ker L = S
        # exact on D only: Y solves W Y + V Xi = Y L_D with N^T Y = Xi, V and N otherwise free
        Y = rng.normal(size=(n, 2))
        V = rng.normal(size=(n, 3))
        V = V - V @ Xi @ Li + (Y @ L0[:2, :2] - W @ Y) @ Li
        N = (Y @ np.linalg.inv(Y.T @ Y) @ Xi.T + null_space(Y.T) @ rng.normal(size=(n - 2, 3)))
        assert np.linalg.norm(N.T @ Y - Xi) < 1e-9
        J = W + V @ N.T
        lam = np.linalg.eigvals(J)
        Wbasis = null_space(Li @ N.T)  # n-2 dim
        QE = np.eye(n) - Y @ Li @ N.T
        Jq = Wbasis.T @ QE @ J @ Wbasis
        q = np.linalg.eigvals(Jq)
        rest = list(lam)
        for z in [1j, -1j]:
            rest.pop(int(np.argmin(np.abs(np.array(rest) - z))))
        err = 0.0
        for z in q:
            j = int(np.argmin(np.abs(np.array(rest) - z)))
            err = max(err, abs(rest[j] - z)); rest.pop(j)
        worst = max(worst, err)
        worst_sum = max(worst_sum, abs(q.sum() - (np.trace(W) + np.trace(N.T @ V))))
    print(f"quotient form: spectrum err {worst:.2e}; sum rule without smoothness err {worst_sum:.2e}")


def valid_time(fam, eps, seed, dt=0.002, Tmax=40.0, thr=2.0):
    b = np.ones(3) / np.sqrt(3)
    s = settle(dt, T=20.0, seed=seed)
    x = np.concatenate([s, [fam.h(s[2])]])
    fun = lambda x: fam.f(x, x[:3] + eps * b * x[3])
    for i in range(int(Tmax / dt)):
        x = rk4(fun, x, dt); s = rk4(g, s, dt)
        if np.linalg.norm(x[:3] - s) > thr or not np.all(np.isfinite(x)):
            return i * dt
    return Tmax


if __name__ == "__main__":
    quotient_linear(np.random.default_rng(0))
    for E, amp, D in [(-1.0, 0.5, 0.3), (-0.1, 0.05, 0.3), (0.5, 0.2, 5.0)]:
        fam = Fam(E=E, amp=amp, D=D)
        row = []
        for eps in [1e-6, 1e-4, 1e-2]:
            row.append((eps, round(float(np.median([valid_time(fam, eps, sd) for sd in range(12)])), 2)))
        print(f"E={E} amp={amp}: (eps, median time to |s_hat - s| > 2) {row}", flush=True)
