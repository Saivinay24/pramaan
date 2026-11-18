#!/bin/bash
cd /Users/saivinay/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
echo "== kokoro $(date)"; ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib $HOME/.venvs/kokoro/bin/python scripts/build_generators.py kokoro
echo "== chatterbox $(date)"; scripts/chatterbox_run.sh --n 130 --scan 418 --seed 1 --device mps
echo "== done $(date)"
