"""Readout perturbations that change e_dot at a fixed state error e.

The generalized eigenvectors u of (R_dot^T R_dot, R^T R) are reservoir
directions whose readout signal R u has rms 1 and time derivative of rms
omega. Adding Delta N = eps * u w^T to a trained readout adds the error
delta_e = eps (R u) w^T: its rms is eps for every direction, its derivative
eps * omega. Slow and fast directions therefore give the same state error and
different e_dot.
"""

import numpy as np
from scipy.linalg import eigh


def readout_directions(R, R_dot, reg=1e-10):
    """Directions U (n, n) with rms(R u_i) = 1, and their omega_i = rms(R_dot u_i).

    reg (relative to the mean variance) regularizes R^T R; omega is sorted
    ascending.
    """
    T, n = R.shape
    C0 = R.T @ R / T
    C1 = R_dot.T @ R_dot / T
    C0 += reg * np.trace(C0) / n * np.eye(n)
    _, U = eigh(C1, C0)
    U /= np.sqrt(np.mean((R @ U) ** 2, axis=0))
    omega = np.sqrt(np.mean((R_dot @ U) ** 2, axis=0))
    order = np.argsort(omega)
    return U[:, order], omega[order]


def pick_directions(omega, m, lo=5, hi=95):
    """Indices of m directions with omega log-spaced between two percentiles."""
    targets = np.geomspace(np.percentile(omega, lo), np.percentile(omega, hi), m)
    return np.array([int(np.argmin(np.abs(np.log(omega / t)))) for t in targets])
