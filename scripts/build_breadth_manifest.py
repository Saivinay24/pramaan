#!/usr/bin/env python3
"""Emit data/manifest_breadth.csv, the fifteen-column provenance manifest.

docs/DATA_PLAN.md section A5.1 specifies this file. It exists so the format is proven on
850 laptop-generated clips before 11,220 A100-generated clips depend on it. Every column is
filled from the row files scripts/build_generators.py already writes, plus the engine facts
recorded below, plus a sha256 computed from the wav bytes on disk.

    python scripts/build_breadth_manifest.py

The rule from DATA_PLAN A5.2: a clip with no named source, no named licence and no recorded
generation parameters gets deleted, not imported. This script refuses to write a row with an
empty column.
"""
import csv, datetime, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "data", "clips")
OUT = os.path.join(ROOT, "data", "manifest_breadth.csv")
COLS = ["clip_id", "path", "label", "source", "generator", "family", "language",
        "duration_s", "licence", "parent", "voice_matched", "gen_params", "run_id",
        "generated_utc", "sha256"]

# One entry per family that this manifest covers. `voice_matched` is 0 for both: eSpeak NG
# and Piper reuse the parent's SENTENCE, they do not clone the parent's SPEAKER. That is the
# distinction DATA_PLAN A5.1 added the column for.
FAMILIES = {
    "espeak_ng": dict(
        voice_matched=0,
        run_id="call-20260914-espeak-ng-breadth",
        gen_params=dict(engine="eSpeak NG 1.52.0",
                        data="/opt/homebrew/Cellar/espeak-ng/1.52.0/share/espeak-ng-data",
                        command="espeak-ng -v <voice> -w <out.wav> <text>",
                        voices={"hindi": "hi", "tamil": "ta", "telugu": "te"},
                        speed_wpm="default", pitch="default", source_sr=22050,
                        resampler="torchaudio.functional.resample", target_sr=16000,
                        peak_norm=0.7, device="cpu", seed="n/a, deterministic formant synthesis")),
    "piper": dict(
        voice_matched=0,
        run_id="call-20260914-piper-breadth",
        gen_params=dict(engine="piper-tts 1.8.0 (pip, python 3.12 side venv ~/.venvs/piper)",
                        voices={"hindi": "hi_IN-pratham-medium", "telugu": "te_IN-venkatesh-medium"},
                        voice_source="huggingface.co/rhasspy/piper-voices, fetched 2026-09-14",
                        onnx_sha256_prefix={"hi_IN-pratham-medium": "169964b0871667f67934",
                                            "te_IN-venkatesh-medium": "dfaa5b7833cd48d946f3"},
                        length_scale="default", noise_scale="default", noise_w="default",
                        source_sr=22050, resampler="soxr.resample", target_sr=16000,
                        peak_norm=0.7, device="cpu")),
}


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    rows, bad = [], 0
    for fam, meta in FAMILIES.items():
        p = os.path.join(ROOT, "data", f"rows_{fam}.json")
        if not os.path.exists(p):
            sys.exit(f"missing {p}, run scripts/build_generators.py {fam} first")
        for r in json.load(open(p)):
            wav = os.path.join(CLIPS, r["path"])
            if not os.path.exists(wav):
                bad += 1
                continue
            gp = dict(meta["gen_params"])
            gp["voice"] = r.get("voice", "")
            out = dict(r)
            out.update(voice_matched=meta["voice_matched"],
                       gen_params=json.dumps(gp, ensure_ascii=False, sort_keys=True),
                       run_id=meta["run_id"], generated_utc=stamp,
                       sha256=hashlib.sha256(open(wav, "rb").read()).hexdigest())
            missing = [c for c in COLS if str(out.get(c, "")).strip() == ""]
            if missing:
                print(f"  REFUSED {out['clip_id']}: empty {missing}")
                bad += 1
                continue
            rows.append(out)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    from collections import Counter
    print(f"wrote {len(rows)} rows, refused {bad} -> {OUT}")
    print(Counter((r["generator"], r["language"]) for r in rows))


if __name__ == "__main__":
    main()
