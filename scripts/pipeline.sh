#!/bin/bash
# Everything after data generation, in order. Safe to re-run; every stage is incremental.
set -e
cd "$(dirname "$0")/.."
PY=../.venv/bin/python
echo "== manifest $(date)";  $PY scripts/build_generators.py manifest
echo "== features $(date)";  $PY eval/build_features.py --prefixes 0.5,1,1.5,2,2.5,3,3.5,4
echo "== experiments $(date)"; $PY eval/experiments.py
echo "== latency $(date)";   $PY eval/latency.py
echo "== numbers $(date)";   $PY scripts/fill_numbers.py
echo "== samples $(date)";   $PY scripts/make_samples.py
echo "== deck $(date)";      $PY scripts/draw_architecture.py && $PY scripts/build_deck.py
echo "== done $(date)"
