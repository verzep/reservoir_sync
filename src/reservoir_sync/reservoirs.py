"""Continuous-time reservoirs dr/dt = f(r, s).

`f` accepts a single state or time-major batches, r (T, n) and s (T, d).
The Jacobian products take a single state:

- `jvp_r(r, s, Y)` = A_c Y with A_c = D_r f(r, s)  (Y has shape (n, k))
- `jvp_s(r, s, X)` = B X   with B   = D_s f(r, s)  (X has shape (d, k))

`affine_V` is the input matrix V when the input enters affinely,
f(r, s) = h(r) + V s, and None otherwise.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class LinearReservoir:
    """f(r, s) = W r + V s."""

    W: np.ndarray
    V: np.ndarray

    @property
    def n(self):
        return self.W.shape[0]

    @property
    def d(self):
        return self.V.shape[1]

    @property
    def affine_V(self):
        return self.V

    def f(self, r, s):
        return r @ self.W.T + s @ self.V.T

    def jvp_r(self, r, s, Y):
        return self.W @ Y

    def jvp_s(self, r, s, X):
        return self.V @ X

    def A_c(self, r, s):
        return self.W

    def B(self, r, s):
        return self.V


@dataclass
class TanhReservoir:
    """f(r, s) = gamma * (-r + tanh(W r + V s + b)).

    The paper's standard reservoir -alpha r + theta(W r + V s) with
    alpha = gamma and theta = gamma tanh (plus a bias).
    """

    W: np.ndarray
    V: np.ndarray
    b: np.ndarray
    gamma: float = 1.0

    @property
    def n(self):
        return self.W.shape[0]

    @property
    def d(self):
        return self.V.shape[1]

    @property
    def affine_V(self):
        return None

    def _pre(self, r, s):
        return r @ self.W.T + s @ self.V.T + self.b

    def f(self, r, s):
        return self.gamma * (-r + np.tanh(self._pre(r, s)))

    def _dtanh(self, r, s):
        return 1.0 - np.tanh(self._pre(r, s)) ** 2

    def jvp_r(self, r, s, Y):
        return self.gamma * (-Y + self._dtanh(r, s)[:, None] * (self.W @ Y))

    def jvp_s(self, r, s, X):
        return self.gamma * self._dtanh(r, s)[:, None] * (self.V @ X)

    def A_c(self, r, s):
        return self.gamma * (-np.eye(self.n) + self._dtanh(r, s)[:, None] * self.W)

    def B(self, r, s):
        return self.gamma * self._dtanh(r, s)[:, None] * self.V


@dataclass
class AffineTanhReservoir:
    """f(r, s) = gamma * (-r + tanh(W r + b)) + V s (affine input coupling)."""

    W: np.ndarray
    V: np.ndarray
    b: np.ndarray
    gamma: float = 1.0

    @property
    def n(self):
        return self.W.shape[0]

    @property
    def d(self):
        return self.V.shape[1]

    @property
    def affine_V(self):
        return self.V

    def f(self, r, s):
        return self.gamma * (-r + np.tanh(r @ self.W.T + self.b)) + s @ self.V.T

    def _dtanh(self, r):
        return 1.0 - np.tanh(r @ self.W.T + self.b) ** 2

    def jvp_r(self, r, s, Y):
        return self.gamma * (-Y + self._dtanh(r)[:, None] * (self.W @ Y))

    def jvp_s(self, r, s, X):
        return self.V @ X

    def A_c(self, r, s):
        return self.gamma * (-np.eye(self.n) + self._dtanh(r)[:, None] * self.W)

    def B(self, r, s):
        return self.V


def random_reservoir(
    n: int,
    d: int,
    kind: str = "tanh",
    spectral_radius: float = 0.9,
    input_scale: float = 0.05,
    bias_scale: float = 0.5,
    gamma: float = 1.0,
    density: float | None = None,
    seed: int = 0,
):
    """Random reservoir of the given kind: "tanh", "affine_tanh" or "linear".

    W is Gaussian (optionally sparse) rescaled to `spectral_radius`, V is
    uniform in [-input_scale, input_scale], b uniform in [-bias_scale, bias_scale].
    The linear reservoir is the leaky one, f = gamma * (-r + W r + V s).
    """
    rng = np.random.default_rng(seed)
    W = rng.normal(size=(n, n))
    if density is not None:
        W *= rng.random((n, n)) < density
    W *= spectral_radius / np.max(np.abs(np.linalg.eigvals(W)))
    V = rng.uniform(-input_scale, input_scale, size=(n, d))
    b = rng.uniform(-bias_scale, bias_scale, size=n)
    if kind == "tanh":
        return TanhReservoir(W, V, b, gamma)
    if kind == "affine_tanh":
        return AffineTanhReservoir(W, V, b, gamma)
    if kind == "linear":
        return LinearReservoir(gamma * (W - np.eye(n)), gamma * V)
    raise ValueError(f"unknown reservoir kind {kind!r}")
