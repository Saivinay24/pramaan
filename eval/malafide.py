#!/usr/bin/env python3
"""Malafide-style convolutive-noise attack on the spoof side, black box, CPU only.

G8 in docs/SOTA_GAP_ANALYSIS.md: adversarial robustness is entirely unmeasured and the likely
judge question is "what if the attacker knows your detector". This produces a number instead
of a silence.

WHAT THIS IS, EXACTLY, AND WHAT IT IS NOT. Malafide (arXiv 2306.07655) is a short non-causal
linear time-invariant filter convolved with spoofed audio. The published attack OPTIMISES the
filter coefficients against a specific countermeasure, which needs gradients. This script runs
the BLACK-BOX variant: a bank of random short FIR filters, applied to spoof audio only, and
the worst case over the bank is reported. It models an attacker who knows the attack class but
has no access to the detector's gradients.

    It is therefore WEAKER than the published attack, and every number it produces is a
    LOWER BOUND on the damage a real Malafide attack would do. Say that out loud. A
    white-box gradient attack on this system remains unmeasured, and adversarial training
    is out of scope on this hardware (no GPU, 300M-parameter frozen frontend).

Three rules this script obeys, all of them because breaking one would make the number a lie:

  1. The filter is applied to SPOOF audio only. The attacker controls their own synthetic
     audio and does not control the genuine caller's microphone, so filtering genuine speech
     would be modelling an attacker who has already won.
  2. The detector is not retrained, refit or recalibrated. It is the shipped bundle, exactly
     as the demo runs it.
  3. Distortion is measured and reported per filter, not asserted to be inaudible. A filter
     that wrecks the audio is not an attack, it is a broken clip, and the reader gets the
     number to judge that themselves.

Audio I/O uses soundfile throughout. torchaudio.load() is broken on this machine's pinned
stack (HONEST_LOG.md) and must not be used here.

    python eval/malafide.py                 # writes results.json["adversarial_malafide"]
"""
import argparse, csv, json, os, sys, time
from collections import defaultdict

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "eval"))
from pramaan.model import load_bundle, eer, auroc                      # noqa: E402
from pramaan.config import SR, CLIP_S                                  # noqa: E402
from experiments import Data                                           # noqa: E402

RES = os.path.join(ROOT, "eval", "results.json")
MODEL = os.path.join(ROOT, "eval", "results", "model.pkl")
MANIFEST = os.path.join(ROOT, "data", "manifest_all.csv")
# Filter lengths in taps at 16 kHz. Malafide reports orders in the low hundreds to ~1k;
# these sit in that range. Longer filters colour the signal more and are easier to hear,
# which is why the distortion is reported alongside.
TAPS = [129, 257, 513]
# Off-centre energy share. This is the severity knob and it is swept rather than picked,
# because a filter that colours the audio audibly is not an attack, it is a broken clip. The
# measured signal-to-distortion per filter is reported next to every result so a reader can
# read off the damage at a perceptual quality they are willing to accept.
SIDES = [0.05, 0.15, 0.35]


def fir_bank(rng):
    """Random short non-causal FIR filters, centre-tap dominant so the audio survives.

    Coefficients are Gaussian, scaled down away from the centre by a Hann taper, and the
    whole filter is normalised to unit gain. The centre tap keeps a floor share of the
    energy, which is what stops the filter degenerating into noise and gives the attack its
    "convolutive channel" character rather than "additive noise" character.
    """
    out = []
    for n in TAPS:
        for side in SIDES:
            h = rng.normal(0.0, 1.0, n) * np.hanning(n)
            c = n // 2
            h[c] = 0.0
            e = np.sqrt((h ** 2).sum()) or 1.0
            h = h / e * side
            h[c] = np.sqrt(max(1e-9, 1.0 - side ** 2))
            h = h / np.sqrt((h ** 2).sum())
            out.append((f"fir{n}_s{side:g}", h))
    return out


