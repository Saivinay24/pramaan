#!/usr/bin/env python3
"""Add generator families to the spoof side of the dataset.

The research finding this implements: detectors generalise to an unseen cloner in
proportion to how many DISTINCT generator families they saw in training. The legacy
manifest has two (xtts_v2, freevc24, both from IndicSynth). This script adds more, all
generated locally on the laptop from the SAME FLEURS sentences the bona fide clips speak,
so text content cannot be the tell.

Families:
  mac_say    Apple's on-device TTS (Lekha hi_IN, Geeta te_IN). Concatenative/parametric.
  mms_vits   Meta MMS-TTS (facebook/mms-tts-{hin,tam,tel}). VITS, CC-BY-NC 4.0.
  kokoro     Kokoro-82M (Apache-2.0), Hindi voices, if the side venv exists.
  espeak_ng  eSpeak NG formant synthesis (GPL-3.0). Hindi, Tamil, Telugu. CPU only.
  piper      Piper ONNX VITS (MIT). Hindi and Telugu only, no Tamil voice exists. CPU only.

Usage:
  python scripts/build_generators.py mac_say
  python scripts/build_generators.py mms_vits
  python scripts/build_generators.py kokoro
  python scripts/build_generators.py espeak_ng
  ~/.venvs/piper/bin/python scripts/build_generators.py piper
  python scripts/build_generators.py manifest      # merge everything into data/manifest.csv
"""
import csv, io, json, os, subprocess, sys, tempfile
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = os.path.dirname(ROOT)
CLIPS = os.path.join(ROOT, "data", "clips")
SR = 16000
CLIP_S = 4.0
MIN_SRC_S = 2.5
FLEURS = {"hindi": "hi_in", "tamil": "ta_in", "telugu": "te_in"}
PER_LANG = 170


