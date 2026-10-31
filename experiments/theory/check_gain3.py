"""Certification rate of restricted gains, linear case; unstable closed loops with Hurwitz driven block."""

import numpy as np

from check_gain2 import gain_Q0
from check_linear import perp_eigs, random_exact_N, setup
from check_lorenz import Fam

rng = np.random.default_rng(1)
w_grid = np.concatenate([[0.0], np.logspace(-3, 3, 200)])
tot = 300
stats = dict(a=0, a_false=0, M=0, M_false=0, stable=0, T=0)
for _ in range(tot):
    n = rng.integers(4, 12)
    W, V, Phi, L = setup(rng, n)
    N = random_exact_N(rng, Phi, rng.uniform(0, 3))
    uns = perp_eigs(W, Phi, N).real.max() > 0
    stats["stable"] += not uns
    R0 = N @ np.linalg.inv(N.T @ N)
    I = np.eye(n)
    res = [np.linalg.solve(1j * w * I - W, Phi) for w in w_grid]
    best_a = min(max(np.linalg.norm(N.T @ (W + a * I) @ X, 2) for X in res) for a in [0.1, 0.3, 1, 3, 10])
    M = -N.T @ W @ R0
    NWQ = N.T @ W + M @ N.T
    gM = max(np.linalg.norm(NWQ @ X, 2) for X in res)
    stats["a"] += best_a < 1
    stats["a_false"] += (best_a < 1) and uns
    stats["M"] += gM < 1
    stats["M_false"] += (gM < 1) and uns
    # naive gain ||T|| can never be < 1 at the source frequency
    stats["T"] += max(np.linalg.norm(N.T @ np.linalg.solve(1j * w * I - W, V), 2) for w in [1.0]) < 1
print(stats, "of", tot)
for E, amp, D in [(2.0, 0.5, 12.0), (0.5, 0.2, 5.0), (-0.2, 0.1, 0.3)]:
    fam = Fam(E=E, amp=amp, D=D)
    print("eigs A", np.round(np.linalg.eigvals(fam.A), 3))
    gain_Q0(fam)
