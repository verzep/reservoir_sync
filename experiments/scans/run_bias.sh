#!/bin/bash
# Lambda arm with no offset and a larger independent bias, matched per input scale to the
# spread of b + Vc in the lambda+offset arm: sqrt(0.5^2 + (16.4 sigma)^2).
set -u
D=results/source_scan
PY=.venv/bin/python
ALL=$($PY -c "from reservoir_sync.sources import SOURCES; print(*sorted(SOURCES))")
for pair in "0.02 0.598" "0.05 0.960" "0.1 1.715"; do
    set -- $pair
    $PY experiments/scan.py --source $ALL --spectral-radius 0.5 0.9 1.2 --input-scale $1 --bias-scale $2 --gamma 1 5 20 --seed 0 1 2 3 4 5 6 7 8 9 --n 200 --beta 1e-6 --workers 40 --per-source $D/per_source_lambda.json --out $D/scan_bias.jsonl
done
echo BIAS DONE
