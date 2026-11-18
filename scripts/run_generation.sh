#!/bin/bash
# Sequential, memory-safe data build. Two heavy processes at most on a 16 GB laptop.
#
# One-time setup for the two CPU-only families added 2026-09-14:
#   brew install espeak-ng                       # 1.52.0, gives hi, ta and te voices
#   python3.12 -m venv ~/.venvs/piper            # isolated, the pinned py3.14 stack stays clean
#   ~/.venvs/piper/bin/pip install piper-tts soxr pyarrow soundfile
#   mkdir -p ~/.venvs/piper/voices && cd ~/.venvs/piper/voices
#   B=https://huggingface.co/rhasspy/piper-voices/resolve/main
#   curl -LO $B/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx
#   curl -LO $B/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx.json
#   curl -LO $B/te/te_IN/venkatesh/medium/te_IN-venkatesh-medium.onnx
#   curl -LO $B/te/te_IN/venkatesh/medium/te_IN-venkatesh-medium.onnx.json
# There is no Tamil Piper voice. Checked against voices.json on 2026-09-14: 176 voices,
# hi_IN 3, te_IN 3, ta_IN 0.
cd /Users/saivinay/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
PY=../.venv/bin/python
S=/private/tmp/claude-501/-Users-saivinay-Desktop-hackathons-2026-sih-26104-kempelen/681be50e-e320-4db6-be44-d7a7078dc207/scratchpad
echo "== mac_say $(date)"; $PY scripts/build_generators.py mac_say
echo "== kokoro $(date)"; ESPEAK_DATA_PATH=/opt/homebrew/share/espeak-ng-data PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.dylib $HOME/.venvs/kokoro/bin/python scripts/build_generators.py kokoro
echo "== mms $(date)"; $PY scripts/build_generators.py mms_vits
echo "== espeak_ng $(date)"; $PY scripts/build_generators.py espeak_ng
echo "== piper $(date)"; $HOME/.venvs/piper/bin/python scripts/build_generators.py piper
echo "== manifest $(date)"; $PY scripts/build_generators.py manifest
echo "== breadth manifest $(date)"; $PY scripts/build_breadth_manifest.py
echo "== features $(date)"; $PY eval/build_features.py --prefixes 0.5,1,1.5,2,2.5,3,3.5,4
echo "== done $(date)"
