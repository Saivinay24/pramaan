#!/usr/bin/env python3
"""What is the detector actually responding to?

The 2048 features are learned, so no single one has a human name. But we can probe:
measure ordinary, nameable acoustic properties on real and synthetic clips, and see
which of them line up with the classifier's score. That turns "the model decided for
itself" into an evidence-backed answer.

    python eval/what_it_hears.py --n 400
"""
import argparse, csv, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
SR = 16000
OUT = os.path.join(ROOT, "eval", "results", "what_it_hears.json")


def measures(y):
    """Ordinary acoustic measurements a human can name."""
    import librosa
    out = {}
    S = np.abs(librosa.stft(y, n_fft=512, hop_length=160))
    freqs = librosa.fft_frequencies(sr=SR, n_fft=512)
    power = S ** 2 + 1e-12
    total = power.sum(0)

    # how much energy sits high up: vocoders often smooth the top end away
    out["high_freq_energy_above_5k"] = float((power[freqs > 5000].sum(0) / total).mean())
    out["high_freq_energy_above_7k"] = float((power[freqs > 7000].sum(0) / total).mean())

    # spectral flatness: 0 = pure tone, 1 = noise. Breath and consonants add noise
    out["spectral_flatness"] = float(librosa.feature.spectral_flatness(S=S).mean())
    # brightness
    out["spectral_centroid_hz"] = float(librosa.feature.spectral_centroid(S=S, sr=SR).mean())
    # how fast the spectrum changes moment to moment
    out["spectral_flux"] = float(np.mean(np.sqrt(((np.diff(S, axis=1)) ** 2).sum(0))))

    # pitch: humans wobble more
    f0 = librosa.yin(y, fmin=60, fmax=400, sr=SR, frame_length=1024)
    f0 = f0[np.isfinite(f0)]
    out["pitch_mean_hz"] = float(np.mean(f0)) if len(f0) else 0.0
    out["pitch_variation"] = float(np.std(f0)) if len(f0) else 0.0
    out["pitch_jitter"] = float(np.mean(np.abs(np.diff(f0)))) if len(f0) > 1 else 0.0

    # loudness: humans vary, and leave real pauses
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=160)[0]
    out["loudness_variation"] = float(rms.std() / (rms.mean() + 1e-9))
    out["shimmer"] = float(np.mean(np.abs(np.diff(rms))) / (rms.mean() + 1e-9))
    q = np.quantile(rms, 0.15)
    out["silence_fraction"] = float((rms < q * 1.5).mean())
    out["dynamic_range_db"] = float(20 * np.log10((rms.max() + 1e-9) / (np.quantile(rms, 0.05) + 1e-9)))

    # roughness of the waveform itself
    out["zero_crossing_rate"] = float(librosa.feature.zero_crossing_rate(y, frame_length=1024, hop_length=160).mean())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    import soundfile as sf
    from pramaan.frontend import Frontend
    from pramaan.model import load_bundle

    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "manifest_all.csv"))))
    rng = np.random.default_rng(a.seed)
    bona = [r for r in rows if r["label"] == "0"]
    spoof = [r for r in rows if r["label"] == "1"]
    rng.shuffle(bona); rng.shuffle(spoof)
    pick = bona[:a.n // 2] + spoof[:a.n // 2]

    B = load_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"))
    head = B["head"]
    fe = Frontend()
    lr = head.named_steps["lr"]

    names, X, y, gen = None, [], [], []
    scores = []
    for i, r in enumerate(pick, 1):
        w, _ = sf.read(os.path.join(ROOT, "data", "clips", r["path"]), dtype="float32")
        if w.ndim > 1:
            w = w.mean(axis=1)
        try:
            m = measures(w)
        except Exception as e:
            continue
        if names is None:
            names = list(m)
        X.append([m[k] for k in names]); y.append(int(r["label"])); gen.append(r["generator"])
        scores.append(float(head.decision_function(fe.embed(w)[None])[0]))
        if i % 50 == 0:
            print(f"  {i}/{len(pick)}", flush=True)
    X = np.array(X); y = np.array(y); scores = np.array(scores)

    print(f"\n{len(X)} clips: {(y==0).sum()} human, {(y==1).sum()} synthetic\n")
    print(f"{'acoustic property':28s} {'human avg':>11s} {'synthetic avg':>14s} {'gap':>7s}  {'agrees with the model':>21s}")
    print("-" * 92)
    res = []
    for j, nm in enumerate(names):
        h, s = X[y == 0, j], X[y == 1, j]
        pooled = np.sqrt((h.var() + s.var()) / 2) + 1e-12
        d = (s.mean() - h.mean()) / pooled          # effect size, in standard deviations
        corr = float(np.corrcoef(X[:, j], scores)[0, 1])
        res.append(dict(name=nm, human_mean=float(h.mean()), synthetic_mean=float(s.mean()),
                        effect_size=float(d), correlation_with_score=corr))
    res.sort(key=lambda r: -abs(r["effect_size"]))
    for r in res:
        arrow = "higher in fakes" if r["effect_size"] > 0 else "lower in fakes "
        print(f"{r['name']:28s} {r['human_mean']:11.3f} {r['synthetic_mean']:14.3f} "
              f"{r['effect_size']:+6.2f}s  {arrow}  r={r['correlation_with_score']:+.2f}")

    # how much of the decision weight sits on the average half vs the spread half
    wm = float(np.abs(lr.coef_[0][:1024]).sum()); ws = float(np.abs(lr.coef_[0][1024:]).sum())
    print(f"\nDecision weight: {100*wm/(wm+ws):.0f}% on the AVERAGE of the frames, "
          f"{100*ws/(wm+ws):.0f}% on how much they VARY.")

    json.dump(dict(n_clips=int(len(X)), properties=res,
                   weight_on_average_half=wm / (wm + ws),
                   weight_on_variation_half=ws / (wm + ws),
                   note="effect size is in standard deviations; correlation is against the classifier's raw score"),
              open(OUT, "w"), indent=1)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
