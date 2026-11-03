#!/bin/bash
# After the freq arm: does a constant input explain Lorenz vs Rossler? Controls
# on the two sources, then the lambda arm with an offset on all sources, then
# the raw arm. Offsets: Lorenz's raw z mean 23.57 in units of the amplitude.
set -u
D=results/source_scan
PY=.venv/bin/python
W=${WORKERS:-40}
ALL=$($PY -c "from reservoir_sync.sources import SOURCES; print(*sorted(SOURCES))")
GRID="--spectral-radius 0.5 0.9 1.2 --input-scale 0.02 0.05 0.1 --gamma 1 5 20 --seed 0 1 2 3 4 5 6 7 8 9 --n 200 --beta 1e-6 --workers $W"
ctl() {  # label source per-source-arm amplitude offset
    $PY experiments/scan.py --source $2 $GRID --per-source $D/per_source_$3.json --amplitude $4 --offset $5 --out $D/ctl_$1.jsonl
}
# the per-source tables fix the amplitude; these strip it so that the CLI value holds
$PY - <<P
import json
for arm in ("raw", "lambda"):
    t = json.load(open("$D/per_source_%s.json" % arm))
    for v in t.values():
        v.pop("amplitude")
    json.dump(t, open("$D/per_source_%s_noamp.json" % arm, "w"), indent=1)
P
ctl L_A6_off lorenz lambda_noamp 6 16.4
ctl L_A8.5_off0 lorenz lambda_noamp 8.5 0
ctl L_A8.5_off lorenz lambda_noamp 8.5 23.3
ctl R_A6_off0_rawtime rossler raw_noamp 6 0
ctl R_A6_off_rawtime rossler raw_noamp 6 16.4
ctl R_A4.3_off0_rawtime rossler raw_noamp 4.3 0
ctl R_A6_off_lambda rossler lambda_noamp 6 16.4
$PY experiments/scan.py --source $ALL $GRID --per-source $D/per_source_lambda.json --offset 16.4 --out $D/scan_lambdaoff.jsonl
$PY experiments/scan.py --source $ALL $GRID --per-source $D/per_source_raw.json --out $D/scan_raw.jsonl
echo CONTROLS AND RAW DONE