def _decode(b):
    y, r = sf.read(io.BytesIO(b), dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if r != SR:
        import torch, torchaudio.functional as F
        y = F.resample(torch.from_numpy(y)[None], r, SR).numpy()[0]
    return y


def _fit(y):
    n = int(CLIP_S * SR)
    if len(y) < int(MIN_SRC_S * SR):
        return None
    return y[:n] if len(y) >= n else y


def transcripts(lang, limit=PER_LANG):
    """Replay the legacy bona fide walk so index i maps to bona_<lang>_<i>."""
    import pyarrow.parquet as pq
    d = os.path.join(LEGACY, "data", "raw", "google__fleurs", FLEURS[lang])
    files = sorted(os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if f.endswith(".parquet"))
    out, n = {}, 0
    for p in files:
        for batch in pq.ParquetFile(p).iter_batches(batch_size=64):
            for r in batch.to_pylist():
                if n >= limit:
                    return out
                a = r.get("audio")
                if not a or not a.get("bytes"):
                    continue
                try:
                    y = _fit(_decode(a["bytes"]))
                except Exception:
                    continue
                if y is None:
                    continue
                out[f"bona_{lang}_{n:05d}"] = r.get("raw_transcription") or r.get("transcription") or ""
                n += 1
    return out


def _write(y, rel):
    p = os.path.join(CLIPS, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    y = np.asarray(y, dtype=np.float32)
    peak = float(np.abs(y).max()) or 1.0
    y = y / peak * 0.7
    sf.write(p, y, SR, subtype="PCM_16")
    return len(y) / SR



def _existing(rel):
    """Resume support: return duration if the clip already exists on disk."""
    p = os.path.join(CLIPS, rel)
    if os.path.exists(p):
        info = sf.info(p)
        return info.frames / info.samplerate
    return None

def _rows_path(family):
    return os.path.join(ROOT, "data", f"rows_{family}.json")


def _save_rows(family, rows):
    json.dump(rows, open(_rows_path(family), "w"), indent=1)
    print(f"{family}: {len(rows)} clips", flush=True)


# ------------------------------------------------------------------ mac_say
SAY_VOICES = {"hindi": "Lekha", "telugu": "Geeta"}


def build_mac_say():
    rows = []
    for lang, voice in SAY_VOICES.items():
        tx = transcripts(lang)
        for i, (parent, text) in enumerate(sorted(tx.items())):
            if len(text.split()) < 3:
                continue
            cid = f"spoof_macsay_{lang}_{i:05d}"
            rel = os.path.join("spoof", "mac_say", lang, cid + ".wav")
            dur = _existing(rel)
            if dur:
                rows.append(dict(clip_id=cid, path=rel, label=1, source="mac_say", generator="mac_say",
                                 family="concatenative_tts", language=lang, duration_s=round(dur, 3),
                                 licence="Apple on-device TTS output", parent=parent))
                continue
            with tempfile.TemporaryDirectory() as d:
                tmp = os.path.join(d, "o.wav")
                r = subprocess.run(["say", "-v", voice, "-o", tmp, "--data-format=LEI16@16000", text],
                                   capture_output=True)
                if r.returncode != 0 or not os.path.exists(tmp):
                    continue
                y, sr = sf.read(tmp, dtype="float32")
            y = _fit(y)
            if y is None:
                continue
            dur = _write(y, rel)
            rows.append(dict(clip_id=cid, path=rel, label=1, source="mac_say", generator="mac_say",
                             family="concatenative_tts", language=lang, duration_s=round(dur, 3),
                             licence="Apple on-device TTS output", parent=parent))
    _save_rows("mac_say", rows)


# ------------------------------------------------------------------ mms_vits
MMS = {"hindi": "hin", "tamil": "tam", "telugu": "tel"}


def build_mms():
    import torch
    from transformers import VitsModel, AutoTokenizer
    rows = []
    for lang, code in MMS.items():
        m = VitsModel.from_pretrained(f"facebook/mms-tts-{code}").eval()
        tok = AutoTokenizer.from_pretrained(f"facebook/mms-tts-{code}")
        tx = transcripts(lang)
        for i, (parent, text) in enumerate(sorted(tx.items())):
            if len(text.split()) < 3:
                continue
            cid = f"spoof_mms_{lang}_{i:05d}"
            rel = os.path.join("spoof", "mms_vits", lang, cid + ".wav")
            dur = _existing(rel)
            if dur:
                rows.append(dict(clip_id=cid, path=rel, label=1, source="MMS-TTS", generator="mms_vits",
                                 family="vits_e2e", language=lang, duration_s=round(dur, 3),
                                 licence="CC-BY-NC-4.0", parent=parent))
                continue
            try:
                x = tok(text, return_tensors="pt")
                with torch.no_grad():
                    w = m(**x).waveform[0].numpy()
            except Exception as e:
                print("  skip", parent, type(e).__name__, flush=True)
                continue
            if m.config.sampling_rate != SR:
                import torchaudio.functional as F
                w = F.resample(torch.from_numpy(w)[None], m.config.sampling_rate, SR).numpy()[0]
            y = _fit(w)
            if y is None:
                continue
            cid = f"spoof_mms_{lang}_{i:05d}"
            rel = os.path.join("spoof", "mms_vits", lang, cid + ".wav")
            dur = _write(y, rel)
            rows.append(dict(clip_id=cid, path=rel, label=1, source="MMS-TTS", generator="mms_vits",
                             family="vits_e2e", language=lang, duration_s=round(dur, 3),
                             licence="CC-BY-NC-4.0", parent=parent))
            if len(rows) % 50 == 0:
                print(f"  {len(rows)}", flush=True)
    _save_rows("mms_vits", rows)


# ------------------------------------------------------------------ kokoro
def build_kokoro():
    """Runs INSIDE the kokoro venv (python 3.12). Hindi only."""
    from kokoro import KPipeline
    import torch, torchaudio.functional as F
    p = KPipeline(lang_code="h")
    voices = ["hf_alpha", "hf_beta", "hm_omega", "hm_psi"]
    rows = []
    tx = transcripts("hindi")
    for i, (parent, text) in enumerate(sorted(tx.items())):
        if len(text.split()) < 3:
            continue
        cid = f"spoof_kokoro_hindi_{i:05d}"
        rel = os.path.join("spoof", "kokoro", "hindi", cid + ".wav")
        dur = _existing(rel)
        if dur:
            rows.append(dict(clip_id=cid, path=rel, label=1, source="Kokoro-82M", generator="kokoro",
                             family="style_tts_decoder", language="hindi", duration_s=round(dur, 3),
                             licence="Apache-2.0", parent=parent, voice=voices[i % len(voices)]))
            continue
        try:
            chunks = [a for _, _, a in p(text, voice=voices[i % len(voices)])]
        except Exception as e:
            print("  skip", parent, type(e).__name__, e, flush=True)
            continue
        if not chunks:
            continue
        w = np.concatenate([np.asarray(c, dtype=np.float32) for c in chunks])
        w = F.resample(torch.from_numpy(w)[None], 24000, SR).numpy()[0]
        y = _fit(w)
        if y is None:
            continue
        cid = f"spoof_kokoro_hindi_{i:05d}"
        rel = os.path.join("spoof", "kokoro", "hindi", cid + ".wav")
        dur = _write(y, rel)
        rows.append(dict(clip_id=cid, path=rel, label=1, source="Kokoro-82M", generator="kokoro",
                         family="style_tts_decoder", language="hindi", duration_s=round(dur, 3),
                         licence="Apache-2.0", parent=parent, voice=voices[i % len(voices)]))
        if len(rows) % 50 == 0:
            print(f"  {len(rows)}", flush=True)
    _save_rows("kokoro", rows)


# ------------------------------------------------------------------ espeak_ng
# espeak-ng 1.52.0 (`espeak-ng --version`, run 2026-09-14). Formant synthesis, not neural.
# `espeak-ng --voices` on 2026-09-14 lists hi (Hindi), ta (Tamil), te (Telugu), so all three
# project languages are covered. Output is 22050 Hz mono, resampled to 16 kHz here.
ESPEAK_VOICES = {"hindi": "hi", "tamil": "ta", "telugu": "te"}
ESPEAK_SR = 22050


def build_espeak_ng():
    import torch, torchaudio.functional as F
    rows = []
    for lang, voice in ESPEAK_VOICES.items():
        tx = transcripts(lang)
        for i, (parent, text) in enumerate(sorted(tx.items())):
            if len(text.split()) < 3:
                continue
            cid = f"spoof_espeak_{lang}_{i:05d}"
            rel = os.path.join("spoof", "espeak_ng", lang, cid + ".wav")
            row = dict(clip_id=cid, path=rel, label=1, source="eSpeak NG", generator="espeak_ng",
                       family="formant_tts", language=lang, duration_s=0.0,
                       licence="GPL-3.0", parent=parent, voice=voice)
            dur = _existing(rel)
            if dur:
                row["duration_s"] = round(dur, 3)
                rows.append(row)
                continue
            with tempfile.TemporaryDirectory() as d:
                tmp = os.path.join(d, "o.wav")
                r = subprocess.run(["espeak-ng", "-v", voice, "-w", tmp, text],
                                   capture_output=True)
                if r.returncode != 0 or not os.path.exists(tmp):
                    print("  skip", parent, r.returncode, flush=True)
                    continue
                w, sr = sf.read(tmp, dtype="float32")
            if w.ndim > 1:
                w = w.mean(axis=1)
            if sr != SR:
                w = F.resample(torch.from_numpy(w)[None], sr, SR).numpy()[0]
            y = _fit(w)
            if y is None:
                continue
            row["duration_s"] = round(_write(y, rel), 3)
            rows.append(row)
            if len(rows) % 50 == 0:
                print(f"  {len(rows)}", flush=True)
    _save_rows("espeak_ng", rows)


# ------------------------------------------------------------------ piper
# Runs INSIDE the piper venv (python 3.12, ~/.venvs/piper), so the pinned py3.14 stack in
# ../.venv is untouched. Voice inventory checked against rhasspy/piper-voices voices.json on
# 2026-09-14: hi_IN has 3 voices, te_IN has 3 voices, ta_IN has NONE. Piper is therefore a
# two-language family (Hindi, Telugu), the same shape as mac_say.
PIPER_DIR = os.path.join(os.path.expanduser("~"), ".venvs", "piper", "voices")
PIPER_VOICES = {"hindi": "hi_IN-pratham-medium", "telugu": "te_IN-venkatesh-medium"}


def build_piper():
    from piper import PiperVoice
    import soxr                      # the piper venv stays light: no torch, no torchaudio
    rows = []
    for lang, voice in PIPER_VOICES.items():
        v = PiperVoice.load(os.path.join(PIPER_DIR, voice + ".onnx"))
        src_sr = v.config.sample_rate
        tx = transcripts(lang)
        for i, (parent, text) in enumerate(sorted(tx.items())):
            if len(text.split()) < 3:
                continue
            cid = f"spoof_piper_{lang}_{i:05d}"
            rel = os.path.join("spoof", "piper", lang, cid + ".wav")
            row = dict(clip_id=cid, path=rel, label=1, source="Piper", generator="piper",
                       family="vits_onnx", language=lang, duration_s=0.0,
                       licence="MIT", parent=parent, voice=voice)
            dur = _existing(rel)
            if dur:
                row["duration_s"] = round(dur, 3)
                rows.append(row)
                continue
            try:
                chunks = [c.audio_int16_array for c in v.synthesize(text)]
            except Exception as e:
                print("  skip", parent, type(e).__name__, e, flush=True)
                continue
            if not chunks:
                continue
            w = np.concatenate(chunks).astype(np.float32) / 32768.0
            if src_sr != SR:
                w = soxr.resample(w, src_sr, SR).astype(np.float32)
            y = _fit(w)
            if y is None:
                continue
            row["duration_s"] = round(_write(y, rel), 3)
            rows.append(row)
            if len(rows) % 50 == 0:
                print(f"  {len(rows)}", flush=True)
    _save_rows("piper", rows)


# ------------------------------------------------------------------ manifest
FAMILY_OF = {"xtts_v2": "autoregressive_tts", "freevc24": "voice_conversion",
             "encodec": "neural_codec", "chatterbox": "llm_tts_2025"}


def build_manifest():
    rows = []
    with open(os.path.join(ROOT, "data", "manifest.csv")) as f:
        for r in csv.DictReader(f):
            gen = "none" if r["label"] == "0" else r["cloner"]
            rows.append(dict(clip_id=r["clip_id"], path=r["path"], label=int(r["label"]),
                             source=r["source"], generator=gen,
                             family="human" if gen == "none" else FAMILY_OF[gen],
                             language=r["language"], duration_s=r["duration_s"],
                             licence=r["licence"], parent=""))
    with open(os.path.join(ROOT, "data", "manifest_samecorpus.csv")) as f:
        for r in csv.DictReader(f):
            if r["label"] == "0":
                continue                      # the bona parents are already in manifest.csv
            rows.append(dict(clip_id=r["clip_id"], path=r["path"], label=1, source=r["source"],
                             generator="encodec", family="neural_codec", language=r["language"],
                             duration_s=r["duration_s"], licence=r["licence"],
                             parent=r.get("parent_clip_id", "")))
    with open(os.path.join(ROOT, "data", "manifest_a2.csv")) as f:
        for r in csv.DictReader(f):
            if r["label"] == "0":
                continue
            rows.append(dict(clip_id=r["clip_id"], path=r["path"], label=1, source=r["source"],
                             generator="chatterbox", family="llm_tts_2025", language=r["language"],
                             duration_s=r["duration_s"], licence=r["licence"],
                             parent=r.get("parent_clip_id", "")))
    cbp = os.path.join(ROOT, "data", "manifest_chatterbox.csv")
    seen = {r["parent"] for r in rows if r["generator"] == "chatterbox"}
    if os.path.exists(cbp):
        with open(cbp) as f:
            for r in csv.DictReader(f):
                if r["parent_clip_id"] in seen:
                    continue                      # already covered by the A2 clone of this parent
                rows.append(dict(clip_id=r["clip_id"], path=r["path"], label=1, source=r["source"],
                                 generator="chatterbox", family="llm_tts_2025", language=r["language"],
                                 duration_s=r["duration_s"], licence=r["licence"],
                                 parent=r["parent_clip_id"]))
    for fam in ["mac_say", "mms_vits", "kokoro", "espeak_ng", "piper"]:
        if os.path.exists(_rows_path(fam)):
            rows += json.load(open(_rows_path(fam)))
    cols = ["clip_id", "path", "label", "source", "generator", "family", "language",
            "duration_s", "licence", "parent"]
    out = os.path.join(ROOT, "data", "manifest_all.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    from collections import Counter
    print(f"wrote {len(rows)} rows -> {out}")
    print(Counter((r["generator"], r["language"]) for r in rows))


if __name__ == "__main__":
    {"mac_say": build_mac_say, "mms_vits": build_mms, "kokoro": build_kokoro,
     "espeak_ng": build_espeak_ng, "piper": build_piper,
     "manifest": build_manifest}[sys.argv[1]]()
