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


def _flow(name, s0, rhs, jac):
    """Factory of a Source from rhs(*state) -> components and jac(*state) -> rows."""
    s0 = np.array(s0, dtype=float)
    d = s0.size

    def make():
        def g(s):
            return np.stack(rhs(*(s[..., i] for i in range(d))), axis=-1)

        def Dg(s):
            return np.array(jac(*s), dtype=float)

        return Source(name, d, g, Dg, s0)

    return make


# Systems from the dysts collection (Gilpin, NeurIPS Datasets and Benchmarks
# 2021), with its default parameters and initial conditions; equations copied
# from dysts/flows.py, Jacobians checked by finite differences in the tests.
_DYSTS = {
    "shimizu_morioka": _flow(
        "shimizu_morioka", [0.016838697, 0.03489384, 0.35346848],
        lambda x, y, z: (y, x - 0.85 * y - x * z, -0.5 * z + x**2),
        lambda x, y, z: [[0, 1, 0], [1 - z, -0.85, -x], [2 * x, 0, -0.5]],
    ),
    "sprott_jerk": _flow(
        "sprott_jerk", [-0.54106056, 0.59383201, 0.45127217],
        lambda x, y, z: (y, z, -x + y**2 - 2.017 * z),
        lambda x, y, z: [[0, 1, 0], [0, 0, 1], [-1, 2 * y, -2.017]],
    ),
    "genesio_tesi": _flow(
        "genesio_tesi", [-0.053772565, -0.26162564, 0.33501557],
        lambda x, y, z: (y, z, -x - 1.1 * y - 0.44 * z + x**2),
        lambda x, y, z: [[0, 1, 0], [0, 0, 1], [-1 + 2 * x, -1.1, -0.44]],
    ),
    "arneodo": _flow(
        "arneodo", [-2.7515698, 0.19079818, 3.4703629],
        lambda x, y, z: (y, z, 5.5 * x - 4.5 * y - z - x**3),
        lambda x, y, z: [[0, 1, 0], [0, 0, 1], [5.5 - 3 * x**2, -4.5, -1]],
    ),
    "aizawa": _flow(
        "aizawa", [-0.78450179, -0.62887672, -0.17620268],
        lambda x, y, z: (
            x * z - 0.7 * x - 3.5 * y,
            3.5 * x + y * z - 0.7 * y,
            0.6 + 0.95 * z - z**3 / 3 - x**2 - y**2 - 0.25 * z * x**2 - 0.25 * z * y**2 + 0.1 * z * x**3,
        ),
        lambda x, y, z: [
            [z - 0.7, -3.5, x],
            [3.5, z - 0.7, y],
            [-2 * x - 0.5 * z * x + 0.3 * z * x**2, -2 * y - 0.5 * z * y,
             0.95 - z**2 - 0.25 * x**2 - 0.25 * y**2 + 0.1 * x**3],
        ],
    ),
    "hadley": _flow(
        "hadley", [1.3664423, 0.9309146, 0.64283417],
        lambda x, y, z: (-(y**2) - z**2 - 0.2 * x + 1.8, x * y - 4 * x * z - y + 1, 4 * x * y + x * z - z),
        lambda x, y, z: [[-0.2, -2 * y, -2 * z], [y - 4 * z, x - 1, -4 * x], [4 * y + z, 4 * x, x - 1]],
    ),
    "lorenz84": _flow(
        "lorenz84", [1.926479236120359, -0.13402110197257552, -1.72146730664761],
        lambda x, y, z: (-1.32 * x - y**2 - z**2 + 1.32 * 4.83, -y + x * y - 7.91 * x * z + 4.194, -z + 7.91 * x * y + x * z),
        lambda x, y, z: [[-1.32, -2 * y, -2 * z], [y - 7.91 * z, x - 1, -7.91 * x], [7.91 * y + z, 7.91 * x, x - 1]],
    ),
    "rucklidge": _flow(
        "rucklidge", [1.9257158, 3.1923835, 5.7829655],
        lambda x, y, z: (-2 * x + 6.7 * y - y * z, x, -z + y**2),
        lambda x, y, z: [[-2, 6.7 - z, -y], [1, 0, 0], [0, 2 * y, -1]],
    ),
    "halvorsen": _flow(
        "halvorsen", [-8.6807408, -2.4741399, 0.070775762],
        lambda x, y, z: (
            -1.4 * x - 4 * y - 4 * z - y**2,
            -1.4 * y - 4 * z - 4 * x - z**2,
            -1.4 * z - 4 * x - 4 * y - x**2,
        ),
        lambda x, y, z: [[-1.4, -4 - 2 * y, -4], [-4, -1.4, -4 - 2 * z], [-4 - 2 * x, -4, -1.4]],
    ),
    "thomas": _flow(
        "thomas", [2.199442, 2.3634225, 3.220197],
        lambda x, y, z: (-1.85 * x + 10 * np.sin(y), -1.85 * y + 10 * np.sin(z), -1.85 * z + 10 * np.sin(x)),
        lambda x, y, z: [[-1.85, 10 * np.cos(y), 0], [0, -1.85, 10 * np.cos(z)], [10 * np.cos(x), 0, -1.85]],
    ),
    "chen": _flow(
        "chen", [3.2689697, 5.2990458, 19.435349],
        lambda x, y, z: (35 * (y - x), -7 * x - x * z + 28 * y, x * y - 3 * z),
        lambda x, y, z: [[-35, 35, 0], [-7 - z, 28, -x], [y, x, -3]],
    ),
    "qi_chen": _flow(
        "qi_chen", [17.420882, 5.5459627, 78.89139],
        lambda x, y, z: (38 * (y - x) + y * z, 80 * x + y - x * z, x * y - 2.666 * z),
        lambda x, y, z: [[-38, 38 + z, y], [80 - z, 1, -x], [y, x, -2.666]],
    ),
    "lu_chen": _flow(
        "lu_chen", [10.956479, 9.8813092, 22.676714],
        lambda x, y, z: (36 * (y - x), -x * z + 18 * y, x * y - 3 * z),
        lambda x, y, z: [[-36, 36, 0], [-z, 18, -x], [y, x, -3]],
    ),
    "dadras": _flow(
        "dadras", [1.0284085, -3.5348655, -0.72081646],
        lambda x, y, z: (y - 3 * x + 2.7 * y * z, 1.7 * y - x * z + z, 2 * x * y - 9 * z),
        lambda x, y, z: [[-3, 1 + 2.7 * z, 2.7 * y], [-z, 1.7, 1 - x], [2 * y, 2 * x, -9]],
    ),
    "hyper_lorenz": _flow(
        "hyper_lorenz", [-9.186073735061425, -0.6744570634419695, 16.440536886214517, -145.0243848950473],
        lambda x, y, z, w: (10 * (y - x) + w, -x * z + 28 * x - y, -2.667 * z + x * y, 1.1 * w - x * z),
        lambda x, y, z, w: [[-10, 10, 0, 1], [28 - z, -1, -x, 0], [y, x, -2.667, 0], [-z, 0, -x, 1.1]],
    ),
    "lorenz_stenflo": _flow(
        "lorenz_stenflo", [4.233438598886809, 9.08970605484108, 21.86662535600487, -1.4080695182833802],
        lambda x, y, z, w: (2 * (y - x) + 1.5 * w, 26 * x - x * z - y, x * y - 0.7 * z, -x - 2 * w),
        lambda x, y, z, w: [[-2, 2, 0, 1.5], [26 - z, -1, -x, 0], [y, x, -0.7, 0], [-1, 0, 0, -2]],
    ),
    "hyper_xu": _flow(
        "hyper_xu", [0.68944486, -0.60254126, -0.5814657, 0.26629277],
        lambda x, y, z, w: (10 * (y - x) + w, 40 * x + 16 * x * z, -2.5 * z - x * y, x * z - 2 * y),
        lambda x, y, z, w: [[-10, 10, 0, 1], [40 + 16 * z, 0, 16 * x, 0], [-y, -x, -2.5, 0], [z, -2, x, 0]],
    ),
}

