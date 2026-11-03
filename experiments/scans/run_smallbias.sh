#!/bin/bash
# Lambda arm with small biases: breaks the odd symmetry with little saturation.
set -u
D=results/source_scan
PY=.venv/bin/python
ALL=$($PY -c "from reservoir_sync.sources import SOURCES; print(*sorted(SOURCES))")
$PY experiments/scan.py --source $ALL --spectral-radius 0.5 0.9 1.2 --input-scale 0.02 0.05 0.1 --bias-scale 0.01 0.03 0.1 0.2 --gamma 1 5 20 --seed 0 1 2 3 4 5 6 7 8 9 --n 200 --beta 1e-6 --workers 40 --per-source $D/per_source_lambda.json --out $D/scan_smallbias.jsonl
echo SMALLBIAS DONE
