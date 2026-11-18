#!/usr/bin/env python3
"""Bundle the demo samples. Every file carries a JSON stating its TRUE origin.

Each sample is a short 'call opening' the operator console streams through the live
pipeline. Pairs are the strongest demo: a real FLEURS recording next to a 2025 cloner
speaking the same sentence in the same voice.
"""
import csv, json, os, shutil, sys
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "data", "clips")
OUT = os.path.join(ROOT, "data", "samples")
SR = 16000

CALLERS = {
    "hindi": dict(name="Rajesh Menon", claims="claims to be Group CFO, calling from a new number"),
    "tamil": dict(name="Priya Raghavan", claims="claims to be Head of Treasury"),
    "telugu": dict(name="Suresh Babu", claims="claims to be the branch's regional director"),
}
ACTION = dict(what="Approve outward transfer to a new beneficiary", amount="₹ 42,00,000",
              to="to a beneficiary added 11 minutes ago")


def concat(paths, gap_s=0.35, total_s=None):
    ys = []
    for p in paths:
        y, sr = sf.read(os.path.join(CLIPS, p), dtype="float32")
        if y.ndim > 1:
            y = y.mean(axis=1)
        ys += [y, np.zeros(int(gap_s * SR), np.float32)]
    y = np.concatenate(ys)
    return y[:int(total_s * SR)] if total_s else y


def write(name, y, meta):
    os.makedirs(OUT, exist_ok=True)
    sf.write(os.path.join(OUT, name + ".wav"), y, SR, subtype="PCM_16")
    json.dump(meta, open(os.path.join(OUT, name + ".json"), "w"), indent=1, ensure_ascii=False)
    print(f"  {name:32s} {len(y)/SR:5.1f}s  {meta['origin']}")


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "manifest_all.csv"))))
    by = lambda **k: [r for r in rows if all(r[a] == b for a, b in k.items())]
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    # 1. genuine speech, three languages, ~10 s each (three consecutive FLEURS clips)
    for lang in ["hindi", "tamil", "telugu"]:
        b = by(label="0", language=lang)[-3:]
        write(f"human_{lang}", concat([r["path"] for r in b]),
              dict(title=f"Genuine caller · {lang.title()} (FLEURS recording)", origin=f"real human speech, FLEURS {lang}, CC-BY 4.0",
                   language=lang, label="human", caller=CALLERS[lang], action=ACTION, seed=7))

    # 2. the pair: a real recording and its 2025 clone, same speaker, same words
    cb = by(generator="chatterbox")
    if cb:
        pick = cb[-3:]
        parents = [r["parent"] for r in pick]
        prow = {r["clip_id"]: r for r in rows}
        write("pair_real_hindi", concat([prow[p]["path"] for p in parents if p in prow]),
              dict(title="Pair A · the real person (FLEURS Hindi recording)", origin="real human speech, FLEURS Hindi",
                   language="hindi", label="human", caller=CALLERS["hindi"], action=ACTION, seed=11))
        write("pair_clone_hindi", concat([r["path"] for r in pick]),
              dict(title="Pair B · 2025 zero-shot clone of the same person (Chatterbox, unseen in training)",
                   origin="ResembleAI Chatterbox Multilingual clone of the Pair A recording. This cloner appears in NO training data.",
                   language="hindi", label="synthetic", caller=CALLERS["hindi"], action=ACTION, seed=11))

    # 3. clones from families the detector has seen (held-out clips)
    for gen, title, origin in [
        ("xtts_v2", "Clone · XTTS-v2 (IndicSynth, Hindi)", "IndicSynth XTTS-v2 synthetic speech, CC-BY-NC"),
        ("kokoro", "Clone · Kokoro-82M (2025 open TTS, Hindi)", "Kokoro-82M synthetic speech, Apache-2.0"),
        ("mms_vits", "Clone · Meta MMS-TTS (Tamil)", "Meta MMS-TTS VITS synthetic speech, CC-BY-NC"),
        ("mac_say", "Clone · Apple on-device TTS (Telugu)", "Apple macOS TTS synthetic speech"),
    ]:
        g = by(generator=gen)
        if gen == "mms_vits":
            g = [r for r in g if r["language"] == "tamil"] or g
        if gen == "mac_say":
            g = [r for r in g if r["language"] == "telugu"] or g
        if not g:
            continue
        lang = g[-1]["language"]
        write(f"clone_{gen}", concat([r["path"] for r in g[-3:]]),
              dict(title=title, origin=origin, language=lang, label="synthetic",
                   caller=CALLERS.get(lang, CALLERS["hindi"]), action=ACTION, seed=5))


if __name__ == "__main__":
    main()
