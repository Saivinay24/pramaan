#!/usr/bin/env python3
"""A2: an attack set from a voice cloner that appears in NO training data.

WHY THIS EXISTS
---------------
Everything spoof in data/manifest.csv comes from IndicSynth, which burned XTTS-v2, VITS and
FreeVC24. A1 then added neural-codec resynthesis, which is a genuinely unseen generative
family but is the VOCODER stage of a cloner, not a cloner: no cloner was prompted and no new
sentence was spoken. A2 closes that gap with the real thing.

WHAT IT BUILDS
--------------
For a FLEURS clip in the TEST split, we take:
  - its own recording as the speaker prompt, and
  - its own transcript as the text,
and have Chatterbox Multilingual speak that sentence in that speaker's voice.

So the output is a genuine text-to-speech voice clone of a real speaker who is in our bona
fide set, saying the words that speaker actually said. It is therefore held out on BOTH axes
at once, which no other set in this repo is:

  - held-out cloner: Chatterbox appears in no training data, and IndicSynth predates it.
  - same corpus: the bona fide comparison recording is the very clip that was cloned, so
    corpus, speaker, words, microphone and session are all held fixed. The A1 confound
    cannot inflate this number.

HONEST LIMITS, WRITTEN BEFORE THE RESULT EXISTS
-----------------------------------------------
1. HINDI ONLY. Chatterbox Multilingual supports 23 languages and Tamil and Telugu are not
   among them. This measures one of our three languages, and nothing here may be reported
   as "across Indian languages".
2. Clone QUALITY is not verified. A cloner given a 4 s prompt in a language it supports
   thinly may produce a poor impersonation, and a poor impersonation is easier to detect.
   A low EER here is therefore not automatically a win, and the eval reports speaker
   similarity alongside it so the two cannot be confused.
3. Chatterbox watermarks its output with Perth by default. That is a synthesis artefact no
   attacker would leave in, so it is DISABLED here. If it could not be disabled the number
   would be meaningless and the script says so rather than quietly measuring a watermark
   detector.
4. Generation is sampled, not deterministic. The seed is fixed and recorded.

ENVIRONMENT
-----------
Chatterbox cannot run in this repo's pinned stack (it needs transformers 4.x, the project
runs 5.x) and a second full torch does not fit on this disk. It runs in an isolated venv
that borrows the project's torch over PYTHONPATH, bootstrapped by /tmp/kv_boot.py. The
runner is documented in docs/ENVIRONMENT.md and the Makefile target passes it for you.

    make a2

Licence: Chatterbox is MIT (ResembleAI). Its output here is derived from FLEURS (CC-BY-4.0).
"""
import argparse, csv, json, os, sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGACY = os.path.dirname(ROOT)
CLIPS = os.path.join(ROOT, "data", "clips")
RAW = os.path.join(LEGACY, "data", "raw")
SR = 16000
CLIP_S = 4.0
LANG = "hindi"
FLEURS_DIR = "hi_in"
CHATTERBOX_LANG = "hi"


def fleurs_transcripts(limit):
    """Replay build_dataset.py's bona fide walk to recover each clip's transcript.

    build_dataset.py assigns bona_hindi_00000, 00001, ... in parquet order, skipping rows
    whose audio fails to decode or is too short. This reproduces that walk exactly, so the
    index it produces maps to the same clip_id. It decodes audio for the sole purpose of
    applying the same skip rule; the wav on disk is the one we actually use.
    """
    sys.path.insert(0, os.path.join(LEGACY, "scripts"))
    import build_dataset as bd
    import pyarrow.parquet as pq

    out, n = {}, 0
    d = os.path.join(RAW, "google__fleurs", FLEURS_DIR)
    for p in bd._parquets(d):
        pf = pq.ParquetFile(p)
        for batch in pf.iter_batches(batch_size=64):
            for r in batch.to_pylist():
                if n >= limit:
                    return out
                a = r.get("audio")
                if not a or not a.get("bytes"):
                    continue
                try:
                    y = bd._fit(bd._decode(a["bytes"]))
                except Exception:
                    continue
                if y is None:
                    continue
                out[f"bona_{LANG}_{n:05d}"] = (r.get("raw_transcription")
                                               or r.get("transcription") or "")
                n += 1
    return out


