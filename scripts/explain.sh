#!/bin/bash
# Show every number at every stage for one clip. See scripts/explain_clip.py.
cd "$(dirname "$0")/.."
export PYTHONPATH=src
exec ../.venv/bin/python scripts/explain_clip.py "$@"
