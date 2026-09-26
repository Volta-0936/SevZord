#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$(dirname "$0")"
( for c in main necessity brain; do s=$(date +%s); python3 exp.py $c; echo "$c $(( $(date +%s)-s )) s"; done ) > logs/lane1.log 2>&1 &
( for c in sym_anchor exact sim noisy scratchB; do s=$(date +%s); python3 exp.py $c; echo "$c $(( $(date +%s)-s )) s"; done ) > logs/lane2.log 2>&1 &
wait
echo ALLDONE >> logs/done.log
