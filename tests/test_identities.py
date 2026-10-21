"""Exact identities of the draft, checked on simulated data."""

import numpy as np
import pytest
from scipy.linalg import solve_sylvester

from reservoir_sync.closed_loop import field_errors
from reservoir_sync.driven import drive, settle_source
from reservoir_sync.readout import fit_readout
from reservoir_sync.reservoirs import random_reservoir
from reservoir_sync.sources import linear, lorenz

DT = 0.01


@pytest.fixture(scope="module")
def lorenz_s0():
    return settle_source(lorenz(), DT, 20.0)


def _driven(source, res, s0, n_steps=2000, washout=500):
    run = drive(source, res, s0, np.zeros(res.n), DT, washout + n_steps)
    return run[washout:]


@pytest.mark.parametrize("kind", ["tanh", "affine_tanh", "linear"])
def test_jacobian_products_match_finite_differences(kind):
    res = random_reservoir(12, 3, kind=kind, input_scale=0.3, seed=1)
    rng = np.random.default_rng(0)
    r, s = rng.normal(size=12), rng.normal(size=3)
    Y, X = rng.normal(size=(12, 2)), rng.normal(size=(3, 2))
    h = 1e-6
    fd_r = np.stack([(res.f(r + h * y, s) - res.f(r - h * y, s)) / (2 * h) for y in Y.T], 1)
    fd_s = np.stack([(res.f(r, s + h * x) - res.f(r, s - h * x)) / (2 * h) for x in X.T], 1)
    np.testing.assert_allclose(res.jvp_r(r, s, Y), fd_r, atol=1e-7)
    np.testing.assert_allclose(res.jvp_s(r, s, X), fd_s, atol=1e-7)
    np.testing.assert_allclose(res.A_c(r, s) @ Y, res.jvp_r(r, s, Y), atol=1e-12)
    np.testing.assert_allclose(res.B(r, s) @ X, res.jvp_s(r, s, X), atol=1e-12)


def test_field_error_decomposition(lorenz_s0):
    """g_hat - g = e_dot + N^T d for a general (non-affine) reservoir."""
    source = lorenz()
    res = random_reservoir(50, 3, kind="tanh", seed=2)
    run = _driven(source, res, lorenz_s0)
    N = fit_readout(run.R, run.S, beta=1e-6)
    fe = field_errors(source, res, N, run)
    np.testing.assert_allclose(fe["g_hat"] - fe["g"], fe["e_dot"] + fe["feedback"], atol=1e-8)


def test_affine_identities(lorenz_s0):
    """Affine input: N^T d = N^T V e and R_dot - G_N(R) = V (S - N^T R)."""
    source = lorenz()
    res = random_reservoir(40, 3, kind="affine_tanh", seed=3)
    run = _driven(source, res, lorenz_s0)
    N = fit_readout(run.R, run.S, beta=1e-6)
    fe = field_errors(source, res, N, run)
    V = res.affine_V
    np.testing.assert_allclose(fe["feedback"], fe["e"] @ V.T @ N, atol=1e-8)
    lhs = res.f(run.R, run.S) - res.f(run.R, run.R @ N)
    np.testing.assert_allclose(lhs, (run.S - run.R @ N) @ V.T, atol=1e-8)


def test_ridge_readout_is_regularized_dmd_toward_W(lorenz_s0):
    """W + V N^T = R_dot R^T C^-1 + beta W C^-1, C = R R^T + beta I (column form)."""
    source = lorenz()
    res = random_reservoir(20, 3, kind="linear", spectral_radius=0.5, input_scale=0.1, seed=4)
    run = _driven(source, res, lorenz_s0)
    beta = 1e-2
    N = fit_readout(run.R, run.S, beta=beta)
    R, R_dot = run.R, res.f(run.R, run.S)
    C_inv = np.linalg.inv(R.T @ R + beta * np.eye(res.n))
    expected = R_dot.T @ R @ C_inv + beta * res.W @ C_inv
    np.testing.assert_allclose(res.W + res.V @ N.T, expected, rtol=1e-6, atol=1e-8)  # C is ill-conditioned


