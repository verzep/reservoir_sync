"""Grid scan over reservoir parameters, in parallel, one JSON line per run.

    python experiments/scan.py --source lorenz --gamma 1 5 20 \\
        --spectral-radius 0.5 0.9 1.2 --input-scale 0.02 0.05 0.1 \\
        --seed 0 1 2 --workers 32 --out results/scan_lorenz.jsonl

Every field of reservoir_sync.experiment.Config takes one or more values; the
grid is their product. Runs already in --out (same config) are skipped, so an
interrupted scan can be restarted with the same command.
"""

import os

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")  # one thread per worker

import argparse
import dataclasses
import itertools
import json
import multiprocessing as mp
import traceback
from pathlib import Path

from reservoir_sync.experiment import Config, run


def _run_safe(cfg):
    try:
        return run(cfg)
    except Exception:
        return {"config": dataclasses.asdict(cfg), "error": traceback.format_exc()}


def parse_grid(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in dataclasses.fields(Config):
        typ = float if f.type == (float | None) else f.type
        parser.add_argument(f"--{f.name.replace('_', '-')}", type=typ, nargs="+", default=[f.default])
    parser.add_argument("--workers", type=int, default=os.cpu_count())
    parser.add_argument("--out", type=Path, required=True)
    args = vars(parser.parse_args(argv))
    workers, out = args.pop("workers"), args.pop("out")
    names = list(args)
    grid = [Config(**dict(zip(names, values))) for values in itertools.product(*args.values())]
    return grid, workers, out


def main():
    grid, workers, out = parse_grid()
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            rec = json.loads(line)
            if "error" not in rec:
                # fill fields added to Config since the record was written
                done.add(json.dumps(dataclasses.asdict(Config(**rec["config"])), sort_keys=True))
    todo = [c for c in grid if json.dumps(dataclasses.asdict(c), sort_keys=True) not in done]
    print(f"{len(grid)} configs, {len(grid) - len(todo)} already done, {len(todo)} to run on {workers} workers")
    with mp.get_context("spawn").Pool(workers) as pool, out.open("a") as fh:
        for i, rec in enumerate(pool.imap_unordered(_run_safe, todo), 1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            status = "ERROR" if "error" in rec else f"valid {rec['valid_time_lyap']:.2f} Lyap, {rec['seconds']:.0f}s"
            print(f"[{i}/{len(todo)}] {status}", flush=True)


if __name__ == "__main__":
    main()
