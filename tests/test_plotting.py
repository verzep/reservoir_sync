"""Shared loading helpers of the analysis and figure scripts."""

import json

import numpy as np

from reservoir_sync.plotting import col, load, read_jsonl


def test_load_filters(tmp_path):
    recs = [{"config": {"source": "lorenz"}, "x": 1.0}, {"config": {"source": "rossler"}, "x": None},
            {"config": {"source": "lorenz"}, "error": "boom"}, {"config": {"source": "lorenz"}, "x": 3.0}]
    path = tmp_path / "scan.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    assert len(read_jsonl(path)) == 4
    assert len(load(path)) == 3
    assert [r["x"] for r in load([path], "lorenz")] == [1.0, 3.0]
    assert len(load(path, keep=lambda r: r["x"] is not None)) == 2
    np.testing.assert_array_equal(col(load(path), lambda r: r["x"]), [1.0, np.nan, 3.0])
