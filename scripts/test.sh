#!/bin/bash
# Score any audio file through the live pipeline. See scripts/test_clip.py for options.
cd "$(dirname "$0")/.."
export PYTHONPATH=src
exec ../.venv/bin/python scripts/test_clip.py "$@"
