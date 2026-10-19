# Reservoir synchronization

What does a reservoir trained to reconstruct states learn once the loop is closed?
Numerics for the draft *Closing the Loop: How State Reconstruction Determines
Autonomous Dynamics*: field errors along the synchronized trajectory, and conditional
vs closed-loop Lyapunov spectra.

## Layout

```
reservoir_sync/
├── src/reservoir_sync/
│   ├── sources.py       Lorenz, Rössler, linear sources (g, Dg)
│   ├── reservoirs.py    linear, tanh and affine-input tanh reservoirs (f, A_c = D_r f, B = D_s f)
│   ├── integrate.py     fixed-step RK4, also for tangent vectors
│   ├── driven.py        driven runs (source + reservoir)
│   ├── readout.py       least-squares / ridge readout N (s_hat = N^T r)
│   ├── closed_loop.py   closed-loop field, free runs, g_hat - g = e_dot + N^T d, valid time
│   ├── lyapunov.py      QR spectra: source, CLEs, closed loop (driven and free base)
│   ├── transverse.py    ker N^T and the invariance leak of A_c
│   └── experiment.py    one train / test / diagnose run (Config, run)
├── experiments/
│   ├── counterexample.py  the 2-d counterexample of the draft
│   ├── run_single.py      one configuration, JSON output
│   └── scan.py            parallel grid scan, one JSON line per run (restartable)
├── notebooks/
└── tests/               the exact identities of the draft, Lorenz exponents, the counterexample
```

Arrays are time-major: trajectories are (T, dim) and the readout is `S_hat = R @ N`.

## Setup

With [uv](https://docs.astral.sh/uv/):

```
$ git clone git@github.com:verzep/reservoir_sync.git
$ cd reservoir_sync
$ uv sync
$ uv run pytest
```

Without uv (e.g. on uranus):

```
$ python3.12 -m venv .venv
$ .venv/bin/pip install -e . pytest
$ .venv/bin/pytest
```

## Running

```
$ .venv/bin/python experiments/counterexample.py
$ .venv/bin/python experiments/run_single.py --source lorenz --n 200 --out results/lorenz.json
$ .venv/bin/python experiments/scan.py --source lorenz rossler --gamma 1 5 20 \
      --spectral-radius 0.5 0.9 1.2 --seed 0 1 2 --workers 32 --out results/scan.jsonl
```

`results/` is git-ignored.
