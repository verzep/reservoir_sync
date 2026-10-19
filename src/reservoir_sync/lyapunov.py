"""Lyapunov spectra by QR reorthonormalization of propagated tangent vectors.

All spectra are the top k exponents, sorted in decreasing order:

- source: ds/dt = g(s)
- conditional (CLEs): the driven reservoir with the input held fixed, A_c
- closed loop, "driven" base: the closed-loop Jacobian A_c + B N^T evaluated
  along the synchronized (driven) trajectory, i.e. the linearization around
  phi(s(t)). With exact reconstruction its spectrum is the source exponents
  plus the transverse ones.
- closed loop, "free" base: the same Jacobian along the free-running
  trajectory (the Lu-Hunt-Ott diagnostic).
"""

import numpy as np

from .closed_loop import closed_loop_field
from .driven import joint_field
from .integrate import rk4_tangent_step


def lyapunov_spectrum(F, tangent, x0, m, k, dt, n_steps, reortho_every=10, seed=0):
    """Top k exponents of dx/dt = F(x) with tangent dynamics dY/dt = tangent(x, Y).

    m is the tangent-space dimension. Returns (exponents, final state).
    Non-finite trajectories give NaN exponents.
    """
    rng = np.random.default_rng(seed)
    Y = np.linalg.qr(rng.normal(size=(m, k)))[0]
    x = np.asarray(x0, dtype=float).copy()
    logs = np.zeros(k)
    with np.errstate(all="ignore"):
        for i in range(n_steps):
            x, Y = rk4_tangent_step(F, tangent, x, Y, dt)
            if (i + 1) % reortho_every == 0 or i == n_steps - 1:
                if not (np.all(np.isfinite(x)) and np.all(np.isfinite(Y))):
                    return np.full(k, np.nan), x
                Y, Rq = np.linalg.qr(Y)
                logs += np.log(np.abs(np.diag(Rq)))
    return np.sort(logs / (n_steps * dt))[::-1], x


def source_exponents(source, s0, dt, n_steps, k=None, **kw):
    k = source.dim if k is None else k
    return lyapunov_spectrum(
        source.g, lambda s, Y: source.Dg(s) @ Y, s0, source.dim, k, dt, n_steps, **kw
    )[0]


def _split(source):
    d = source.dim
    return lambda z: (z[:d], z[d:])


def conditional_exponents(source, reservoir, s0, r0, dt, n_steps, k, **kw):
    split = _split(source)

    def tangent(z, Y):
        s, r = split(z)
        return reservoir.jvp_r(r, s, Y)

    z0 = np.concatenate([s0, r0])
    F = joint_field(source, reservoir)
    return lyapunov_spectrum(F, tangent, z0, reservoir.n, k, dt, n_steps, **kw)[0]


def _closed_loop_tangent(reservoir, N, r, Y):
    u = r @ N
    return reservoir.jvp_r(r, u, Y) + reservoir.jvp_s(r, u, N.T @ Y)


def closed_loop_exponents_driven(source, reservoir, N, s0, r0, dt, n_steps, k, **kw):
    split = _split(source)

    def tangent(z, Y):
        _, r = split(z)
        return _closed_loop_tangent(reservoir, N, r, Y)

    z0 = np.concatenate([s0, r0])
    F = joint_field(source, reservoir)
    return lyapunov_spectrum(F, tangent, z0, reservoir.n, k, dt, n_steps, **kw)[0]


def closed_loop_exponents_free(reservoir, N, r0, dt, n_steps, k, **kw):
    F = closed_loop_field(reservoir, N)
    tangent = lambda r, Y: _closed_loop_tangent(reservoir, N, r, Y)
    return lyapunov_spectrum(F, tangent, r0, reservoir.n, k, dt, n_steps, **kw)[0]


def extra_exponents(closed_loop, source_exps, tol=0.1):
    """Closed-loop exponents left after removing a match for each source
    exponent >= -tol (the unstable and neutral ones, along which phi stays
    differentiable). The largest leftover estimates the top transverse exponent.
    """
    left = list(closed_loop)
    for lam in source_exps:
        if lam < -tol or not left:
            continue
        j = int(np.argmin([abs(x - lam) for x in left]))
        left.pop(j)
    return np.array(left)
