"""Linear readout s_hat = N^T r, i.e. S_hat = R @ N in time-major arrays."""

import numpy as np


def fit_readout(R, S, beta=0.0, rcond=None, penalty=None):
    """Readout N (n, d) fitted on states R (T, n) and targets S (T, d).

    beta = 0 gives the minimum-norm least-squares solution (N^T = S R^+ in the
    paper's column convention); beta > 0 gives ridge regression. penalty, an
    (n, n) PSD matrix P, adds tr(N^T P N) to the ridge objective.
    """
    if beta == 0 and penalty is None:
        return np.linalg.lstsq(R, S, rcond=rcond)[0]
    n = R.shape[1]
    G = R.T @ R + beta * np.eye(n)
    if penalty is not None:
        G = G + penalty
    return np.linalg.solve(G, R.T @ S)


def feedback_gram(reservoir, R, S, stride=10):
    """sum_t B_t B_t^T over the run (every stride-th step, rescaled), B_t = D_s f(r_t, s_t).

    tr(N^T P N) with this P is sum_t ||N^T B_t||_F^2: the loop gain of the
    source-space feedback, g_hat - g = e_dot + N^T d with d ~ B e.
    """
    idx = range(0, len(R), stride)
    P = sum(reservoir.B(R[i], S[i]) @ reservoir.B(R[i], S[i]).T for i in idx)
    return P * (len(R) / len(idx))


def feedback_gain_rms(reservoir, N, R, S, stride=10):
    """sqrt(<||N^T B_t||_F^2>) over the run."""
    idx = range(0, len(R), stride)
    return float(np.sqrt(np.mean([np.sum((N.T @ reservoir.B(R[i], S[i])) ** 2) for i in idx])))


def nrmse(S_true, S_pred):
    """Root-mean-square error normalized by the per-component standard deviation."""
    return float(np.sqrt(np.mean(((S_pred - S_true) / S_true.std(axis=0)) ** 2)))


def jacobian_gram(reservoir, R, S, stride=10):
    """sum_t A_c(t) A_c(t)^T over the run (every stride-th step, rescaled).

    tr(N^T P N) with this P is sum_t ||N^T A_c(t)||_F^2: how much of the
    reservoir Jacobian's action the readout sees (the transverse coupling,
    cf. transverse.invariance_leak).
    """
    idx = range(0, len(R), stride)
    P = 0
    for i in idx:
        A = reservoir.A_c(R[i], S[i])
        P = P + A @ A.T
    return P * (len(R) / len(idx))


def readout_jacobian_rms(reservoir, N, R, S, stride=10):
    """sqrt(<||N^T A_c(t)||_F^2>) over the run."""
    idx = range(0, len(R), stride)
    return float(np.sqrt(np.mean([np.sum((N.T @ reservoir.A_c(R[i], S[i])) ** 2) for i in idx])))
