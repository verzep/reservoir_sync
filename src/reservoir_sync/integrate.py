"""Fixed-step RK4 integration (fixed steps keep tangent propagation simple)."""

import numpy as np


def rk4_step(F, x, dt):
    k1 = F(x)
    k2 = F(x + 0.5 * dt * k1)
    k3 = F(x + 0.5 * dt * k2)
    k4 = F(x + dt * k3)
    return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(F, x0, dt, n_steps):
    """Trajectory of dx/dt = F(x) with n_steps + 1 rows, starting at x0."""
    x = np.asarray(x0, dtype=float)
    out = np.empty((n_steps + 1, x.size))
    out[0] = x
    for i in range(n_steps):
        x = rk4_step(F, x, dt)
        out[i + 1] = x
    return out


def rk4_tangent_step(F, tangent, x, Y, dt):
    """One RK4 step of dx/dt = F(x) together with dY/dt = tangent(x, Y)."""
    k1, K1 = F(x), tangent(x, Y)
    x2, Y2 = x + 0.5 * dt * k1, Y + 0.5 * dt * K1
    k2, K2 = F(x2), tangent(x2, Y2)
    x3, Y3 = x + 0.5 * dt * k2, Y + 0.5 * dt * K2
    k3, K3 = F(x3), tangent(x3, Y3)
    x4, Y4 = x + dt * k3, Y + dt * K3
    k4, K4 = F(x4), tangent(x4, Y4)
    return (
        x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4),
        Y + dt / 6 * (K1 + 2 * K2 + 2 * K3 + K4),
    )
