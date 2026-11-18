#!/usr/bin/env python3
"""Cache frozen XLS-R embeddings for every (clip, codec condition, prefix length).

Resumable: re-running only computes what is missing. Legacy caches from the Kempelen
build (same frontend, same layer, same codec grid) are merged in so nothing is recomputed.

    python eval/build_features.py                       # full clips, all 7 conditions
    python eval/build_features.py --prefixes 1,1.5,2,3  # streaming prefixes, clean only
"""
import argparse, csv, os, sys, time
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from pramaan.channels import GRID, apply_channel          # noqa: E402
from pramaan.config import SR, CLIP_S                     # noqa: E402

OUT = os.path.join(ROOT, "eval", "results", "features.npz")
LEGACY = [os.path.join(ROOT, "eval", "results", "features_legacy.npz"),
          os.path.join(ROOT, "eval", "results", "features_samecorpus_legacy.npz"),
          os.path.join(ROOT, "eval", "results", "features_prefix_legacy.npz")]
META = ["clip_id", "condition", "prefix_s", "y", "generator", "family", "language", "source", "parent"]


def load_cache(out=OUT):
    cache = {}
    if os.path.exists(out):
        z = np.load(out, allow_pickle=True)
        X, cid, cond, pre = z["X"], z["clip_id"], z["condition"], z["prefix_s"]
        for i in range(len(cid)):
            cache[(str(cid[i]), str(cond[i]), float(pre[i]))] = X[i]
    for p in LEGACY:
        if not os.path.exists(p):
            continue
        z = np.load(p, allow_pickle=True)
        X, cid, cond = z["X"], z["clip_id"], z["condition"]
        pre = z["prefix_s"].astype(float) if "prefix_s" in z.files else np.full(len(cid), CLIP_S)
        for i in range(len(cid)):
            cache.setdefault((str(cid[i]), str(cond[i]), float(pre[i])), X[i])
    return cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=os.path.join(ROOT, "data", "manifest_all.csv"))
    ap.add_argument("--conditions", default=",".join(GRID))
    ap.add_argument("--prefixes", default=str(CLIP_S))
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--prefix-conditions", default="clean",
                    help="short prefixes are computed only on these conditions")
    a = ap.parse_args()
    pconds = set(a.prefix_conditions.split(","))
    conds = [c for c in a.conditions.split(",") if c]
    prefixes = [float(p) for p in a.prefixes.split(",") if p]

    rows = list(csv.DictReader(open(a.manifest)))
    cache = load_cache(a.out)
    print(f"{len(rows)} clips, {len(cache)} cached embeddings", flush=True)

    todo = [(r, c, p) for r in rows for c in conds for p in prefixes
            if (r["clip_id"], c, p) not in cache and (p == CLIP_S or c in pconds)]
    print(f"{len(todo)} embeddings to compute", flush=True)
    if todo:
        from pramaan.frontend import Frontend
        fe = Frontend()
        t0 = time.perf_counter()
        wav_cache = {}
        for n, (r, c, p) in enumerate(todo, 1):
            key = r["clip_id"]
            if key not in wav_cache:
                w, _ = sf.read(os.path.join(ROOT, "data", "clips", r["path"]), dtype="float32")
                wav_cache = {key: w.mean(axis=1) if w.ndim > 1 else w}
            w = wav_cache[key]
            try:
                x = apply_channel(w, c, sr=SR)
                x = x[:int(p * SR)]
                cache[(key, c, p)] = fe.embed(x)
            except Exception as e:
                print(f"  SKIP {key}/{c}/{p}: {type(e).__name__}: {e}", flush=True)
            if n % 200 == 0:
                el = time.perf_counter() - t0
                print(f"  {n}/{len(todo)}  {el:.0f}s, eta {el / n * (len(todo) - n):.0f}s", flush=True)
                if n % 1000 == 0:
                    _save(rows, cache, a.out)
    _save(rows, cache, a.out)
    return 0


def _save(rows, cache, out=OUT):
    meta = {r["clip_id"]: r for r in rows}
    X, cols = [], {k: [] for k in META}
    for (cid, c, p), v in cache.items():
        if cid not in meta:
            continue
        r = meta[cid]
        X.append(v)
        cols["clip_id"].append(cid); cols["condition"].append(c); cols["prefix_s"].append(p)
        cols["y"].append(int(r["label"])); cols["generator"].append(r["generator"])
        cols["family"].append(r["family"]); cols["language"].append(r["language"])
        cols["source"].append(r["source"]); cols["parent"].append(r.get("parent", ""))
    np.savez_compressed(out, X=np.stack(X).astype(np.float32),
                        **{k: np.array(v) for k, v in cols.items()})
    print(f"wrote {len(X)} embeddings -> {out}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
