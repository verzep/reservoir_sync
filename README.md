# reservoir_sync

Code for the paper *Learn to Synchronize, Fail to Predict: What Training Cannot See in Surrogates of Chaotic
Systems* (Pietro Verzelli).

A reservoir (or any surrogate) driven by a chaotic source and trained to reconstruct its state is then run in
closed loop, its decoded output fed back as input. The code computes what training sees (training error, conditional
Lyapunov exponents) and what decides the free run: the closed-loop spectrum along the synchronized trajectory and the
transverse exponent λ⊥, together with valid times and the end state of the free run.

**To reproduce the paper's figures and numbers, see [REPRODUCE.md](REPRODUCE.md).**

## Install

With [uv](https://docs.astral.sh/uv/) (the lock file pins every version):

```
git clone https://github.com/verzep/reservoir_sync.git
cd reservoir_sync
uv sync --locked
uv run pytest            # under a minute
```

Without uv: `python3.12 -m venv .venv && .venv/bin/pip install -e . pytest` (versions not pinned).

## Run

One configuration with a small reservoir, JSON output:

```
uv run python experiments/run_single.py --source lorenz --n 50 --out results/lorenz.json
```

A grid scan, one JSON line per run, in parallel and restartable:

```
uv run python experiments/scan.py --source lorenz rossler --gamma 1 5 20 \
    --spectral-radius 0.5 0.9 1.2 --seed 0 1 2 --workers 8 --out results/scan.jsonl
```

Every field of `reservoir_sync.experiment.Config` is a command-line option (`--help` lists them). Each record stores
its configuration and its provenance (git commit, library versions, BLAS thread settings). `results/` is not tracked.

## Layout

```
src/reservoir_sync/
  sources.py       Lorenz, Rössler, 17 systems of the dysts collection (equations copied), linear sources;
                   rescaling and offset (make_source)
  reservoirs.py    linear, tanh and affine-input tanh reservoirs
  integrate.py     fixed-step RK4, also for tangent vectors
  driven.py        driven runs (source + reservoir)
  readout.py       ridge readout and its penalties
  closed_loop.py   closed-loop field, free runs, field errors, valid times, end states
  lyapunov.py      QR spectra: source, conditional, closed loop (driven and free base)
  transverse.py    ker N^T and the invariance leak
  perturbation.py  readout directions by frequency (claim_a.py)
  experiment.py    one train / test / diagnose run (Config, run)
  plotting.py      loading of scan results and the shared plot style
experiments/
  run_single.py, scan.py           one run, grid scans
  calibrate_sources.py             attractor statistics and windows of the 19 sources
  scans/                           the shell scripts of the paper's scans
  analyze_night.py, analyze_sources.py, claim_a.py, analyze_claim_a.py, counterexample.py   analyses
  figures_paper.py, figure_night.py, paper_figures.sh                                        the paper's figures
tests/             exact identities, Lyapunov exponents, sources, provenance
docs/              working notes
```

Arrays are time-major: trajectories are (T, dim) and the readout is `S_hat = R @ N`.

## License and citation

MIT, see [LICENSE](LICENSE). To cite, see [CITATION.cff](CITATION.cff).
