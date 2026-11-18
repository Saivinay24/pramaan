#!/usr/bin/env python3
"""Add a new synthetic-voice family from a folder of audio files, then retrain.

Drop mp3/wav/m4a files into a folder (for example clips generated with ElevenLabs in
different voices and sentences), then:

    python scripts/add_family.py --folder ~/Downloads/eleven --generator elevenlabs \
        --family commercial_pvc_2026 --language hindi --licence "ElevenLabs output"

Each file is converted to 16 kHz mono and cut into 4 s clips (minimum 2.5 s), added to
data/manifest_all.csv, embedded through the 7 codec conditions, and the shipped head is
retrained. Keep the clip you will play in the demo OUT of the folder, so it stays unseen.
"""
import argparse, csv, glob, os, subprocess, sys
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
SR, CLIP_S, MIN_S = 16000, 4.0, 2.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--generator", required=True)
    ap.add_argument("--family", required=True)
    ap.add_argument("--language", default="hindi")
    ap.add_argument("--licence", default="vendor output")
    a = ap.parse_args()
    files = sorted(f for f in glob.glob(os.path.join(os.path.expanduser(a.folder), "*"))
                   if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg", ".flac")))
    if not files:
        sys.exit("no audio files found")
    outdir = os.path.join(ROOT, "data", "clips", "spoof", a.generator, a.language)
    os.makedirs(outdir, exist_ok=True)
    rows, n = [], 0
    for f in files:
        tmp = "/tmp/_fam.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", tmp], check=True)
        y, _ = sf.read(tmp, dtype="float32")
        for start in range(0, len(y), int(CLIP_S * SR)):
            seg = y[start:start + int(CLIP_S * SR)]
            if len(seg) < MIN_S * SR:
                break
            cid = f"spoof_{a.generator}_{a.language}_{n:05d}"
            rel = os.path.join("spoof", a.generator, a.language, cid + ".wav")
            peak = float(np.abs(seg).max()) or 1.0
            sf.write(os.path.join(ROOT, "data", "clips", rel), seg / peak * 0.7, SR, subtype="PCM_16")
            rows.append(dict(clip_id=cid, path=rel, label=1, source=os.path.basename(f), generator=a.generator,
                             family=a.family, language=a.language, duration_s=round(len(seg) / SR, 3),
                             licence=a.licence, parent=""))
            n += 1
    man = os.path.join(ROOT, "data", "manifest_all.csv")
    existing = list(csv.DictReader(open(man)))
    cols = list(existing[0].keys())
    have = {r["clip_id"] for r in existing}
    with open(man, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        for r in rows:
            if r["clip_id"] not in have:
                w.writerow(r)
    print(f"{len(rows)} clips from {len(files)} files -> manifest")
    py = sys.executable
    subprocess.run([py, os.path.join(ROOT, "eval", "build_features.py")], check=True)
    # register the family so experiments treat it as seen
    exp = os.path.join(ROOT, "eval", "experiments.py")
    s = open(exp).read()
    if f'"{a.generator}"' not in s:
        s = s.replace('SEEN_ORDER = ["xtts_v2", "freevc24", "encodec", "mac_say", "mms_vits", "kokoro"]',
                      f'SEEN_ORDER = ["xtts_v2", "freevc24", "encodec", "mac_say", "mms_vits", "kokoro", "{a.generator}"]')
        open(exp, "w").write(s)
    subprocess.run([py, exp, "--only", "ship"], check=True)
    print("shipped. restart the server: pkill -f pramaan.server; scripts/demo.sh")


if __name__ == "__main__":
    main()
