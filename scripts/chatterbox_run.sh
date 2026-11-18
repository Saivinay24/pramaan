#!/bin/bash
# Runs the Chatterbox cloner in its own venv (~/.venvs/chatterbox, python 3.12).
cd /Users/saivinay/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
exec $HOME/.venvs/chatterbox/bin/python scripts/build_chatterbox.py "$@"
