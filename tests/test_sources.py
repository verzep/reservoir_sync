"""The source collection: Jacobians, rescaling, and the scan's per-source overrides."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from reservoir_sync.lyapunov import source_exponents
from reservoir_sync.sources import ATTRACTOR_STATS, SOURCES, make_source, rescaled
from reservoir_sync.driven import settle_source


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_jacobian_matches_finite_differences(name):
    source = SOURCES[name]()
    s = source.s0 + 0.1
    h = 1e-6
    fd = np.stack([(source.g(s + h * e) - source.g(s - h * e)) / (2 * h) for e in np.eye(source.dim)], axis=1)
    np.testing.assert_allclose(source.Dg(s), fd, rtol=1e-5, atol=1e-5)


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_batch_field_matches_single_state(name):
    source = SOURCES[name]()
    S = np.stack([source.s0, source.s0 + 0.1])
    np.testing.assert_allclose(source.g(S)[1], source.g(S[1]))


def test_rescaled_is_the_conjugate_flow():
    source = SOURCES["lorenz"]()
    shift, scale, tau = np.array([1.0, 2.0, 20.0]), np.array([0.5, 2.0, 0.1]), 3.0
    other = rescaled(source, shift, scale, tau)
    s = np.array([3.0, -1.0, 25.0])
    y = scale * (s - shift)
    np.testing.assert_allclose(other.g(y), tau * scale * source.g(s))
    h = 1e-6
    fd = np.stack([(other.g(y + h * e) - other.g(y - h * e)) / (2 * h) for e in np.eye(3)], axis=1)
    np.testing.assert_allclose(other.Dg(y), fd, rtol=1e-5, atol=1e-5)


def test_time_scale_multiplies_exponents():
    tau = 2.0
    source = make_source("lorenz", time_scale=tau)
    s0 = settle_source(source, 0.005, 10.0)
    lam = source_exponents(source, s0, 0.005, 20000)
    assert lam[0] == pytest.approx(tau * 0.906, abs=0.3)
    assert lam.sum() == pytest.approx(tau * -(10 + 1 + 8 / 3), abs=0.1)


def test_default_source_is_untouched():
    a, b = make_source("rossler"), SOURCES["rossler"]()
    np.testing.assert_array_equal(a.g(a.s0), b.g(b.s0))


def test_amplitude_needs_stats_and_standardizes():
    if "lorenz" not in ATTRACTOR_STATS:
        pytest.skip("no calibration table")
    source = make_source("lorenz", amplitude=6.0)
    stats = ATTRACTOR_STATS["lorenz"]
    np.testing.assert_allclose(source.s0, 6.0 * (SOURCES["lorenz"]().s0 - stats["mean"]) / stats["std"])


def test_scan_per_source_overrides(tmp_path):
    spec = importlib.util.spec_from_file_location("scan", Path(__file__).parents[1] / "experiments" / "scan.py")
    scan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan)
    table = tmp_path / "t.json"
    table.write_text(json.dumps({"rossler": {"t_lyap": 2000.0, "dt": 0.02}}))
    argv = ["--source", "lorenz", "rossler", "--seed", "0", "1", "--out", str(tmp_path / "o.jsonl")]
    grid, _, _ = scan.parse_grid(argv + ["--per-source", str(table)])
    assert len(grid) == 4
    assert {c.t_lyap for c in grid if c.source == "lorenz"} == {200.0}
    assert {(c.t_lyap, c.dt) for c in grid if c.source == "rossler"} == {(2000.0, 0.02)}
    plain, _, _ = scan.parse_grid(argv)
    assert {c.t_lyap for c in plain} == {200.0}
