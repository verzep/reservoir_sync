"""Provenance of runs, and the opening figure's lambda_perp computed as in run()."""

import json
import platform

import numpy as np
import pytest
import scipy

from reservoir_sync.experiment import THREAD_VARS, Config, provenance, run


def test_provenance_fields(monkeypatch):
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.delenv("MKL_NUM_THREADS", raising=False)
    p = provenance()
    assert p["python"] == platform.python_version()
    assert p["numpy"] == np.__version__ and p["scipy"] == scipy.__version__
    assert set(p["threads"]) == set(THREAD_VARS)
    assert p["threads"]["OMP_NUM_THREADS"] == "1" and p["threads"]["MKL_NUM_THREADS"] is None
    assert p["git"] is None or isinstance(p["git"], str)


def test_run_records_provenance():
    out = run(Config(n=20, t_washout=2, t_train=10, t_test=4, t_lyap=2, k=2, n_starts=0))
    assert out["provenance"]["numpy"] == np.__version__
    json.dumps(out)  # stays a JSON line


def test_opening_diagnostics_match_run():
    """figures_paper.opening_diagnostics (the opening figure's titles and printed numbers) gives run()'s
    training error, largest CLE, lambda_perp_driven and median valid time."""
    import importlib.util
    from pathlib import Path

    from reservoir_sync.driven import drive, settle_source
    from reservoir_sync.readout import fit_readout
    from reservoir_sync.reservoirs import random_reservoir
    from reservoir_sync.sources import make_source

    path = Path(__file__).parents[1] / "experiments" / "figures_paper.py"
    spec = importlib.util.spec_from_file_location("figures_paper", path)
    figures_paper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(figures_paper)

    cfg = Config(source="rossler", n=20, t_washout=2, t_train=10, t_test=4, t_lyap=3, k=4, n_starts=20, seed=3)
    out = run(cfg)
    source = make_source(cfg.source)
    res = random_reservoir(cfg.n, source.dim, cfg.kind, cfg.spectral_radius, cfg.input_scale,
                           cfg.bias_scale, cfg.gamma, cfg.density, cfg.seed)
    s0 = settle_source(source, cfg.dt, cfg.t_settle, seed=cfg.seed)
    n_wash, n_train = 200, 1000
    full = drive(source, res, s0, np.zeros(res.n), cfg.dt, n_wash + n_train + 400)
    train = full[n_wash : n_wash + n_train + 1]
    N = fit_readout(train.R, train.S, cfg.beta)
    test = full[n_wash + n_train :]
    d = figures_paper.opening_diagnostics(source, res, N, train, test, cfg.dt, cfg.t_lyap, cfg.k)
    assert d["perp"] == pytest.approx(out["lambda_perp_driven"], abs=1e-9)
    assert d["cle_max"] == pytest.approx(out["lyap_cle"][0], abs=1e-9)
    assert d["train_nrmse"] == pytest.approx(out["train_nrmse"], abs=1e-12)
    assert d["valid_median_lyap"] == pytest.approx(out["valid_median_lyap"], abs=1e-9)
