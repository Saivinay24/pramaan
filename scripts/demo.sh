#!/bin/bash
# Start the Pramaan operator console, fully offline. http://127.0.0.1:8770
cd "$(dirname "$0")/.."
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONPATH=src
test -f eval/results/model.pkl || { echo "no model: run make all first"; exit 1; }
exec ../.venv/bin/python -m pramaan.server
