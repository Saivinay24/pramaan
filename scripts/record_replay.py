#!/usr/bin/env python3
"""Add the demo laptop's speaker-to-microphone path as a training channel.

Playing a clip through the speaker and recording it with the built-in mic is a channel
the detector has never seen: room, speaker colouring, mic gain. This script plays a
balanced set of real and synthetic training clips through that path, embeds the
recordings, and appends them to features.npz as condition "replay_mic". Then
`experiments.py --only ship` folds them into the shipped head.

    python scripts/record_replay.py --per-class 42
"""
import argparse, csv, os, subprocess, sys, time
import numpy as np, soundfile as sf, sounddevice as sd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
FEAT = os.path.join(ROOT, "eval", "results", "features.npz")
SR = 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=42)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--volume", type=float, default=1.0, help="afplay playback volume, to cover quieter setups")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "manifest_all.csv"))))
    rng = np.random.default_rng(a.seed)
    bona = [r for r in rows if r["label"] == "0"]
    spoof = [r for r in rows if r["label"] == "1" and r["generator"] != "chatterbox"]
    rng.shuffle(bona); rng.shuffle(spoof)
    # spread spoof picks evenly over generator families
    by_gen = {}
    for r in spoof:
        by_gen.setdefault(r["generator"], []).append(r)
    picks_s = []
    while len(picks_s) < a.per_class:
        for g in by_gen:
            if by_gen[g] and len(picks_s) < a.per_class:
                picks_s.append(by_gen[g].pop())
    picks = bona[:a.per_class] + picks_s
    rng.shuffle(picks)
    print(f"{len(picks)} clips through {sd.query_devices(kind='input')['name']}", flush=True)

    from pramaan.frontend import Frontend
    fe = Frontend()
    X, meta = [], []
    t0 = time.time()
    for i, r in enumerate(picks, 1):
        p = os.path.join(ROOT, "data", "clips", r["path"])
        info = sf.info(p)
        n = int((info.frames / info.samplerate + 0.4) * SR)
        rec = sd.rec(n, samplerate=SR, channels=1, dtype="float32")
        subprocess.run(["afplay", "-v", str(a.volume), p]); sd.wait()
        y = rec[:, 0]
        peak = float(np.abs(y).max())
        if peak < 0.005:
            print(f"  {r['clip_id']}: silence recorded (peak {peak:.4f}), skipping", flush=True)
            continue
        X.append(fe.embed(y)); meta.append(r)
        if i % 10 == 0:
            print(f"  {i}/{len(picks)}  {time.time()-t0:.0f}s  last peak {peak:.3f}", flush=True)

    z = np.load(FEAT, allow_pickle=True)
    keep = np.ones(len(z["condition"]), bool)          # append; earlier batches stay
    out = {k: z[k][keep] for k in z.files}
    add = dict(X=np.stack(X).astype(np.float32),
               clip_id=np.array([r["clip_id"] for r in meta]),
               condition=np.array([f"replay_mic_v{a.volume:g}"] * len(meta)),
               prefix_s=np.array([4.0] * len(meta)),
               y=np.array([int(r["label"]) for r in meta]),
               generator=np.array([r["generator"] for r in meta]),
               family=np.array([r["family"] for r in meta]),
               language=np.array([r["language"] for r in meta]),
               source=np.array([r["source"] for r in meta]),
               parent=np.array([r.get("parent", "") for r in meta]))
    merged = {k: np.concatenate([out[k], add[k]]) for k in out}
    np.savez_compressed(FEAT, **merged)
    print(f"appended {len(meta)} replay_mic rows -> {FEAT}")


if __name__ == "__main__":
    main()
