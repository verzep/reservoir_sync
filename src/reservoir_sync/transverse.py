"""Readout-null directions ker N^T and the invariance condition.

If A_c ker N^T is contained in ker N^T along the trajectory, the closed-loop
Jacobian maps ker N^T into itself (on ker N^T it acts as A_c), and the
transverse exponents are restricted conditional exponents. None of this needs
D phi.
"""

import numpy as np


def readout_bases(N):
    """Orthonormal bases (U_range, K) of range(N) and ker N^T (N has rank d)."""
    d = N.shape[1]
    U = np.linalg.svd(N, full_matrices=True)[0]
    return U[:, :d], U[:, d:]


def invariance_leak(reservoir, N, R, S):
    """Mean over states of ||P_range A_c K||_F / ||A_c K||_F.

    0 when A_c keeps ker N^T invariant; it measures how much of the reservoir
    Jacobian's action on readout-invisible directions leaks into the readout.
    """
    U, K = readout_bases(N)
    leaks = []
    for r, s in zip(R, S):
        M = reservoir.jvp_r(r, s, K)
        leaks.append(np.linalg.norm(U.T @ M) / np.linalg.norm(M))
    return float(np.mean(leaks))