SOURCES = {"lorenz": lorenz, "rossler": rossler, **_DYSTS}


def rescaled(source: Source, shift, scale, time_scale: float = 1.0) -> Source:
    """The same flow in y = scale * (s - shift) and t' = t / time_scale.

    dy/dt' = time_scale * scale * g(s). Lyapunov exponents are multiplied by
    time_scale; an invertible affine map leaves them otherwise unchanged.
    """
    shift, scale = np.asarray(shift, dtype=float), np.asarray(scale, dtype=float)

    def g(y):
        return time_scale * scale * source.g(y / scale + shift)

    def Dg(y):
        return time_scale * scale[:, None] * source.Dg(y / scale + shift) / scale

    return Source(source.name, source.dim, g, Dg, scale * (source.s0 - shift))


def make_source(name: str, amplitude: float | None = None, time_scale: float = 1.0) -> Source:
    """Source `name`, optionally centred with component std `amplitude` and sped up by time_scale."""
    source = SOURCES[name]()
    if amplitude is None:
        return source if time_scale == 1.0 else rescaled(source, np.zeros(source.dim), np.ones(source.dim), time_scale)
    stats = ATTRACTOR_STATS[name]
    return rescaled(source, stats["mean"], amplitude / np.asarray(stats["std"]), time_scale)


# Attractor mean and std per component, from experiments/calibrate_sources.py
ATTRACTOR_STATS: dict = {}
