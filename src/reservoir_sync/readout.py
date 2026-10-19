"""Linear readout s_hat = N^T r, i.e. S_hat = R @ N in time-major arrays."""

import numpy as np


def fit_readout(R, S, beta=0.0, rcond=None):
    """Readout N (n, d) fitted on states R (T, n) and targets S (T, d).

    beta = 0 gives the minimum-norm least-squares solution (N^T = S R^+ in the
    paper's column convention); beta > 0 gives ridge regression.
    """
    if beta == 0:
        return np.linalg.lstsq(R, S, rcond=rcond)[0]
    n = R.shape[1]
    return np.linalg.solve(R.T @ R + beta * np.eye(n), R.T @ S)


def nrmse(S_true, S_pred):
    """Root-mean-square error normalized by the per-component standard deviation."""
    return float(np.sqrt(np.mean(((S_pred - S_true) / S_true.std(axis=0)) ** 2)))
