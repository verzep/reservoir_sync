#!/bin/bash
# Rebuild every figure of the paper from archived results (no scans are run).
#
#     bash experiments/paper_figures.sh RESULTS_DIR [OUT_DIR]     (OUT_DIR default: figures)
#
# RESULTS_DIR must hold
#   night_2026-10-20/lorenz_long.jsonl, night_2026-10-20/rossler_long.jsonl
#   source_scan/sources_lambda.csv, source_scan/sources_lambdaoff.csv
#     (if missing, they are made from source_scan/{calibration.json,scan_lambda.jsonl,
#      scan_lambdaoff.jsonl} with analyze_sources.py --arms lambda lambdaoff)
# Override the subdirectories with NIGHT_DIR / SOURCE_SCAN_DIR, the interpreter
# with PY (default "uv run --locked python"). See REPRODUCE.md for the figure list.
set -eu
if [ $# -lt 1 ]; then
    sed -n '2,12p' "$0" >&2
    exit 2
fi
abspath() { case $1 in /*) echo "$1" ;; *) echo "$PWD/$1" ;; esac; }
R=$(abspath "$1")
OUT=$(abspath "${2:-figures}")
NIGHT=$(abspath "${NIGHT_DIR:-$R/night_2026-10-20}")
SRC=$(abspath "${SOURCE_SCAN_DIR:-$R/source_scan}")
cd "$(dirname "$0")/.."  # repository root
PY=${PY:-uv run --locked python}

if [ ! -f "$SRC/sources_lambda.csv" ] || [ ! -f "$SRC/sources_lambdaoff.csv" ]; then
    $PY experiments/analyze_sources.py "$SRC" --arms lambda lambdaoff
fi
$PY experiments/figures_paper.py --results "$NIGHT" --source-scan "$SRC" --out "$OUT"
$PY experiments/figure_night.py "$NIGHT/lorenz_long.jsonl:lorenz" "$NIGHT/rossler_long.jsonl:rossler" \
    --out "$OUT/fig_failure_end_state.pdf"
echo "figures in $OUT"
