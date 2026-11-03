#!/bin/bash
# The source scan, in order: existing settings and training-window controls on
# Lorenz and Rossler, then the three normalization arms on all sources.
# Calibrates the sources first if <dir>/calibration.json is missing; restartable
# (scan.py skips finished runs). Then run run_source_scan_controls.sh.
#
#     bash experiments/scans/run_source_scan.sh [RESULTS_DIR]     (default results/source_scan)
#
# Environment: WORKERS (default 40), PY (default "uv run --locked python").
set -eu
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
D=${1:-$ROOT/results/source_scan}
case $D in /*) ;; *) D=$PWD/$D ;; esac  # relative to the calling directory
cd "$ROOT"
PY=${PY:-uv run --locked python}
W=${WORKERS:-40}
mkdir -p "$D"
[ -f "$D/calibration.json" ] || $PY experiments/calibrate_sources.py --workers "$W" --out "$D/calibration.json"
ALL=$($PY -c "from reservoir_sync.sources import SOURCES; print(*sorted(SOURCES))")
GRID="--spectral-radius 0.5 0.9 1.2 --input-scale 0.02 0.05 0.1 --gamma 1 5 20 --seed 0 1 2 3 4 5 6 7 8 9 --n 200 --beta 1e-6 --workers $W"
echo '{"rossler": {"t_test": 300.0, "t_lyap": 2000.0}}' > $D/per_source_base.json
# same training length in Lyapunov times as the other source's existing runs
echo '{"rossler": {"t_test": 300.0, "t_lyap": 2000.0, "t_train": 1300.0}, "lorenz": {"t_train": 7.7}}' > $D/per_source_train.json
$PY experiments/scan.py --source lorenz rossler $GRID --per-source $D/per_source_base.json --out $D/scan_base.jsonl
$PY experiments/scan.py --source lorenz rossler $GRID --per-source $D/per_source_train.json --out $D/scan_train.jsonl
for arm in lambda freq raw; do
    $PY experiments/scan.py --source $ALL $GRID --per-source $D/per_source_$arm.json --out $D/scan_$arm.jsonl
done
echo ALL DONE