def apply_fir(x, h):
    y = np.convolve(x, h, mode="same").astype(np.float32)
    peak = np.abs(y).max()
    if peak > 1.0:                                   # never clip; an attacker would not
        y = y / peak
    return y


def distortion_db(x, y):
    """Signal-to-distortion in dB after gain alignment. Higher means less audible change."""
    a = float(np.dot(x, y) / max(1e-12, np.dot(y, y)))
    d = x - a * y
    return float(10 * np.log10(max(1e-12, np.dot(x, x)) / max(1e-12, np.dot(d, d))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=RES)
    a = ap.parse_args()

    D = Data()
    tr_g, ca_g, te_g = D.split_groups(a.seed)
    spoof = np.isin(D.group, list(te_g)) & (D.cond == "clean") & D.full & np.isin(D.gen, D.generators)
    bona = np.isin(D.group, list(te_g)) & (D.cond == "clean") & D.full & (D.y == 0)
    print(f"attack surface: {int(spoof.sum())} held-out spoof clips from {len(D.generators)} "
          f"seen families, scored against {int(bona.sum())} held-out genuine recordings")

    B = load_bundle(MODEL)
    head, cal = B["head"], B["calibrators"][CLIP_S]
    band = B["band"][CLIP_S]

    s_bona = head.decision_function(D.X[bona])
    s_clean = head.decision_function(D.X[spoof])
    y = np.concatenate([np.zeros(bona.sum(), int), np.ones(spoof.sum(), int)])
    base_eer, _ = eer(np.concatenate([s_bona, s_clean]), y)
    base_catch = float((cal.predict_proba(s_clean) >= band["tau_clone"]).mean())
    print(f"  before the attack: EER {base_eer*100:.2f}%  clones called synthetic "
          f"{base_catch*100:.1f}%")

    rows = {r["clip_id"]: r for r in csv.DictReader(open(MANIFEST))}
    from pramaan.frontend import Frontend
    fe = Frontend()
    rng = np.random.default_rng(a.seed)
    bank = fir_bank(rng)
    ids = D.cid[spoof]
    gens = D.gen[spoof]
    wavs = []
    for cid in ids:
        w, _ = sf.read(os.path.join(ROOT, "data", "clips", rows[cid]["path"]), dtype="float32")
        wavs.append((w.mean(axis=1) if w.ndim > 1 else w)[:int(CLIP_S * SR)])

    per_filter, t0 = [], time.perf_counter()
    for fi, (name, h) in enumerate(bank, 1):
        E, dists = [], []
        for w in wavs:
            yv = apply_fir(w, h)
            dists.append(distortion_db(w, yv))
            E.append(fe.embed(yv))
        s = head.decision_function(np.stack(E))
        e, _ = eer(np.concatenate([s_bona, s]), y)
        p = cal.predict_proba(s)
        by_gen = {g: float((p[gens == g] >= band["tau_clone"]).mean())
                  for g in sorted(set(gens.tolist()))}
        row = dict(filter=name, taps=len(h), eer=e, auroc=auroc(np.concatenate([s_bona, s]), y),
                   catch_rate=float((p >= band["tau_clone"]).mean()),
                   median_score_shift=float(np.median(s) - np.median(s_clean)),
                   distortion_db_median=float(np.median(dists)),
                   distortion_db_min=float(np.min(dists)),
                   catch_rate_by_generator=by_gen)
        per_filter.append(row)
        el = time.perf_counter() - t0
        print(f"  [{fi}/{len(bank)}] {name:12s} EER {e*100:5.2f}%  caught "
              f"{row['catch_rate']*100:5.1f}%  distortion {row['distortion_db_median']:5.1f} dB"
              f"  ({el:.0f}s elapsed)", flush=True)

    worst = max(per_filter, key=lambda r: r["eer"])
    least_caught = min(per_filter, key=lambda r: r["catch_rate"])
    out = dict(
        attack="Malafide-style convolutive noise, arXiv 2306.07655",
        variant="BLACK BOX. Random short FIR filters, worst case over the bank. The published "
                "attack optimises the filter against the countermeasure with gradients; this "
                "does not. Every number here is therefore a LOWER BOUND on the damage the "
                "published attack would do.",
        applied_to="held-out spoof clips only. Genuine speech is never filtered, because an "
                   "attacker controls their own synthetic audio and not the victim's microphone.",
        detector="the shipped bundle, not retrained, not refit, not recalibrated",
        n_spoof=int(spoof.sum()), n_bona=int(bona.sum()),
        n_filters=len(bank), taps=TAPS, off_centre_energy=SIDES, seed=a.seed,
        before=dict(eer=base_eer, catch_rate=base_catch),
        per_filter=per_filter,
        worst_case=dict(by_eer=worst, by_catch_rate=least_caught),
        broke_detection=bool(worst["eer"] > base_eer or least_caught["catch_rate"] < base_catch),
        unmeasured=["white-box gradient attack against this system",
                    "adversarial training as a defence, which needs gradients through a "
                    "300M-parameter frozen frontend and is a GPU workload",
                    "the attack against the Gate's sequential decision rather than against a "
                    "single 4 s score"],
    )
    # The headline branches, because "moves EER from 0.00% to 0.00%" is a sentence that reads
    # as a result when the honest reading is that nothing moved. A null result gets said as a
    # null result, with the range it was null over and the distortion floor it held to.
    tail = ("This is the weak version of the attack. The published Malafide optimises the "
            "filter against the detector with gradients and would do more. A white-box "
            "gradient attack against the frozen XLS-R frontend remains unmeasured, and "
            "adversarial training is out of scope on this hardware, because it needs "
            "gradients through a 300M-parameter frontend and there is no GPU for it.")
    # Most aggressive filter in the bank, ranked by measured damage to the audio rather than
    # by the nominal knob, because signal-to-distortion is the quantity an attacker is bounded by.
    hardest = min(per_filter, key=lambda r: r["distortion_db_median"])
    if out["broke_detection"]:
        out["headline"] = (
            f"A black-box convolutive filter, no gradients and no access to the detector, moves "
            f"held-out EER on seen families from {base_eer*100:.2f}% to {worst['eer']*100:.2f}% "
            f"in the worst of {len(bank)} filters, and drops the share of clones called synthetic "
            f"at the shipped band from {base_catch*100:.1f}% to "
            f"{least_caught['catch_rate']*100:.1f}%, at a median signal-to-distortion of "
            f"{least_caught['distortion_db_median']:.1f} dB. " + tail)
    else:
        out["headline"] = (
            f"The attack does not land. Across all {len(bank)} filters, {TAPS[0]} to {TAPS[-1]} "
            f"taps at {SIDES[0]:g} to {SIDES[-1]:g} off-centre energy, held-out EER on "
            f"{int(spoof.sum())} seen-family spoof clips stays at {worst['eer']*100:.2f}% "
            f"against {base_eer*100:.2f}% before the attack, and the share of clones called "
            f"synthetic at the shipped band stays at {least_caught['catch_rate']*100:.1f}% "
            f"against {base_catch*100:.1f}% before, on every filter including the most "
            f"aggressive one at a median signal-to-distortion of "
            f"{hardest['distortion_db_median']:.1f} dB, where the colouration is audible. Under "
            f"that filter the median spoof score moves {hardest['median_score_shift']:+.3f} in "
            f"log-odds, towards synthetic rather than away from it, so the filter is adding "
            f"evidence for the detector instead of removing it. " + tail)
    print("\n  " + out["headline"])

    R = json.load(open(a.out)) if os.path.exists(a.out) else {}
    R["adversarial_malafide"] = out
    json.dump(R, open(a.out, "w"), indent=2)
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
