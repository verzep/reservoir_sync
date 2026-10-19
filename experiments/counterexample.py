"""The 2-d counterexample of the draft: stable GS, transversely unstable closed loop.

    python experiments/counterexample.py
"""

import numpy as np

from reservoir_sync.lyapunov import closed_loop_exponents_driven, conditional_exponents
from reservoir_sync.reservoirs import LinearReservoir
from reservoir_sync.sources import linear
from reservoir_sync.transverse import invariance_leak

A = np.array([[1.0, 10.0], [-1.0, -3.0]])
V = np.array([[-10.0], [2.0]])
N = np.array([[0.0], [1.0]])
DT, STEPS = 0.01, 20000


def main():
    source, res = linear([[-1.0]], s0=[1.0]), LinearReservoir(A, V)
    s0, r0 = source.s0, np.array([0.0, 1.0])  # phi(s) = (0, s)
    print("eig(A)          ", np.linalg.eigvals(A))
    print("eig(A + V N^T)  ", np.linalg.eigvals(A + V @ N.T))
    print("CLEs            ", conditional_exponents(source, res, s0, r0, DT, STEPS, k=2))
    print("closed loop     ", closed_loop_exponents_driven(source, res, N, s0, r0, DT, STEPS, k=2))
    print("invariance leak ", invariance_leak(res, N, r0[None], s0[None]))


if __name__ == "__main__":
    main()
