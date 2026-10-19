"""Lyapunov spectra: Lorenz sanity check and the counterexample of the draft."""

import numpy as np
import pytest

from reservoir_sync.driven import drive, settle_source
from reservoir_sync.lyapunov import (
    closed_loop_exponents_driven,
    conditional_exponents,
    source_exponents,
)
from reservoir_sync.reservoirs import LinearReservoir
from reservoir_sync.sources import linear, lorenz
from reservoir_sync.transverse import invariance_leak

DT = 0.01


def test_lorenz_exponents():
    source = lorenz()
    s0 = settle_source(source, DT, 20.0)
    lam = source_exponents(source, s0, DT, 20000)
    assert lam[0] == pytest.approx(0.906, abs=0.15)
    assert lam[1] == pytest.approx(0.0, abs=0.1)
    assert lam[2] == pytest.approx(-14.57, abs=0.3)
    assert lam.sum() == pytest.approx(-(10 + 1 + 8 / 3), abs=0.05)


@pytest.fixture
def counterexample():
    A = np.array([[1.0, 10.0], [-1.0, -3.0]])
    V = np.array([[-10.0], [2.0]])
    N = np.array([[0.0], [1.0]])  # N^T = (0, 1)
    return linear([[-1.0]], s0=[1.0]), LinearReservoir(A, V), N


def test_counterexample_exact_reconstruction(counterexample):
    source, res, N = counterexample
    run = drive(source, res, source.s0, np.array([0.0, 1.0]), DT, 1000)  # phi(s) = (0, s)
    np.testing.assert_allclose(run.R @ N, run.S, atol=1e-12)


def test_counterexample_cles_stable_but_transversely_unstable(counterexample):
    source, res, N = counterexample
    s0, r0 = source.s0, np.array([0.0, 1.0])
    cle = conditional_exponents(source, res, s0, r0, DT, 10000, k=2)
    np.testing.assert_allclose(cle, [-1.0, -1.0], atol=0.05)
    closed = closed_loop_exponents_driven(source, res, N, s0, r0, DT, 10000, k=2)
    np.testing.assert_allclose(closed, [1.0, -1.0], atol=0.05)  # lambda_perp = +1, source -1


def test_invariance_leak():
    source = linear([[-1.0]], s0=[1.0])
    N = np.array([[0.0], [0.0], [1.0]])
    R = np.random.default_rng(0).normal(size=(5, 3))
    S = R @ N
    # W maps ker N^T = span(e1, e2) into itself: no leak
    W_inv = np.array([[-1.0, 2.0, 0.3], [-2.0, -1.0, 0.1], [0.0, 0.0, -1.0]])
    assert invariance_leak(LinearReservoir(W_inv, np.ones((3, 1))), N, R, S) < 1e-12
    # the counterexample leaks
    A = np.array([[1.0, 10.0], [-1.0, -3.0]])
    N2 = np.array([[0.0], [1.0]])
    R2 = np.random.default_rng(1).normal(size=(5, 2))
    leak = invariance_leak(LinearReservoir(A, np.ones((2, 1))), N2, R2, R2 @ N2)
    assert leak == pytest.approx(1 / np.sqrt(2))