def test_least_squares_readout_is_dmd(lorenz_s0):
    """Full row rank: W + V N^T = R_dot R^+ (continuous-time DMD)."""
    source = lorenz()
    res = random_reservoir(6, 3, kind="linear", spectral_radius=0.5, input_scale=0.1, seed=5)
    run = _driven(source, res, lorenz_s0, n_steps=5000)
    assert np.linalg.matrix_rank(run.R) == res.n
    N = fit_readout(run.R, run.S)
    R_dot = res.f(run.R, run.S)
    dmd = R_dot.T @ np.linalg.pinv(run.R.T)
    closed = res.W + res.V @ N.T
    assert np.linalg.norm(closed - dmd) / np.linalg.norm(dmd) < 1e-6


def test_rank_deficient_readout_keeps_W_off_the_data():
    """Linear source, phi(s) = Phi s: W + V N^T = R_dot R^+ + W (I - R R^+)."""
    A = np.array([[-0.1, 1.0], [-1.0, -0.1]])
    source = linear(A, s0=[1.0, 0.0])
    res = random_reservoir(6, 2, kind="linear", spectral_radius=0.5, input_scale=1.0, seed=6)
    Phi = solve_sylvester(res.W, -A, -res.V)  # W Phi - Phi A = -V
    run = drive(source, res, source.s0, Phi @ source.s0, DT, 1000)
    np.testing.assert_allclose(run.R, run.S @ Phi.T, atol=1e-10)  # sync map
    R, R_dot = run.R, res.f(run.R, run.S)
    R_pinv = np.linalg.pinv(R.T, rcond=1e-10)  # pseudo-inverse of the (n, T) matrix
    N = (run.S.T @ R_pinv).T
    np.testing.assert_allclose(R @ N, run.S, atol=1e-8)  # exact reconstruction
    expected = R_dot.T @ R_pinv + res.W @ (np.eye(res.n) - R.T @ R_pinv)
    np.testing.assert_allclose(res.W + res.V @ N.T, expected, atol=1e-8)


def test_feedback_penalty_lowers_loop_gain():
    from reservoir_sync.driven import drive, settle_source
    from reservoir_sync.readout import feedback_gain_rms, feedback_gram, fit_readout
    from reservoir_sync.reservoirs import random_reservoir
    from reservoir_sync.sources import lorenz

    source = lorenz()
    res = random_reservoir(40, 3, "tanh", 0.9, 0.05, 0.5, 1.0, None, 0)
    run = drive(source, res, settle_source(source, 0.01, 20.0), np.zeros(40), 0.01, 3000)
    P = feedback_gram(res, run.R, run.S, stride=1)
    B = [res.B(r, s) for r, s in zip(run.R, run.S)]
    np.testing.assert_allclose(P, sum(b @ b.T for b in B), rtol=1e-10)
    gains = [feedback_gain_rms(res, fit_readout(run.R, run.S, 1e-6, penalty=mu * P), run.R, run.S)
             for mu in (0.0, 1e-4, 1e-2)]
    assert gains[0] > gains[1] > gains[2]


def test_jacobian_gram():
    from reservoir_sync.readout import jacobian_gram, readout_jacobian_rms
    from reservoir_sync.reservoirs import random_reservoir

    res = random_reservoir(20, 3, "tanh", 0.9, 0.05, 0.5, 2.0, None, 0)
    rng = np.random.default_rng(1)
    R, S, N = rng.normal(size=(50, 20)), rng.normal(size=(50, 3)), rng.normal(size=(20, 3))
    P = jacobian_gram(res, R, S, stride=1)
    np.testing.assert_allclose(np.trace(N.T @ P @ N) / 50, readout_jacobian_rms(res, N, R, S, stride=1) ** 2)
