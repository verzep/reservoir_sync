"""One reservoir on one source: training, field errors, prediction and spectra.

    python experiments/run_single.py --source lorenz --n 200 --gamma 1
    python experiments/run_single.py --source rossler --gamma 20 --out results/rossler_g20.json

Every field of reservoir_sync.experiment.Config is a command-line option.
Prints the results as JSON and optionally writes them to --out.
"""

import argparse
import dataclasses
import json
from pathlib import Path

from reservoir_sync.experiment import Config, run


def parse_config(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in dataclasses.fields(Config):
        typ = float if f.type == (float | None) else f.type
        parser.add_argument(f"--{f.name.replace('_', '-')}", type=typ, default=f.default)
    parser.add_argument("--out", type=Path, default=None)
    args = vars(parser.parse_args(argv))
    out = args.pop("out")
    return Config(**args), out


def main():
    cfg, out = parse_config()
    result = run(cfg)
    text = json.dumps(result, indent=2)
    print(text)
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)


if __name__ == "__main__":
    main()
