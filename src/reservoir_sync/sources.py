"""Source systems ds/dt = g(s), with their Jacobians.

Arrays are time-major: a trajectory has shape (T, d). `g` accepts a single
state (d,) or a batch (T, d); `Dg` takes a single state.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class Source:
    name: str
    dim: int
    g: Callable[[np.ndarray], np.ndarray]
    Dg: Callable[[np.ndarray], np.ndarray]
    s0: np.ndarray


def lorenz(sigma: float = 10.0, rho: float = 28.0, beta: float = 8 / 3) -> Source:
    """Lorenz 63. Exponents at the default parameters: about 0.906, 0, -14.57."""

    def g(s):
        x, y, z = s[..., 0], s[..., 1], s[..., 2]
        return np.stack([sigma * (y - x), x * (rho - z) - y, x * y - beta * z], axis=-1)

    def Dg(s):
        x, y, z = s
        return np.array([[-sigma, sigma, 0.0], [rho - z, -1.0, -x], [y, x, -beta]])

    return Source("lorenz", 3, g, Dg, np.array([1.0, 1.0, 20.0]))


def rossler(a: float = 0.2, b: float = 0.2, c: float = 5.7) -> Source:
    """Rössler. Exponents at the default parameters: about 0.07, 0, -5.39."""

    def g(s):
        x, y, z = s[..., 0], s[..., 1], s[..., 2]
        return np.stack([-y - z, x + a * y, b + z * (x - c)], axis=-1)

    def Dg(s):
        x, _, z = s
        return np.array([[0.0, -1.0, -1.0], [1.0, a, 0.0], [z, 0.0, x - c]])

    return Source("rossler", 3, g, Dg, np.array([1.0, 1.0, 0.0]))


def linear(A, s0=None) -> Source:
    """Linear source ds/dt = A s."""
    A = np.atleast_2d(np.asarray(A, dtype=float))
    d = A.shape[0]
    s0 = np.ones(d) if s0 is None else np.asarray(s0, dtype=float)
    return Source("linear", d, lambda s: s @ A.T, lambda s: A, s0)


SOURCES = {"lorenz": lorenz, "rossler": rossler}
