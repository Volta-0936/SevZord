#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
( for c in flat_blind flat_risk flat_pain; do for s in 0 1 2; do python3 exp2.py $c $s || echo "FAIL $c $s"; done; done ) > logs/v1_lane1.log 2>&1 &
( for c in flat_riskpain frame_blind frame_riskpain; do for s in 0 1 2; do python3 exp2.py $c $s || echo "FAIL $c $s"; done; done ) > logs/v1_lane2.log 2>&1 &
wait
echo DONE >> logs/v1_done.log
