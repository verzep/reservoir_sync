#!/bin/bash
# The two long scans behind Figs. fig:predictors, fig:gap, fig:tangent_survival, fig:failure_end_state and
# Secs. 5.1, 5.3-5.5 (810 runs per source). Recovered from results/night_2026-10-20/batch_long.sh on tethys,
# where they ran through a retry wrapper (resumable, nice -n 10) with 28 workers, Rossler at commit fc4fcdf and
# Lorenz at e3c3e7b (both on main). Run from the repository root: bash experiments/scans/night_long.sh [OUT_DIR]
set -eu
D=${1:-results/night_2026-10-20}
PY=${PY:-uv run --locked python}
W=${WORKERS:-28}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$D"
GRID="--spectral-radius 0.5 0.9 1.2 --input-scale 0.02 0.05 0.1 --gamma 1 5 20 --seed $(seq -s " " 0 29)"
$PY experiments/scan.py --source rossler --t-test 300 --t-lyap 2000 $GRID --workers $W --out "$D/rossler_long.jsonl"
$PY experiments/scan.py --source lorenz --t-test 300 --t-lyap 2000 --t-pred 25 $GRID --workers $W --out "$D/lorenz_long.jsonl"
