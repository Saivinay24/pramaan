#!/usr/bin/env python3
"""Show every number, at every stage, for one audio clip.

Walks a clip through the exact live path and prints what comes out of each step:
raw samples, the frozen model's per-frame features, the pooled 2048-number vector,
the standardiser, the classifier's dot product, the calibrator, the gate.

    scripts/explain.sh data/samples/human_hindi.wav
    scripts/explain.sh data/samples/clone_xtts_v2.wav --compare data/samples/human_hindi.wav
"""
import argparse, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
SR = 16000
np.set_printoptions(precision=3, suppress=True, linewidth=120)


def rule(t=""):
    print("\n" + "=" * 78)
    if t:
        print(t)
        print("=" * 78)


def walk(path, verbose=True):
    import torch, soundfile as sf
    from pramaan.frontend import Frontend
    from pramaan.model import load_bundle
    from pramaan.config import SSL_MODEL, SSL_LAYER, CLIP_S

    y, sr = sf.read(path, dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    y = y[:int(CLIP_S * SR)]

    if verbose:
        rule(f"STEP 0 · THE AUDIO   {os.path.basename(path)}")
        print(f"{len(y)} samples at {sr} Hz = {len(y)/sr:.2f} seconds of sound")
        print("each sample is loudness at one instant, between -1 and +1:")
        print("  first 12 :", y[:12])
        print(f"  loudest  : {np.abs(y).max():.3f}     average level: {np.sqrt((y**2).mean()):.4f}")
        print("\nThat is all the computer has. 64,000 numbers. Nothing about words or voices yet.")

    fe = Frontend()
    x = (y - y.mean()) / (y.std() + 1e-7)
    t = torch.from_numpy(x)[None].to(device=fe.device, dtype=fe.torch_dtype)
    with torch.inference_mode():
        out = fe.model(t, output_hidden_states=True)
    hs = out.hidden_states
    h = hs[SSL_LAYER][0].float().cpu().numpy()

    if verbose:
        rule(f"STEP 1 · THE FROZEN MODEL   {SSL_MODEL}")
        print(f"It has {sum(p.numel() for p in fe.model.parameters())/1e6:.0f} million numbers inside, and none of them change.")
        print(f"It chops the 4 seconds into {h.shape[0]} overlapping frames, one every {1000*len(y)/sr/h.shape[0]:.0f} ms,")
        print(f"and describes each frame with {h.shape[1]} numbers.")
        print(f"It produces {len(hs)} stages of description. We read stage {SSL_LAYER}.")
        print(f"\nSo stage {SSL_LAYER} is a table of {h.shape[0]} rows x {h.shape[1]} columns = {h.size:,} numbers.")
        print("  frame 0, first 10 of its 1024 numbers :", h[0][:10])
        print("  frame 1, first 10                     :", h[1][:10])
        print("  frame 100, first 10                   :", h[100][:10])
        print("\nThese are LEARNED features, not hand-designed ones. Nobody can point at column 37")
        print("and say 'that is pitch'. The model invented them while learning 128 languages.")
        print("What matters is that machine-made speech puts different values in them than a")
        print("human throat does, and that difference survives a phone line.")
        print("\nWhy stage 5 of 25: the early stages still describe HOW the sound was made")
        print("(texture, breath, micro-timing). The last stages have thrown that away and only")
        print("kept WHAT was said, which is useless for spotting a fake.")

    mean, std = h.mean(0), h.std(0)
    v = np.concatenate([mean, std])

    if verbose:
        rule("STEP 2 · SQUASH THE TABLE INTO ONE ROW")
        print(f"A call has no fixed length, so we summarise the {h.shape[0]} frames two ways:")
        print(f"  the AVERAGE of each column  -> {mean.shape[0]} numbers  (the typical texture of this voice)")
        print(f"  the SPREAD  of each column  -> {std.shape[0]} numbers  (how much it varies: humans vary more)")
        print(f"  glued together              -> {v.shape[0]} numbers, and this is the whole clip now")
        print("\n  average, first 8 :", mean[:8])
        print("  spread,  first 8 :", std[:8])
        print(f"\n  So 64,000 audio samples became {v.shape[0]} numbers. This is the only thing the")
        print("  classifier ever sees.")

    B = load_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"))
    head = B["head"]
    sc = head.named_steps["sc"]
    lr = head.named_steps["lr"]
    z = (v - sc.mean_) / sc.scale_
    contrib = lr.coef_[0] * z
    raw = float(contrib.sum() + lr.intercept_[0])

    if verbose:
        rule("STEP 3 · OUR CLASSIFIER")
        print(f"It is {lr.coef_.size + lr.intercept_.size:,} numbers: one weight per feature, plus one bias.")
        print("It works in two moves.\n")
        print("  Move 1, put every feature on the same scale, using the average and spread")
        print("  measured across the whole training set:")
        print("    raw feature 0    :", f"{v[0]:+.3f}")
        print("    training average :", f"{sc.mean_[0]:+.3f}", "  training spread:", f"{sc.scale_[0]:.3f}")
        print("    so scaled        :", f"{z[0]:+.3f}", " (how unusual this clip is on that feature)")
        print("\n  Move 2, multiply each scaled feature by its weight and add everything up:")
        print(f"    score = bias {lr.intercept_[0]:+.3f}")
        for i in np.argsort(-np.abs(contrib))[:5]:
            half = "average" if i < 1024 else "spread"
            print(f"          + weight {lr.coef_[0][i]:+7.3f} x feature {i:4d} ({half:7s}) = {contrib[i]:+7.3f}")
        print(f"          + {v.shape[0]-5} more terms")
        print(f"    ---------------------------------------------")
        print(f"    raw score = {raw:+.3f}")
        pos = contrib[contrib > 0].sum(); neg = contrib[contrib < 0].sum()
        print(f"\n  Evidence pushing towards SYNTHETIC: {pos:+.1f}")
        print(f"  Evidence pushing towards HUMAN     : {neg:+.1f}")
        print(f"  Net                                : {raw:+.1f}   ({'synthetic' if raw > 0 else 'human'} side)")
        wm = np.abs(lr.coef_[0][:1024]).sum(); ws = np.abs(lr.coef_[0][1024:]).sum()
        print(f"\n  Of the total decision weight, {100*wm/(wm+ws):.0f}% sits on the AVERAGE half")
        print(f"  and {100*ws/(wm+ws):.0f}% on the SPREAD half. Both matter.")

    cal = B["calibrators"][4.0]
    # The commit band is per channel; a file handed to this script carries no channel, so
    # the clean-line band is the right one to show. See streaming.band_by_channel for the rest.
    band = B["band"][4.0]
    p = float(cal.predict_proba([raw])[0])

    if verbose:
        rule("STEP 4 · TURN THE SCORE INTO AN HONEST PROBABILITY")
        print(f"The raw score {raw:+.2f} means nothing to an operator. The calibrator was fitted on")
        print("held-out clips: it looked at every score and recorded what fraction of clips at that")
        print("score were really synthetic. It is a lookup table, so 0.8 genuinely means 80%.")
        print(f"\n  raw {raw:+.3f}  ->  P(synthetic) = {p:.2f}")
        print("\n  a few other scores, through the same table:")
        for probe in [-20, -10, -5, 0, 5, 10, 20]:
            print(f"    raw {probe:+4d}  ->  {float(cal.predict_proba([probe])[0]):.2f}")
        print("\n  There are 8 of these tables, one per audio length, because a score from 1.5")
        print("  seconds and a score from 4 seconds do not mean the same thing.")

        rule("STEP 5 · THE GATE DECIDES WHETHER TO SPEAK")
        print(f"  commit SYNTHETIC if P >= {band['tau_clone']:.3f}   (clean-line band; a G.723.1 line uses a higher one)")
        print(f"  commit HUMAN     if P <= {band['tau_human']:.3f}")
        print(f"  anything between is the undecidable band: DEFER, and escalate to the ladder")
        print(f"  and never before 1.5 s of audio, and only if the score held steady for 3 updates.")
        verdict = "SYNTHETIC" if p >= band["tau_clone"] else "HUMAN" if p <= band["tau_human"] else "DEFER"
        print(f"\n  P = {p:.2f}  ->  {verdict}")
        rule("SUMMARY OF THE WHOLE JOURNEY")
        print(f"  64,000 audio samples")
        print(f"    -> {h.shape[0]} frames x {h.shape[1]} learned features   (frozen model, 300M numbers, unchanged)")
        print(f"    -> {v.shape[0]} numbers                     (average and spread)")
        print(f"    -> 1 raw score  {raw:+.2f}              (our {lr.coef_.size+1:,}-number classifier)")
        print(f"    -> 1 probability {p:.2f}                (calibrator)")
        print(f"    -> {verdict}                        (gate)")
    return dict(y=y, h=h, v=v, z=z, raw=raw, p=p, contrib=contrib, verdict=(
        "SYNTHETIC" if p >= band["tau_clone"] else "HUMAN" if p <= band["tau_human"] else "DEFER"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--compare", help="a second clip to put side by side")
    a = ap.parse_args()
    r1 = walk(a.file)
    if a.compare:
        r2 = walk(a.compare, verbose=False)
        rule("SIDE BY SIDE")
        n1, n2 = os.path.basename(a.file)[:34], os.path.basename(a.compare)[:34]
        print(f"{'':22s} {n1:>26s} {n2:>26s}")
        for lab, k in [("average feature 0", None), ("raw score", "raw"), ("P(synthetic)", "p"), ("verdict", "verdict")]:
            if k is None:
                print(f"{lab:22s} {r1['v'][0]:26.3f} {r2['v'][0]:26.3f}")
            elif k == "verdict":
                print(f"{lab:22s} {r1[k]:>26s} {r2[k]:>26s}")
            else:
                print(f"{lab:22s} {r1[k]:26.3f} {r2[k]:26.3f}")
        d = np.abs(r1["z"] - r2["z"])
        print(f"\nThe two 2048-number descriptions differ most on features: {list(np.argsort(-d)[:6])}")
        print(f"Average difference across all 2048 features: {d.mean():.2f} standard deviations")


if __name__ == "__main__":
    main()
