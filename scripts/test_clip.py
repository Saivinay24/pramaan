#!/usr/bin/env python3
"""Score any audio file through the live pipeline, exactly as the demo does.

    scripts/test.sh data/clips/spoof/kokoro/hindi/spoof_kokoro_hindi_00003.wav
    scripts/test.sh ~/Downloads/whatever.mp3 --channel opus_24k --play
    scripts/test.sh --random spoof --n 8          # 8 random synthetic clips
    scripts/test.sh --random bonafide --n 8       # 8 random human clips
    scripts/test.sh --list                        # what is in the library

Accepts wav, mp3, m4a, ogg, flac: anything ffmpeg can read.
"""
import argparse, glob, os, random, subprocess, sys, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
CLIPS = os.path.join(ROOT, "data", "clips")
SR = 16000

LIBRARY = {
    "bonafide":   ("real human speech, FLEURS Hindi / Tamil / Telugu", "bonafide/**/*.wav"),
    "spoof":      ("all synthetic training clips", "spoof/**/*.wav"),
    "xtts_v2":    ("XTTS-v2 voice clones (IndicSynth)", "spoof/xtts_v2/**/*.wav"),
    "freevc24":   ("FreeVC voice conversion (IndicSynth)", "spoof/freevc24/**/*.wav"),
    "mac_say":    ("Apple on-device TTS, Hindi and Telugu", "spoof/mac_say/**/*.wav"),
    "mms_vits":   ("Meta MMS-TTS, all three languages", "spoof/mms_vits/**/*.wav"),
    "kokoro":     ("Kokoro-82M, Hindi", "spoof/kokoro/**/*.wav"),
    "encodec":    ("EnCodec neural rebuild of the real recordings", "samecorpus/spoof/**/*.wav"),
    "chatterbox": ("HELD OUT: Chatterbox 2025 clones of our own speakers", "a2_cloner/**/*.wav"),
    "samples":    ("the bundled demo clips", None),
}


def load(path):
    """Read any audio file as 16 kHz mono float32."""
    import soundfile as sf
    if not path.lower().endswith(".wav"):
        tmp = tempfile.mktemp(suffix=".wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path,
                        "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", tmp], check=True)
        path = tmp
    y, sr = sf.read(path, dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        import torch, torchaudio.functional as F
        y = F.resample(torch.from_numpy(y)[None], sr, SR).numpy()[0]
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--random", help="pick from the library: " + ", ".join(LIBRARY))
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--channel", default="clean", help="telephony codec to simulate")
    ap.add_argument("--play", action="store_true", help="play each clip aloud while scoring")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    if a.list:
        print(f"{'name':12s} {'clips':>6s}  what it is")
        for k, (desc, pat) in LIBRARY.items():
            n = len(glob.glob(os.path.join(ROOT, "data", "samples", "*.wav"))) if pat is None \
                else len(glob.glob(os.path.join(CLIPS, pat), recursive=True))
            print(f"{k:12s} {n:6d}  {desc}")
        print("\nexample:  scripts/test.sh --random chatterbox --n 5 --channel opus_24k")
        return

    files = list(a.files)
    if a.random:
        key = a.random
        if key not in LIBRARY:
            sys.exit(f"unknown set {key!r}; one of: {', '.join(LIBRARY)}")
        pat = LIBRARY[key][1]
        pool = glob.glob(os.path.join(ROOT, "data", "samples", "*.wav")) if pat is None \
            else glob.glob(os.path.join(CLIPS, pat), recursive=True)
        random.Random(a.seed).shuffle(pool)
        files += pool[:a.n]
    if not files:
        sys.exit("give a file, or --random <set>, or --list")

    from pramaan.frontend import Frontend
    from pramaan.stream import CallSession
    from pramaan.channels import apply_channel
    fe = Frontend()
    print(f"\nchannel: {a.channel}\n")
    print(f"{'file':42s} {'verdict':10s} {'at':>5s}  {'P(synthetic)':>12s}  score trace")
    print("-" * 108)
    agree = 0
    for f in files:
        try:
            y = load(f)
        except Exception as e:
            print(f"{os.path.basename(f)[:42]:42s} could not read: {type(e).__name__}")
            continue
        if a.channel != "clean":
            y = apply_channel(y, a.channel, sr=SR)
        if a.play:
            subprocess.Popen(["afplay", f])
        s = CallSession(fe, channel=a.channel, caller={"name": "test", "claims": "test"}, action={})
        for i in range(0, len(y), SR // 2):
            s.push(y[i:i + SR // 2])
        if not s.trace:
            print(f"{os.path.basename(f)[:42]:42s} too short to score ({len(y)/SR:.1f}s)")
            continue
        first = next((t for t in s.trace if t["committed"]), None)
        last = s.trace[-1]
        trace = " ".join(f"{t['p']:.2f}" for t in s.trace[:12])
        print(f"{os.path.basename(f)[:42]:42s} {last['state']:10s} "
              f"{(str(first['t']) + 's') if first else '  -':>5s}  {last['p']:12.2f}  {trace}")
        # if the path tells us the truth, count agreement
        truth = "HUMAN" if ("bonafide" in f or "/bona/" in f or "human_" in f) else \
                "SYNTHETIC" if ("spoof" in f or "clone" in f or "a2_cloner" in f or "chatterbox" in f) else None
        if truth and last["state"] == truth:
            agree += 1
    if len(files) > 1:
        print(f"\nmatched the file's own label on {agree} of {len(files)}")


if __name__ == "__main__":
    main()
