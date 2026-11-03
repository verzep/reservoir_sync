#!/bin/bash
# Runs after run_bias.sh: lambda arm with no offset and no bias, the exactly symmetric reservoir.
set -u
D=results/source_scan
PY=.venv/bin/python
while pgrep -f run_bias.sh >/dev/null; do sleep 60; done
ALL=$($PY -c "from reservoir_sync.sources import SOURCES; print(*sorted(SOURCES))")
$PY experiments/scan.py --source $ALL --spectral-radius 0.5 0.9 1.2 --input-scale 0.02 0.05 0.1 --bias-scale 0 --gamma 1 5 20 --seed 0 1 2 3 4 5 6 7 8 9 --n 200 --beta 1e-6 --workers 40 --per-source $D/per_source_lambda.json --out $D/scan_bias0.jsonl
echo BIAS0 DONE
