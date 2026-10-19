"""Closed-loop reservoir dr/dt = G_N(r) = f(r, N^T r) and its source-space field."""

import numpy as np

from .integrate import simulate


def closed_loop_field(reservoir, N):
    return lambda r: reservoir.f(r, r @ N)


def run_autonomous(reservoir, N, r0, dt, n_steps):
    """Free-running reservoir from r0 (n_steps + 1 rows)."""
    return simulate(closed_loop_field(reservoir, N), r0, dt, n_steps)


def field_errors(source, reservoir, N, run):
    """Learned-field error along a driven run, with its decomposition.

    With e = N^T r - s along the synchronized trajectory,

        g_hat - g = e_dot + N^T d,   d = f(r, s + e) - f(r, s),

    where e_dot is the time derivative along the run (no D phi needed). For
    affine input, N^T d = N^T V e.
    """
    S, R = run.S, run.R
    g = source.g(S)
    e = R @ N - S
    e_dot = reservoir.f(R, S) @ N - g
    feedback = (reservoir.f(R, S + e) - reservoir.f(R, S)) @ N
    g_hat = reservoir.f(R, R @ N) @ N
    return {"g": g, "g_hat": g_hat, "e": e, "e_dot": e_dot, "feedback": feedback}


def rms(x):
    return float(np.sqrt(np.mean(np.sum(x**2, axis=-1))))


def summarize_field_errors(fe):
    """RMS norms of the terms, plus the error relative to the RMS of g."""
    err = fe["g_hat"] - fe["g"]
    g_rms = rms(fe["g"])
    return {
        "e_rms": rms(fe["e"]),
        "e_dot_rms": rms(fe["e_dot"]),
        "feedback_rms": rms(fe["feedback"]),
        "field_error_rms": rms(err),
        "field_error_rel": rms(err) / g_rms,
        "decomposition_residual": rms(err - fe["e_dot"] - fe["feedback"]),
    }


def valid_time(S_true, S_pred, dt, threshold=0.4):
    """Time until ||s_pred - s|| / sqrt(<||s||^2>) first exceeds threshold."""
    scale = np.sqrt(np.mean(np.sum(S_true**2, axis=1)))
    err = np.linalg.norm(S_pred - S_true, axis=1) / scale
    bad = np.flatnonzero(~(err <= threshold))  # NaN counts as failure
    return (bad[0] if bad.size else len(err)) * dt