def fit(y, sr_in):
    """Resample to 16k and cut or pad to exactly CLIP_S, the manifest's clip shape."""
    import scipy.signal as ss
    y = np.asarray(y, dtype=np.float32)
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr_in != SR:
        y = ss.resample_poly(y, SR, sr_in).astype(np.float32)
    want = int(CLIP_S * SR)
    if len(y) >= want:
        return y[:want]
    return np.pad(y, (0, want - len(y)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50, help="clones to generate")
    ap.add_argument("--scan", type=int, default=400, help="bona fide clips to scan for text")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="mps", help="mps is roughly 4x cpu here")
    ap.add_argument("--out-manifest", default=os.path.join(ROOT, "data", "manifest_chatterbox.csv"))
    a = ap.parse_args()


    with open(os.path.join(ROOT, "data", "manifest.csv")) as f:
        man = {r["clip_id"]: r for r in csv.DictReader(f)}

    texts = fleurs_transcripts(a.scan)
    cands = [cid for cid in sorted(texts)
             if cid in man and len(texts[cid].split()) >= 4]
    if not cands:
        raise SystemExit("no test-split Hindi bona fide clip has a usable transcript")
    rng = np.random.default_rng(a.seed)
    rng.shuffle(cands)
    cands = cands[:a.n]
    print(f"{len(cands)} test-split Hindi clips selected as clone targets")

    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    torch.manual_seed(a.seed)
    # perth's implicit watermarker is None in this install (its optional backend is
    # absent). We disable the watermark anyway, so give the constructor a stub.
    import perth
    if getattr(perth, "PerthImplicitWatermarker", None) is None:
        class _Stub:
            def apply_watermark(self, wav, sample_rate=None, **kw):
                return wav
        perth.PerthImplicitWatermarker = _Stub
    model = ChatterboxMultilingualTTS.from_pretrained(device=a.device)

    # The watermark is a synthesis artefact no attacker would leave in place, so it is
    # removed. Setting the watermarker to None is not enough, the caller invokes it
    # unconditionally, so it is replaced by a pass-through that returns the waveform it
    # was handed. If the attribute ever disappears this fails loudly rather than quietly
    # measuring a watermark detector and calling it a deepfake detector.
    if not hasattr(model, "watermarker"):
        raise SystemExit("no watermarker attribute to neutralise; refusing to generate")

    class _NoWatermark:
        def apply_watermark(self, wav, sample_rate=None, **kw):
            return wav

    model.watermarker = _NoWatermark()

    outdir = os.path.join(CLIPS, "chatterbox", LANG)
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for i, cid in enumerate(cands, 1):
        src = os.path.join(CLIPS, man[cid]["path"])
        if os.path.exists(os.path.join(CLIPS, "chatterbox", LANG, f"cb_{cid}.wav")):
            continue
        text = texts[cid].strip()
        try:
            wav = model.generate(text, language_id=CHATTERBOX_LANG, audio_prompt_path=src)
        except Exception as e:                      # a cloner that refuses a prompt is data
            print(f"  {cid}: generation failed, {type(e).__name__}: {e}", flush=True)
            continue
        y = wav.squeeze(0).detach().cpu().numpy() if hasattr(wav, "squeeze") else np.asarray(wav)
        y = fit(y, getattr(model, "sr", 24000))
        ocid = f"cb_{cid}"
        rel = os.path.join("chatterbox", LANG, ocid + ".wav")
        sf.write(os.path.join(CLIPS, rel), y, SR)
        rows.append(dict(clip_id=ocid, path=rel, label=1, source="FLEURS+Chatterbox",
                         cloner="chatterbox_multilingual", language=LANG,
                         duration_s=CLIP_S, licence="CC-BY-4.0+MIT",
                         parent_clip_id=cid,
                         generator="ResembleAI/chatterbox multilingual",
                         device=a.device,
                         text=text))
        if i % 10 == 0:
            print(f"  {i}/{len(cands)}", flush=True)

    if not rows:
        raise SystemExit("no clones were generated")

    with open(a.out_manifest, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {len(rows)} clones -> {a.out_manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
