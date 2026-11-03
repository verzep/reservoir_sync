"""Every run records the code version, library versions and BLAS thread settings."""

import json
import platform

import numpy as np
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
