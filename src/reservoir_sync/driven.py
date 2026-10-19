"""Driven reservoir: the source and the reservoir integrated together."""

from dataclasses import dataclass

import numpy as np

from .integrate import simulate


@dataclass
class DrivenRun:
    dt: float
    S: np.ndarray  # (T, d) source states
    R: np.ndarray  # (T, n) reservoir states

    def __getitem__(self, idx):
        return DrivenRun(self.dt, self.S[idx], self.R[idx])


def joint_field(source, reservoir):
    """Vector field of z = (s, r) for the driven reservoir."""
    d = source.dim

    def F(z):
        s, r = z[:d], z[d:]
        return np.concatenate([source.g(s), reservoir.f(r, s)])

    return F


def settle_source(source, dt, t_transient, seed=0):
    """A point on the source attractor: run from a perturbed s0 for t_transient."""
    rng = np.random.default_rng(seed)
    s0 = source.s0 + 0.1 * rng.normal(size=source.dim)
    return simulate(source.g, s0, dt, int(round(t_transient / dt)))[-1]


def drive(source, reservoir, s0, r0, dt, n_steps) -> DrivenRun:
    """Integrate the driven reservoir for n_steps (n_steps + 1 rows)."""
    Z = simulate(joint_field(source, reservoir), np.concatenate([s0, r0]), dt, n_steps)
    return DrivenRun(dt, Z[:, : source.dim], Z[:, source.dim :])
