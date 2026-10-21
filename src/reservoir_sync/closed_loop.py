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


def valid_time(S_true, S_pred, dt, threshold=0.4, scale=None):
    """Time until ||s_pred - s|| / scale first exceeds threshold.

    scale defaults to sqrt(<||s||^2>) over S_true.
    """
    if scale is None:
        scale = np.sqrt(np.mean(np.sum(S_true**2, axis=1)))
    err = np.linalg.norm(S_pred - S_true, axis=1) / scale
    bad = np.flatnonzero(~(err <= threshold))  # NaN counts as failure
    return (bad[0] if bad.size else len(err)) * dt


def valid_times(reservoir, N, run, starts, n_pred, threshold=0.4):
    """Valid times of free runs started from the driven states run.R[i], i in starts."""
    scale = np.sqrt(np.mean(np.sum(run.S**2, axis=1)))
    out = []
    with np.errstate(all="ignore"):
        for i in starts:
            free = run_autonomous(reservoir, N, run.R[i], run.dt, n_pred)
            out.append(valid_time(run.S[i : i + n_pred + 1], free @ N, run.dt, threshold, scale))
    return np.array(out)


def free_run_end_state(reservoir, N, r0, dt, n_steps, S_ref, n_points=2000, seed=0):
    """Where the free run from r0 ends up, compared with the source attractor S_ref.

    Uses the second half of the run (s_hat = N^T r). Returns the class
    ("diverged", "fixed_point" or "bounded") and attractor statistics:

    - nn_to_source / nn_from_source: median distance from free-run points to
      the nearest S_ref point and back, relative to the rms of S_ref around its
      mean; both small means the free run covers the source attractor;
    - mean_shift, std_ratio: per-component mean difference (relative to the
      S_ref std) and std ratio;
    - recurrence: closest return to the final point earlier in the second half,
      in units of the largest step |s_hat(t + dt) - s_hat(t)| (<~ 1 on a cycle).
    """
    with np.errstate(all="ignore"):
        R = run_autonomous(reservoir, N, r0, dt, n_steps)
        S = R[len(R) // 2 :] @ N
    mu, sd = S_ref.mean(0), S_ref.std(0)
    scale = float(np.sqrt(np.mean(np.sum((S_ref - mu) ** 2, axis=1))))
    out = {"t": n_steps * dt}
    if not np.all(np.isfinite(S)) or np.max(np.abs(S - mu)) > 1e3 * scale:
        out["class"] = "diverged"
        return out
    spread = float(np.sqrt(np.mean(np.sum((S - S.mean(0)) ** 2, axis=1)))) / scale
    out["spread"] = spread
    out["mean_shift"] = ((S.mean(0) - mu) / sd).tolist()
    out["std_ratio"] = (S.std(0) / sd).tolist()
    rng = np.random.default_rng(seed)
    A = S[rng.choice(len(S), min(n_points, len(S)), replace=False)]
    B = S_ref[rng.choice(len(S_ref), min(n_points, len(S_ref)), replace=False)]
    D = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)) / scale
    out["nn_to_source"] = float(np.median(D.min(1)))
    out["nn_from_source"] = float(np.median(D.min(0)))
    # recurrence of the final point, skipping the last 5% (its own neighbourhood)
    step = float(np.max(np.linalg.norm(np.diff(S, axis=0), axis=1)))
    d_last = np.linalg.norm(S[: int(0.95 * len(S))] - S[-1], axis=1)
    out["recurrence"] = float(d_last.min() / step) if step > 0 else 0.0
    out["class"] = "fixed_point" if spread < 1e-3 else "bounded"
    return out
