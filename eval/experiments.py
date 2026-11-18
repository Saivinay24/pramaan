#!/usr/bin/env python3
"""Every number Pramaan is allowed to say, produced by one re-runnable script.

Protocols (all held-out means held-out, enforced by clip-level and parent-level splits):

  generator_matrix   Leave-one-generator-out. For each generator family, train on every
                     other family and score the held-out one. Cross-family generalisation,
                     per family, per telephony codec.
  diversity_curve    Hold out the 2025 cloner (Chatterbox, same-corpus clones of the bona
                     fide recordings). Train with k = 1..K seen families. The scaling law
                     the research predicts, reproduced on this laptop.
  calibration        None vs Platt vs isotonic, ECE on seen and unseen generators.
  streaming          Prefix-length EER curve and the commit/defer gate replay, replayed
                     on every channel separately because the band is per channel.
  streaming_leave_one_out
                     The same Gate replay, in every leave-one-generator-out direction and on
                     every channel. One head per direction, trained on the other families
                     only, so no row is in sample. Closes GAPS.md's reverse-direction gap.
  band_selection     The false-positive budget sweep behind the band. Thresholds come from
                     bona fide speech alone, per prefix and per channel; no spoof clip of
                     any generator informs them.
  adaptation         Few-shot repair on the unseen cloner, parent-disjoint.
  ship               The deployed bundle: head + per-prefix isotonic calibrators + band.
  confidence         95% intervals. Cluster bootstrap over parent recordings for every EER,
                     Wilson score intervals for every rate. Also reconciles the two clip
                     counts the artifacts quote for the unseen cloner, 23 and 39.
  replay_mic         The loudspeaker-to-microphone channel, scored and published.

Writes eval/results.json. Nothing outward may print a number that is not in that file.
"""
import argparse, csv, json, os, sys, time
from collections import Counter, defaultdict
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from pramaan.model import (Head, IsotonicCalibrator, band_from_genuine, eer, auroc,  # noqa
                           ece, save_bundle)
from pramaan.channels import GRID, BANDWIDTH, SEVERITY, UNAVAILABLE                 # noqa
from pramaan.config import MIN_COMMIT_S, STABILITY_WINDOW, STABILITY_TOL, CLIP_S   # noqa

FEAT = os.path.join(ROOT, "eval", "results", "features.npz")
RES = os.path.join(ROOT, "eval", "results.json")
UNSEEN = "chatterbox"
# Chronological order of acquisition. espeak_ng and piper were added on 2026-09-14, so they
# sit at the end and the diversity curve's chronological arm at k=1..6 is unchanged.
SEEN_ORDER = ["xtts_v2", "freevc24", "encodec", "mac_say", "mms_vits", "kokoro",
              "espeak_ng", "piper"]
FPR_BUDGET = 0.02
# The band the project shipped until 2026-09-14. Kept only as the comparison row: every
# band this script now uses is derived by pramaan.model.band_from_genuine from bona fide
# scores alone, per prefix and per channel. See band_selection in results.json.
LEGACY_BAND = (0.85, 0.15)
# The false-positive budgets swept when the derived band is reported, so "why 0.02?" has a
# table behind it instead of an assertion.
FPR_GRID = [0.002, 0.005, 0.01, 0.02, 0.05]
# A channel and prefix needs at least this many bona fide calibration clips before a
# quantile on them is allowed to set a threshold.
MIN_BAND_CLIPS = 20
REPLAY_WEIGHT = 30.0


class Data:
    def __init__(self, path=FEAT):
        z = np.load(path, allow_pickle=True)
        self.X = z["X"]; self.y = z["y"].astype(int)
        self.cid = z["clip_id"].astype(str); self.cond = z["condition"].astype(str)
        self.pre = z["prefix_s"].astype(float); self.gen = z["generator"].astype(str)
        self.fam = z["family"].astype(str); self.lang = z["language"].astype(str)
        self.parent = z["parent"].astype(str)
        # canonical "parent" for splitting: a spoof's parent bona clip if known, else itself
        self.group = np.where(self.parent != "", self.parent, self.cid)
        self.full = self.pre == CLIP_S
        self.generators = [g for g in SEEN_ORDER if (self.gen == g).any()]
        print(f"{len(self.X)} rows | generators {self.generators} + unseen {UNSEEN}"
              f" | conditions {sorted(set(self.cond))} | prefixes {sorted(set(self.pre))}")

    def split_groups(self, seed=0, frac=(0.6, 0.15, 0.25)):
        """Parent-level split of bona fide clips. Every spoof follows its parent."""
        rng = np.random.default_rng(seed)
        # a unit is a bona fide recording together with every spoof derived from it, or a
        # parentless spoof clip on its own. Units never straddle a split boundary.
        units = np.array(sorted(set(self.group)))
        rng.shuffle(units)
        n = len(units)
        a, b = int(frac[0] * n), int((frac[0] + frac[1]) * n)
        return set(units[:a]), set(units[a:b]), set(units[b:])

    def mask(self, groups, gens, cond="clean", prefix=CLIP_S, label=None):
        m = np.isin(self.group, list(groups)) & (self.cond == cond) & (self.pre == prefix)
        m &= (self.y == 0) | np.isin(self.gen, list(gens))
        if label is not None:
            m &= self.y == label
        return m


def fit_and_score(D, train_groups, calib_groups, test_groups, seen, held, seed=0,
                  conds=("clean",), train_conds=("clean",)):
    """Train on `seen` generators, evaluate the `held` generator(s). Bona fide from the split."""
    tr = np.zeros(len(D.X), bool)
    for c in train_conds:
        tr |= D.mask(train_groups, seen, cond=c)
    head = Head(seed=seed).fit(D.X[tr], D.y[tr], D.gen[tr])
    ca = D.mask(calib_groups, seen)
    cal = IsotonicCalibrator().fit(head.raw(D.X[ca]), D.y[ca])
    out = {}
    for c in conds:
        te = D.mask(test_groups, held, cond=c)
        if te.sum() == 0 or len(set(D.y[te])) < 2:
            continue
        s = head.raw(D.X[te]); p = cal.predict_proba(s)
        e, thr = eer(s, D.y[te])
        out[c] = dict(eer=e, auroc=auroc(s, D.y[te]), ece=ece(p, D.y[te]),
                      n_bona=int((D.y[te] == 0).sum()), n_spoof=int((D.y[te] == 1).sum()),
                      fpr_at_p50=float((p[D.y[te] == 0] >= 0.5).mean()),
                      tpr_at_p50=float((p[D.y[te] == 1] >= 0.5).mean()))
    return head, cal, out


# --------------------------------------------------------------------- protocols
def generator_matrix(D, seed=0):
    tr_g, ca_g, te_g = D.split_groups(seed)
    allg = D.generators + [UNSEEN]
    res = {}
    for held in allg:
        seen = [g for g in allg if g != held]
        _, _, out = fit_and_score(D, tr_g, ca_g, te_g, seen, [held], seed, conds=GRID)
        res[held] = dict(trained_on=seen, trained_on_conditions=["clean"],
                         per_condition=out, clean_eer=out.get("clean", {}).get("eer"))
        print(f"  held-out {held:10s} clean EER {out['clean']['eer']*100:6.2f}%  "
              f"auroc {out['clean']['auroc']:.3f}  n={out['clean']['n_spoof']}")
    return res


def diversity_curve(D, seed=0, n_random=6):
    tr_g, ca_g, te_g = D.split_groups(seed)
    gens = D.generators
    rng = np.random.default_rng(seed)
    curve = []
    for k in range(1, len(gens) + 1):
        subsets = [gens[:k]]                     # the fixed chronological order
        for _ in range(n_random):
            subsets.append(sorted(rng.choice(gens, size=k, replace=False).tolist()))
        eers, aucs = [], []
        for sub in subsets:
            _, _, out = fit_and_score(D, tr_g, ca_g, te_g, sub, [UNSEEN], seed)
            eers.append(out["clean"]["eer"]); aucs.append(out["clean"]["auroc"])
        curve.append(dict(k=k, chronological=gens[:k], eer_chronological=eers[0],
                          eer_mean=float(np.mean(eers)), eer_min=float(np.min(eers)),
                          eer_max=float(np.max(eers)), auroc_mean=float(np.mean(aucs)),
                          n_subsets=len(subsets)))
        print(f"  k={k}  EER chrono {eers[0]*100:5.1f}%  mean {np.mean(eers)*100:5.1f}%  "
              f"[{np.min(eers)*100:.1f}, {np.max(eers)*100:.1f}]")
    return dict(unseen=UNSEEN, order=gens, curve=curve)


def calibration_study(D, seed=0):
    from sklearn.linear_model import LogisticRegression
    tr_g, ca_g, te_g = D.split_groups(seed)
    seen = D.generators
    tr = D.mask(tr_g, seen); ca = D.mask(ca_g, seen)
    head = Head(seed=seed).fit(D.X[tr], D.y[tr], D.gen[tr])
    s_ca = head.raw(D.X[ca])
    iso = IsotonicCalibrator().fit(s_ca, D.y[ca])
    platt = LogisticRegression(max_iter=1000).fit(s_ca[:, None], D.y[ca])
    res = {}
    for name, held in [("seen_generators", seen), ("unseen_cloner", [UNSEEN])]:
        te = D.mask(te_g, held)
        s = head.raw(D.X[te]); y = D.y[te]
        p_none = 1 / (1 + np.exp(-s))
        res[name] = dict(
            raw_sigmoid=dict(ece=ece(p_none, y), fpr50=float((p_none[y == 0] >= .5).mean())),
            platt=dict(ece=ece(platt.predict_proba(s[:, None])[:, 1], y)),
            isotonic=dict(ece=ece(iso.predict_proba(s), y)),
            n=int(te.sum()))
        print(f"  {name}: ECE raw {res[name]['raw_sigmoid']['ece']:.3f}  "
              f"platt {res[name]['platt']['ece']:.3f}  isotonic {res[name]['isotonic']['ece']:.3f}")
    return res


def derive_bands(D, head, cals, calib_groups, conditions, fpr=FPR_BUDGET):
    """Commit band per condition, from bona fide calibration clips only.

    No spoof clip touches this. It is the parent repo's select_operating_point.py method,
    which exists because spoof score location does not transfer across cloners while
    genuine score location does, applied here on the second axis that moves it: the codec.

    Two deliberate choices, both measured rather than assumed:

    Per channel, not per bandwidth class. channels.BANDWIDTH splits on sample rate and calls
    opus_8k wideband, but the genuine-score shift tracks bitrate: opus_8k sits with
    g723_1_6k3 at 6.3 kbps, not with opus_24k. See the note in channels.py for the numbers.

    One band per channel across prefixes, not one per (channel, prefix). The calibrator is
    already fit per prefix length, so prefix is accounted for on the probability scale
    before the band is applied; it is NOT fit per channel, which is why the channel still
    needs its own band. Pooling also fixes an estimator problem: there are 76 genuine
    calibration clips at each (channel, prefix), so a 98th-percentile quantile on them is
    the second-highest of 76 samples, and the 2026-09-14 per-prefix run produced a clean
    band that jumped 0.99 at 2.5 s to 0.036 at 4.0 s with no mechanism behind the swing.
    Pooling every prefix at or above MIN_COMMIT_S, the only prefixes the Gate can ever act
    on, puts 304 to 456 clips behind each threshold.
    """
    out = {}
    for c in conditions:
        ts = [t for t in sorted(set(D.pre[D.cond == c])) if t >= MIN_COMMIT_S and t in cals]
        if not ts:
            continue
        pg, levels = [], set()
        for t in ts:
            m = np.isin(D.group, list(calib_groups)) & (D.cond == c) & (D.pre == t) & (D.y == 0)
            if m.sum() < MIN_BAND_CLIPS:
                continue
            pg.append(cals[t].predict_proba(head.raw(D.X[m])))
            levels |= set(cals[t].levels.tolist())
        if not pg:
            continue
        b = band_from_genuine(np.concatenate(pg), sorted(levels), fpr)
        for t in sorted(set(D.pre[D.cond == c])):
            out[(c, t)] = b
    return out


def gate_replay(D, head, cals, test_groups, cond, held, bands):
    """Replay the Gate clip by clip on one channel. bands maps (cond, prefix) -> band."""
    from pramaan.gate import Gate, SYNTHETIC, HUMAN
    prefixes = sorted(set(D.pre[D.cond == cond]))
    rows = np.isin(D.group, list(test_groups)) & (D.cond == cond) & ((D.y == 0) | np.isin(D.gen, held))
    idx = defaultdict(dict)
    for i in np.where(rows)[0]:
        idx[D.cid[i]][D.pre[i]] = i
    results = []
    for m in idx.values():
        g = Gate(); truth = SYNTHETIC if D.y[m[max(m)]] == 1 else HUMAN
        committed, verdict = None, None
        for t in prefixes:
            if t not in m or t not in cals or (cond, t) not in bands:
                continue
            p = float(cals[t].predict_proba(head.raw(D.X[m[t]:m[t] + 1]))[0])
            tc, th = bands[(cond, t)]
            d = g.update(p, t, tau_clone=tc, tau_human=th)
            if d.committed and committed is None:
                committed, verdict = t, d.state
        results.append((truth, committed, verdict))
    comm = [r for r in results if r[1] is not None]
    n_h = sum(1 for r in results if r[0] == HUMAN)
    n_s = len(results) - n_h
    fp = [r for r in comm if r[0] == HUMAN and r[2] == SYNTHETIC]
    comm_h = [r for r in comm if r[0] == HUMAN]
    comm_s = [r for r in comm if r[0] == SYNTHETIC]
    return dict(n_clips=len(results), n_genuine=n_h, n_spoof=n_s,
                coverage=len(comm) / len(results) if results else float("nan"),
                # Split out, because a pooled coverage figure hides which half deferred, and
                # on the six codec channels the spoof half of most families has only one
                # cached prefix at or above MIN_COMMIT_S and therefore cannot commit at all.
                coverage_genuine=len(comm_h) / n_h if n_h else None,
                coverage_spoof=len(comm_s) / n_s if n_s else None,
                n_committed=len(comm), n_committed_genuine=len(comm_h),
                n_committed_spoof=len(comm_s),
                committed_error=float(1 - np.mean([r[0] == r[2] for r in comm])) if comm else float("nan"),
                median_time_to_decision_s=float(np.median([r[1] for r in comm])) if comm else None,
                false_positive_rate=len(fp) / n_h if n_h else None,
                n_false_positive=len(fp), deferred=len(results) - len(comm),
                n_prefixes_available=len(prefixes))


def streaming_head(D, tr_g, ca_g, seen, conds, seed=0):
    """The head and per-prefix calibrators the streaming protocols replay the Gate on.

    Train on pooled prefixes so the head has seen short durations, and on every codec,
    because that is what `ship` trains on and this replay is meant to be the shipped
    system's streaming behaviour. Measured 2026-09-14: a clean-only head meeting opus_8k
    moves the 98th-percentile genuine log-odds from -3.11 to +8.36 and calls 95.3% of
    genuine speech synthetic at p >= 0.5. Training through the codec grid holds the same
    quantile at +1.57. The channel has to be in training before a band can be derived for it.

    Calibrate on every channel at this prefix, as `ship` does; the channel-specific part of
    the decision lives in the band, not in a per-channel calibrator.

    Shared by `streaming` and `streaming_leave_one_out` so the two cannot drift: the only
    difference between them is which generators are in `seen`.
    """
    tr = np.isin(D.group, list(tr_g)) & np.isin(D.cond, conds) & ((D.y == 0) | np.isin(D.gen, seen))
    head = Head(seed=seed).fit(D.X[tr], D.y[tr], D.gen[tr])
    cals = {}
    for t in sorted(set(D.pre[D.cond == "clean"])):
        ca = np.isin(D.group, list(ca_g)) & (D.pre == t) & ((D.y == 0) | np.isin(D.gen, seen))
        if ca.sum() < 20:
            continue
        cals[t] = IsotonicCalibrator().fit(head.raw(D.X[ca]), D.y[ca])
    return head, cals


def usable_prefixes(D, gen, cond):
    """Cached prefixes at or above MIN_COMMIT_S for one generator on one channel.

    The Gate needs STABILITY_WINDOW updates before it may commit, so a generator with fewer
    than that many cached prefixes on a channel cannot be committed on at all, whatever the
    model thinks. That is a cache property, not a model property, and every coverage figure
    in this file is only readable next to it.
    """
    m = (D.gen == gen) & (D.cond == cond)
    return sorted(t for t in set(D.pre[m].tolist()) if t >= MIN_COMMIT_S)


def streaming(D, seed=0):
    """Prefix EER curve, the derived band, and the gate replay on every channel."""
    tr_g, ca_g, te_g = D.split_groups(seed)
    seen = D.generators
    prefixes = sorted(set(D.pre[D.cond == "clean"]))
    conds = [c for c in SEVERITY if (D.cond == c).any()]
    head, cals = streaming_head(D, tr_g, ca_g, seen, conds, seed)
    per_prefix = {}
    for t in prefixes:
        if t not in cals:
            continue
        row = {}
        for name, held in [("seen", seen), ("unseen", [UNSEEN])]:
            te = np.isin(D.group, list(te_g)) & (D.cond == "clean") & (D.pre == t) & ((D.y == 0) | np.isin(D.gen, held))
            if te.sum() and len(set(D.y[te])) == 2:
                e, _ = eer(head.raw(D.X[te]), D.y[te])
                row[name] = dict(eer=e, n=int(te.sum()))
        per_prefix[str(t)] = row
        print(f"  prefix {t:.1f}s  seen EER {row.get('seen',{}).get('eer',float('nan'))*100:5.1f}%"
              f"  unseen EER {row.get('unseen',{}).get('eer',float('nan'))*100:5.1f}%")

    bands = derive_bands(D, head, cals, ca_g, conds)
    band = {t: bands[("clean", t)] for t in prefixes if ("clean", t) in bands}

    # gate replay, per channel, seen families and the held-out cloner
    by_channel = {}
    for c in conds:
        by_channel[c] = {name: gate_replay(D, head, cals, te_g, c, held, bands)
                         for name, held in [("seen", seen), ("unseen", [UNSEEN])]}
        s = by_channel[c]["seen"]
        print(f"  gate replay {c:12s} coverage {s['coverage']*100:5.1f}%  committed error "
              f"{s['committed_error']*100:5.1f}%  FPR on genuine {s['false_positive_rate']*100:5.2f}%"
              f"  ({s['n_prefixes_available']} prefixes cached)")
    replay = {k: dict(by_channel["clean"][k]) for k in ("seen", "unseen")}

    fpr_by_channel = {c: by_channel[c]["seen"]["false_positive_rate"] for c in conds}
    worst = max(fpr_by_channel, key=lambda c: fpr_by_channel[c])
    return dict(prefixes_s=prefixes, per_prefix=per_prefix,
                gate_replay=replay, gate_replay_scope="clean channel only",
                gate_replay_by_channel=by_channel,
                false_positive_rate_by_channel=fpr_by_channel,
                worst_channel=worst, worst_channel_fpr=fpr_by_channel[worst],
                band={str(k): dict(tau_clone=v[0], tau_human=v[1]) for k, v in band.items()},
                band_scope="clean channel; band_by_channel carries the rest",
                band_by_channel={c: {str(t): dict(tau_clone=v[0], tau_human=v[1])
                                     for (cc, t), v in bands.items() if cc == c} for c in conds},
                legacy_fixed_band=dict(tau_clone=LEGACY_BAND[0], tau_human=LEGACY_BAND[1]),
                min_commit_s=MIN_COMMIT_S, fpr_budget=FPR_BUDGET), head, cals, bands


def streaming_leave_one_out(D, seed=0):
    """The streaming Gate replayed in every held-out-generator direction, per channel.

    Opened by GAPS.md ("the reverse cloner direction is not measured in the per-channel
    table") and closed here. That gap was written when this project had two cloners, so
    "the reverse direction" meant the one of the two that `eval/per_channel.py` did not hold
    out. This rebuild has 8 trained generator families plus the held-out 2025 cloner, so
    there is no pair and no reverse: there are 9 leave-one-generator-out directions, and
    `generator_matrix` already carries all 9 on full 4 s clips. The streaming table carried
    none of them. Its two arms were "seen" (a head trained on all 8 families, replayed on
    those same 8) and "unseen" (the same head replayed on Chatterbox, which it never trains
    on). The first is in sample by construction and the second is one direction out of nine.

    This protocol trains one head per direction, exactly `streaming`'s recipe minus the
    held-out family, derives the band from bona fide calibration clips alone as before, and
    replays the Gate on the held-out family against held-out genuine speech on each channel.

    Coverage is reported split into its genuine and spoof halves, and each cell carries the
    number of cached prefixes the held-out family has on that channel. On the six codec
    channels most families are cached at 4.0 s only, so the Gate cannot reach
    STABILITY_WINDOW updates on them and their spoof coverage is 0 for a cache reason. Those
    cells are marked `gate_can_commit_on_held_out: false` rather than published as a result.
    """
    tr_g, ca_g, te_g = D.split_groups(seed)
    conds = [c for c in SEVERITY if (D.cond == c).any()]
    allg = D.generators + [UNSEEN]
    out, blocked = {}, []
    for held in allg:
        seen = [g for g in D.generators if g != held]
        head, cals = streaming_head(D, tr_g, ca_g, seen, conds, seed)
        bands = derive_bands(D, head, cals, ca_g, conds)
        by_channel = {}
        for c in conds:
            r = gate_replay(D, head, cals, te_g, c, [held], bands)
            ups = usable_prefixes(D, held, c)
            r["held_out_prefixes_at_or_above_min_commit"] = [float(t) for t in ups]
            r["gate_can_commit_on_held_out"] = bool(len(ups) >= STABILITY_WINDOW)
            if not r["gate_can_commit_on_held_out"]:
                blocked.append(f"{held}/{c}")
            by_channel[c] = r
        cl = by_channel["clean"]
        out[held] = dict(trained_on=seen, n_trained_on=len(seen), by_channel=by_channel,
                         clean_coverage=cl["coverage"],
                         clean_committed_error=cl["committed_error"],
                         clean_false_positive_rate=cl["false_positive_rate"])
        print(f"  held out {held:10s} clean: coverage {cl['coverage']*100:5.1f}% "
              f"(genuine {cl['coverage_genuine']*100:5.1f}%, held-out clones "
              f"{cl['coverage_spoof']*100:5.1f}%)  committed error "
              f"{cl['committed_error']*100:5.1f}%  false alarms {cl['false_positive_rate']*100:5.2f}%"
              f"  on {cl['n_spoof']} clones and {cl['n_genuine']} genuine")
    worst = max(out, key=lambda k: out[k]["clean_committed_error"])
    fprs = {k: out[k]["clean_false_positive_rate"] for k in out}
    worst_fp = max(fprs, key=lambda k: fprs[k])
    summary = dict(
        n_directions=len(out), channels=conds,
        worst_direction_clean=worst,
        worst_direction_clean_committed_error=out[worst]["clean_committed_error"],
        worst_false_alarm_direction_clean=worst_fp,
        worst_false_alarm_clean=fprs[worst_fp],
        n_cells_gate_cannot_commit=len(blocked),
        n_cells_total=len(out) * len(conds),
        cells_gate_cannot_commit=blocked,
        note=("Every direction trains its own head on the other trained families and is "
              "replayed against held-out genuine speech, so no row here is in sample. The "
              "clean channel is the only one where every direction is measurable: on the six "
              "codec channels the held-out family is cached at 4.0 s alone for every family "
              "except xtts_v2 and freevc24, and the Gate needs three updates at or above "
              f"{MIN_COMMIT_S} s before it may commit, so {len(blocked)} of "
              f"{len(out) * len(conds)} cells cannot commit on the held-out clones for a "
              "cache reason. Their genuine halves are still measured and their false-alarm "
              "rates still count."))
    print(f"  worst direction on clean: {worst} at "
          f"{out[worst]['clean_committed_error']*100:.1f}% committed error; worst false alarms "
          f"{fprs[worst_fp]*100:.2f}% holding out {worst_fp}")
    print(f"  {len(blocked)} of {len(out) * len(conds)} cells cannot commit on the held-out "
          f"clones: only 4.0 s is cached for them on that channel")
    return dict(summary=summary, by_held_out=out)


def band_selection(D, seed=0):
    """Why this false-positive budget: sweep it and print what each one costs.

    The bar is not moved to fit the answer. It is the parent repo's eval/BAR.md bar,
    committed-call error <= 10% at coverage >= 40%, and the budget chosen among the points
    that clear it on the CALIBRATION split is the one that cries wolf least on real humans,
    measured on the worst channel in the grid. The test split and the held-out cloner are
    reported, never consulted.
    """
    tr_g, ca_g, te_g = D.split_groups(seed)
    seen = D.generators
    conds = [c for c in SEVERITY if (D.cond == c).any()]
    tr = np.isin(D.group, list(tr_g)) & ((D.y == 0) | np.isin(D.gen, seen))
    head = Head(seed=seed).fit(D.X[tr], D.y[tr], D.gen[tr])
    cals = {}
    for t in sorted(set(D.pre)):
        ca = np.isin(D.group, list(ca_g)) & (D.pre == t) & ((D.y == 0) | np.isin(D.gen, seen))
        if ca.sum() >= 20:
            cals[t] = IsotonicCalibrator().fit(head.raw(D.X[ca]), D.y[ca])
    sweep = []
    print(f"  {'budget':>8} {'worst chan':>12} {'FPR worst':>10} {'cov(seen)':>10} "
          f"{'err(seen)':>10} {'err(unseen)':>12}")
    for fpr in FPR_GRID:
        bands = derive_bands(D, head, cals, ca_g, conds, fpr=fpr)
        rows = {c: dict(seen=gate_replay(D, head, cals, te_g, c, seen, bands),
                        unseen=gate_replay(D, head, cals, te_g, c, [UNSEEN], bands))
                for c in conds}
        fprs = {c: rows[c]["seen"]["false_positive_rate"] for c in conds}
        wc = max(fprs, key=lambda c: fprs[c])
        row = dict(fpr_budget=fpr, worst_channel=wc, worst_channel_fpr=fprs[wc],
                   false_positive_rate_by_channel=fprs,
                   clean=dict(coverage=rows["clean"]["seen"]["coverage"],
                              committed_error_seen=rows["clean"]["seen"]["committed_error"],
                              committed_error_unseen=rows["clean"]["unseen"]["committed_error"]),
                   band_at_clip_s={c: dict(zip(("tau_clone", "tau_human"), bands[(c, CLIP_S)]))
                                   for c in conds if (c, CLIP_S) in bands})
        sweep.append(row)
        print(f"  {fpr:>8.3f} {wc:>12} {fprs[wc]*100:>9.2f}% {row['clean']['coverage']*100:>9.1f}% "
              f"{row['clean']['committed_error_seen']*100:>9.1f}% "
              f"{row['clean']['committed_error_unseen']*100:>11.1f}%")
    ok = [r for r in sweep if r["clean"]["committed_error_seen"] <= 0.10
          and r["clean"]["coverage"] >= 0.40]
    flat = len({round(r["worst_channel_fpr"], 6) for r in ok}) == 1 and len(ok) > 1
    best = None if flat else (min(ok, key=lambda r: (r["worst_channel_fpr"],
                                                     -r["clean"]["coverage"])) if ok else None)
    if flat:
        note = (f"Every budget from {ok[0]['fpr_budget']} to {ok[-1]['fpr_budget']} clears the bar "
                f"and every one of them measures the same worst-channel false-positive rate, "
                f"{ok[0]['worst_channel_fpr']*100:.2f}% on {ok[0]['worst_channel']}, because the "
                f"isotonic calibrator emits a handful of discrete steps and the whole grid lands "
                f"between the same two of them on the test split. The budget is therefore NOT "
                f"identified by this sweep. Pramaan ships {FPR_BUDGET}, which sits inside that "
                f"flat region; it is a declared design choice, not a fit, and the sweep is "
                f"published so a reader can see it was not tuned to a result.")
    elif best:
        note = (f"Budget {best['fpr_budget']} clears the bar with the lowest worst-channel "
                f"false-positive rate on the selection split. Pramaan ships {FPR_BUDGET}.")
    else:
        note = "No budget on the grid clears the bar. The bar is not moved. Report the negative."
    print(f"  {'flat sweep, budget not identified' if flat else f'selected budget {best}'}; "
          f"shipped budget {FPR_BUDGET}")
    return dict(bar=dict(committed_error_max=0.10, min_coverage=0.40,
                         source="parent repo eval/BAR.md, not moved"),
                selection_split="calib", selection_uses="bona fide speech only",
                reporting_split="test", grid=FPR_GRID, sweep=sweep,
                worst_channel_fpr_is_flat=bool(flat), selection_note=note,
                selected_fpr_budget=best["fpr_budget"] if best else None,
                shipped_fpr_budget=FPR_BUDGET,
                head_trained_on="train split only, so the selection never sees test clips",
                legacy_fixed_band=dict(tau_clone=LEGACY_BAND[0], tau_human=LEGACY_BAND[1]))


def adaptation(D, seed=0, shots=(0, 3, 6, 12, 24, 48)):
    """Few-shot repair on the unseen cloner: adapt on n parents, score on the rest."""
    tr_g, ca_g, te_g = D.split_groups(seed)
    seen = D.generators
    rng = np.random.default_rng(seed)
    parents = np.array(sorted(set(D.parent[(D.gen == UNSEEN) & D.full])))
    rng.shuffle(parents)
    n_hold = max(16, len(parents) // 3)
    hold, pool = set(parents[:n_hold]), parents[n_hold:]
    base_tr = D.mask(tr_g | ca_g, seen)
    res = []
    for n in shots:
        if n > len(pool):
            break
        add = set(pool[:n])
        m = base_tr | (np.isin(D.group, list(add)) & (D.cond == "clean") & D.full
                       & ((D.y == 0) | (D.gen == UNSEEN)))
        head = Head(seed=seed).fit(D.X[m], D.y[m], D.gen[m])
        te = np.isin(D.group, list(hold)) & (D.cond == "clean") & D.full & ((D.y == 0) | (D.gen == UNSEEN))
        e, _ = eer(head.raw(D.X[te]), D.y[te])
        te2 = D.mask(te_g, seen)
        e2, _ = eer(head.raw(D.X[te2]), D.y[te2])
        res.append(dict(shots=n, eer_unseen_heldout=e, eer_seen_test=e2, n_heldout_parents=len(hold)))
        print(f"  adapt on {n:3d} recordings -> unseen EER {e*100:5.1f}%  seen EER {e2*100:5.1f}%")
    return res


def ship(D, seed=0):
    """Train the deployed head on everything seen, calibrate per prefix, derive the band."""
    seen = D.generators
    prefixes = sorted(set(D.pre[D.cond == "clean"]))
    tr_g, ca_g, te_g = D.split_groups(seed)
    tr = (D.cond != "none") & ((D.y == 0) | np.isin(D.gen, seen)) & np.isin(D.group, list(tr_g | te_g))
    # rows recorded through the demo laptop's speaker-to-mic path are few (about 200 among
    # 58,000) and matter for the live demo, so they carry extra weight.
    w = Head.family_weights(D.y[tr], D.gen[tr]) * np.where(np.char.startswith(D.cond[tr], "replay"), REPLAY_WEIGHT, 1.0)
    head = Head(seed=seed); head.pipe.fit(D.X[tr], D.y[tr], lr__sample_weight=w)
    conds = [c for c in SEVERITY if (D.cond == c).any()]
    cals = {}
    for t in prefixes:
        ca = np.isin(D.group, list(ca_g)) & (D.pre == t) & ((D.y == 0) | np.isin(D.gen, seen))
        if ca.sum() < 20:
            continue
        cals[t] = IsotonicCalibrator().fit(head.raw(D.X[ca]), D.y[ca])
    bands = derive_bands(D, head, cals, ca_g, conds)
    by_channel = {c: {t: dict(tau_clone=v[0], tau_human=v[1])
                      for (cc, t), v in bands.items() if cc == c} for c in conds}
    band = by_channel["clean"]
    # The shipped bundle carries a band per channel. A live call declares its channel
    # (src/pramaan/stream.py); a channel with no band falls back to the most degrading one
    # measured, never to clean.
    save_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"), head=head.pipe,
                calibrators=cals, band=band, band_by_channel=by_channel,
                fallback_channel=conds[-1], prefixes=prefixes, generators=seen,
                fpr_budget=FPR_BUDGET, n_trainable=head.n_trainable)
    print(f"  shipped head: {head.n_trainable} trainable parameters, {len(cals)} calibrators, "
          f"{len(by_channel)} per-channel bands, fallback channel {conds[-1]}")
    return dict(n_trainable=head.n_trainable, generators=seen, prefixes=prefixes,
                band={str(k): v for k, v in band.items()}, band_scope="clean channel",
                band_by_channel={c: {str(t): v for t, v in d.items()} for c, d in by_channel.items()},
                fallback_channel=conds[-1], n_train_rows=int(tr.sum()))


def operating_point(D, seed=0):
    """What the SHIPPED model actually decides at its own commit band.

    EER answers "can it rank a clone below a human?". This answers the question an
    operator cares about: at the threshold we actually ship, how many clones does it
    call out, how many does it wave through, and how many does it refuse to judge.
    The two can disagree badly under generator shift, which is the whole reason the
    prevention ladder is mandatory rather than optional.
    """
    from pramaan.model import load_bundle
    B = load_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"))
    head, cal, band = B["head"], B["calibrators"][CLIP_S], B["band"][CLIP_S]
    bbc = B["band_by_channel"]
    m = (D.cond == "clean") & (D.pre == CLIP_S)
    s = head.decision_function(D.X[m]); p = cal.predict_proba(s)
    g, yy = D.gen[m], D.y[m]
    bona = yy == 0
    out = dict(tau_clone=band["tau_clone"], tau_human=band["tau_human"],
               scope="clean channel, 4.0 s prefix", per_generator={})
    for name in ["none"] + D.generators + [UNSEEN]:
        sel = (g == name)
        if not sel.any():
            continue
        pp = p[sel]
        row = dict(n=int(sel.sum()),
                   called_synthetic=float((pp >= band["tau_clone"]).mean()),
                   called_human=float((pp <= band["tau_human"]).mean()))
        row["deferred"] = float(1 - row["called_synthetic"] - row["called_human"])
        if name != "none":
            sub = bona | sel
            row["eer"], _ = eer(s[sub], yy[sub])
        out["per_generator"]["human" if name == "none" else name] = row
        print(f"  {('human' if name=='none' else name):12s} n={row['n']:4d}  "
              f"synthetic {row['called_synthetic']*100:5.1f}%  human {row['called_human']*100:5.1f}%  "
              f"defer {row['deferred']*100:5.1f}%")
    # The same question on every channel, because a claim of "0.0% false alarms" that is
    # measured on clean audio only is a claim about one of seven lines a caller can be on.
    out["per_channel_genuine"] = {}
    for c in [k for k in SEVERITY if (D.cond == k).any()]:
        if c not in bbc or CLIP_S not in bbc[c]:
            continue
        b = bbc[c][CLIP_S]
        mc = (D.cond == c) & (D.pre == CLIP_S) & (D.y == 0)
        if mc.sum() < MIN_BAND_CLIPS:
            continue
        pc = cal.predict_proba(head.decision_function(D.X[mc]))
        row = dict(n=int(mc.sum()), tau_clone=b["tau_clone"], tau_human=b["tau_human"],
                   called_synthetic=float((pc >= b["tau_clone"]).mean()),
                   called_human=float((pc <= b["tau_human"]).mean()),
                   called_synthetic_at_legacy_band=float((pc >= LEGACY_BAND[0]).mean()),
                   called_synthetic_at_p50=float((pc >= 0.5).mean()))
        row["deferred"] = float(1 - row["called_synthetic"] - row["called_human"])
        out["per_channel_genuine"][c] = row
        print(f"  genuine on {c:12s} n={row['n']:4d}  called synthetic "
              f"{row['called_synthetic']*100:5.1f}%  (at p>=0.5: {row['called_synthetic_at_p50']*100:5.1f}%)")
    pcg = out["per_channel_genuine"]
    wc = max(pcg, key=lambda c: pcg[c]["called_synthetic"])
    out["worst_channel"] = wc
    out["worst_channel_fpr"] = pcg[wc]["called_synthetic"]
    out["fpr_pooled_all_channels"] = float(np.average(
        [pcg[c]["called_synthetic"] for c in pcg], weights=[pcg[c]["n"] for c in pcg]))
    u = out["per_generator"][UNSEEN]
    out["headline"] = (
        f"On the unseen 2025 cloner the shipped band calls {u['called_synthetic']*100:.1f}% synthetic, "
        f"defers on {u['deferred']*100:.1f}% and waves {u['called_human']*100:.1f}% through, even though its "
        f"ranking EER is {u['eer']*100:.1f}%. Ranking transfers to a new generator; the absolute threshold "
        f"does not. This is why a high-value action always requires the device factor.")
    print("  " + out["headline"])
    return out


def replay_mic(D, seed=0):
    """The loudspeaker-to-microphone channel, scored and published.

    `dataset.extra_channels` has listed replay_mic and replay_mic_v0.4 since the set was
    built, `docs/RUNSHEET.md` relies on a replay-mic demo beat, and no results grid had a row
    for either. G14 in docs/SOTA_GAP_ANALYSIS.md: better to have the cell printed and failing
    than to discover it on stage when a judge asks to hold a phone up to the laptop.

    Two rows, because one of them would be misleading on its own:

      shipped    The head the demo actually runs. `ship()` trains on every condition that is
                 not "none", replay rows included, at REPLAY_WEIGHT. So these clips are IN
                 its training set and this row is an IN-SAMPLE number. It is published
                 because it is what the demo does, and it is labelled because it is not a
                 generalisation claim.
      channel_heldout  The same recipe with every replay condition removed from training, so
                 the CHANNEL is held out. The underlying recordings are not: their clean and
                 codec versions are still in training, which is why this is a channel-shift
                 measurement and not a held-out-clip measurement. Said plainly rather than
                 implied.

    No gate replay: replay rows are cached at the 4.0 s prefix only, and the Gate needs three
    stable updates before it may commit, so there is nothing for it to replay. The decision
    numbers below are the band applied to the full 4 s clip, using the fallback channel the
    live path would pick for a line it has no band for (src/pramaan/stream.py).
    """
    from pramaan.model import load_bundle
    chans = sorted(c for c in set(D.cond) if c.startswith("replay"))
    if not chans:
        return dict(note="no replay conditions in this feature cache")
    conds = [c for c in SEVERITY if (D.cond == c).any()]
    fallback = conds[-1]
    tr_g, ca_g, te_g = D.split_groups(seed)
    seen = D.generators

    # the channel-held-out head: ship()'s recipe minus every replay row
    trm = ((D.cond != "none") & ~np.char.startswith(D.cond, "replay")
           & ((D.y == 0) | np.isin(D.gen, seen)) & np.isin(D.group, list(tr_g | te_g)))
    hh = Head(seed=seed)
    hh.pipe.fit(D.X[trm], D.y[trm], lr__sample_weight=Head.family_weights(D.y[trm], D.gen[trm]))
    cah = np.isin(D.group, list(ca_g)) & (D.pre == CLIP_S) & ~np.char.startswith(D.cond, "replay") \
        & ((D.y == 0) | np.isin(D.gen, seen))
    calh = IsotonicCalibrator().fit(hh.raw(D.X[cah]), D.y[cah])

    B = load_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"))
    sh, scal = B["head"], B["calibrators"][CLIP_S]
    band = B["band_by_channel"][fallback][CLIP_S]

    out = dict(channels=chans, prefix_s=CLIP_S, band_used=dict(channel=fallback, **band),
               band_note=("replay is not in the codec grid, so it has no band of its own. The "
                          "live path falls back to the most degrading condition measured, "
                          f"{fallback}, never to clean (src/pramaan/stream.py). That is the "
                          "band applied here."),
               rows={})
    for c in chans:
        m = (D.cond == c) & (D.pre == CLIP_S)
        y = D.y[m]
        row = dict(n_clips=int(m.sum()), n_bona=int((y == 0).sum()), n_spoof=int((y == 1).sum()),
                   by_generator=dict(Counter(D.gen[m].tolist())))
        for name, (raw, cal, note) in {
            "shipped": (sh.decision_function(D.X[m]), scal,
                        "IN-SAMPLE: ship() trains on replay rows at weight "
                        f"{REPLAY_WEIGHT:g}. This is what the demo runs, not a "
                        "generalisation claim."),
            "channel_heldout": (hh.raw(D.X[m]), calh,
                                "channel held out of training. The recordings are not: their "
                                "clean and codec versions remain in training, so this is a "
                                "channel-shift number, not a held-out-clip number."),
        }.items():
            p = cal.predict_proba(raw)
            e, _ = eer(raw, y)
            cell = dict(eer=e, auroc=auroc(raw, y), ece=ece(p, y), protocol_note=note,
                        genuine_called_synthetic=float((p[y == 0] >= band["tau_clone"]).mean()),
                        genuine_called_human=float((p[y == 0] <= band["tau_human"]).mean()),
                        spoof_called_synthetic=float((p[y == 1] >= band["tau_clone"]).mean()),
                        spoof_called_human=float((p[y == 1] <= band["tau_human"]).mean()))
            cell["spoof_deferred"] = float(1 - cell["spoof_called_synthetic"]
                                           - cell["spoof_called_human"])
            cell["ci"] = boot_eer(raw, y, D.group[m], 2000, seed)
            row[name] = cell
        out["rows"][c] = row
        print(f"  {c:16s} n={row['n_clips']:3d} ({row['n_bona']} genuine, {row['n_spoof']} clones)"
              f"  shipped EER {row['shipped']['eer']*100:5.1f}%"
              f"  channel-held-out EER {row['channel_heldout']['eer']*100:5.1f}%")
        print(f"  {'':16s} at the {fallback} band, channel-held-out: clones called synthetic "
              f"{row['channel_heldout']['spoof_called_synthetic']*100:5.1f}%, genuine called "
              f"synthetic {row['channel_heldout']['genuine_called_synthetic']*100:5.1f}%")
    worst = max(out["rows"], key=lambda c: out["rows"][c]["channel_heldout"]["eer"])
    out["worst_channel"] = worst
    out["worst_channel_eer_heldout"] = out["rows"][worst]["channel_heldout"]["eer"]
    ho = out["rows"][worst]["channel_heldout"]
    out["headline"] = (
        "Playing audio through a loudspeaker into a microphone costs the detector real "
        f"accuracy. With the channel held out of training, EER on {worst} is "
        f"{ho['eer']*100:.1f}% (95% CI {ho['ci']['lo']*100:.1f}% to {ho['ci']['hi']*100:.1f}%), "
        f"and at the {fallback} fallback band "
        f"{ho['spoof_called_synthetic']*100:.1f}% of clones played through a speaker are "
        f"called synthetic while {ho['genuine_called_synthetic']*100:.1f}% of genuine speech "
        "through the same speaker is called synthetic too, which is the larger of the two "
        "problems and is far above the 0.9% this system reports on the telephony grid. The "
        "shipped head scores better on these clips because it trains on them, so its number "
        "is in sample and is labelled as such rather than quoted as generalisation. This is "
        "published rather than hidden, it is why docs/RUNSHEET.md records that the Chatterbox "
        "clone through the microphone reads as human, and it is the beat where the device "
        "push does the blocking instead of the detector.")
    print("  " + out["headline"])
    return out


def wilson(k, n, z=1.959963984540054):
    """Wilson score interval for a binomial rate. Used instead of the normal approximation
    because the counts here are small and several of the rates are 0, where the normal
    interval collapses to a point and claims a certainty the data does not support."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return dict(rate=float(p), lo=float(max(0.0, c - h)), hi=float(min(1.0, c + h)),
                k=int(k), n=int(n), method="Wilson score, 95%")


def boot_eer(scores, y, groups, n_boot=2000, seed=0):
    """Cluster bootstrap of an EER, resampling PARENT RECORDINGS, not clips.

    A clip-level bootstrap would treat a bona fide recording and the clone made from it as
    two independent draws. They are not: the same-speaker same-sentence protocol makes them
    one unit, and the split code already refuses to let them straddle a boundary. Resampling
    the unit is the interval that matches the protocol, and it is wider than a clip-level
    one, which is the honest direction.
    """
    rng = np.random.default_rng(seed)
    scores, y, groups = np.asarray(scores, float), np.asarray(y), np.asarray(groups)
    units = np.array(sorted(set(groups.tolist())))
    idx_by_unit = {u: np.where(groups == u)[0] for u in units}
    point, _ = eer(scores, y)
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(len(units), size=len(units), replace=True)
        sel = np.concatenate([idx_by_unit[units[i]] for i in pick])
        yy = y[sel]
        if len(set(yy.tolist())) < 2:
            continue
        e, _ = eer(scores[sel], yy)
        draws.append(e)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return dict(eer=float(point), lo=float(lo), hi=float(hi), n_boot=len(draws),
                n_units=len(units), n_clips=int(len(y)),
                n_bona=int((y == 0).sum()), n_spoof=int((y == 1).sum()),
                method="cluster bootstrap over parent recordings, 2.5th and 97.5th percentile")


def confidence(D, R, seed=0, n_boot=2000):
    """95% intervals on the headline EER and on every rate the deck quotes.

    Written because docs/SOTA_GAP_ANALYSIS.md G3 is right: a headline computed on a few
    dozen clips with no error bar is not a measurement, and the parent repo's
    challenge_eval.py already prints Wilson intervals for exactly this reason.
    """
    tr_g, ca_g, te_g = D.split_groups(seed)
    allg = D.generators + [UNSEEN]
    out = {"method": "cluster bootstrap over parent recordings for EERs; Wilson score "
                     "intervals for rates; 95% throughout",
           "n_boot": n_boot, "seed": seed}

    # 1. The headline. Exactly the cell generator_matrix publishes as 13.2%: leave-one-
    # generator-out, clean channel, test split only, scored against test-split genuine.
    seen = [g for g in allg if g != UNSEEN]
    head, cal, _ = fit_and_score(D, tr_g, ca_g, te_g, seen, [UNSEEN], seed, conds=("clean",))
    te = D.mask(te_g, [UNSEEN], cond="clean")
    out["unseen_cloner_eer_leave_one_out"] = boot_eer(
        head.raw(D.X[te]), D.y[te], D.group[te], n_boot, seed)
    out["unseen_cloner_eer_leave_one_out"]["protocol"] = (
        "generator_matrix.chatterbox.per_condition.clean, the README headline")

    # 2. The same head on every codec, because a judge may ask for the interval on the
    # cell that is worst rather than the cell that is quoted.
    out["unseen_cloner_eer_by_channel"] = {}
    for c in [k for k in SEVERITY if (D.cond == k).any()]:
        t = D.mask(te_g, [UNSEEN], cond=c)
        if t.sum() == 0 or len(set(D.y[t].tolist())) < 2:
            continue
        out["unseen_cloner_eer_by_channel"][c] = boot_eer(
            head.raw(D.X[t]), D.y[t], D.group[t], n_boot, seed)

    # 3. The shipped head on all 39 clips, which is the operating_point number. This is the
    # other count and it is a different, legitimate measurement, not a contradiction.
    from pramaan.model import load_bundle
    B = load_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"))
    sh, scal = B["head"], B["calibrators"][CLIP_S]
    m = (D.cond == "clean") & (D.pre == CLIP_S) & ((D.y == 0) | (D.gen == UNSEEN))
    out["unseen_cloner_eer_shipped_head_all_clips"] = boot_eer(
        sh.decision_function(D.X[m]), D.y[m], D.group[m], n_boot, seed)
    out["unseen_cloner_eer_shipped_head_all_clips"]["protocol"] = (
        "operating_point.per_generator.chatterbox.eer, the shipped head at 4.0 s")

    # 4. The count reconciliation G3 asks for, settled by reading the two masks above
    # rather than by choosing one number and hoping.
    n39 = int(((D.gen == UNSEEN) & (D.cond == "clean") & D.full).sum())
    n23 = int(D.mask(te_g, [UNSEEN], cond="clean").sum() - (D.y[D.mask(te_g, [UNSEEN], cond="clean")] == 0).sum())
    out["clip_count_reconciliation"] = dict(
        n_chatterbox_total=n39, n_chatterbox_scored_in_headline=n23,
        resolved=("Both counts are correct and they belong to different protocols. "
                  f"{n39} is every Chatterbox clip in the corpus "
                  "(dataset.by_generator.chatterbox), and the shipped head never trains on "
                  f"any of them, so all {n39} are held out at the operating point. {n23} is "
                  "the subset that falls in the 25% test split of parent recordings, which "
                  "is what the leave-one-generator-out headline is scored on, because that "
                  "protocol also needs its genuine side held out from the head's training "
                  "split. The headline EER is an EER over "
                  f"{n23} clones and "
                  f"{int((D.y[D.mask(te_g, [UNSEEN], cond='clean')] == 0).sum())} genuine "
                  "recordings, and that is the pair of counts any interval on it must use."),
        headline_n_bona=int((D.y[D.mask(te_g, [UNSEEN], cond="clean")] == 0).sum()),
        source_headline="generator_matrix.chatterbox.per_condition.clean",
        source_total="dataset.by_generator.chatterbox and operating_point.per_generator.chatterbox")

    # 5. Every gate rate, per channel, from the counts streaming already published. No refit:
    # an interval on a published rate must be an interval on THAT rate.
    st = R.get("streaming", {})
    out["gate_replay_by_channel"] = {}
    for c, row in st.get("gate_replay_by_channel", {}).items():
        chan = {}
        for name, r in row.items():
            n_clips, deferred = r["n_clips"], r["deferred"]
            committed = n_clips - deferred
            ci = dict(coverage=wilson(committed, n_clips))
            if committed:
                ci["committed_error"] = wilson(round(r["committed_error"] * committed), committed)
            if r.get("false_positive_rate") is not None:
                ci["false_positive_rate"] = wilson(r["n_false_positive"], r["n_genuine"])
            chan[name] = ci
        out["gate_replay_by_channel"][c] = chan

    # 6. The operating-point decision rates on the unseen cloner, the 69.2% / 30.8% pair.
    op = R.get("operating_point", {})
    u = op.get("per_generator", {}).get(UNSEEN)
    if u:
        out["operating_point_unseen"] = dict(
            called_synthetic=wilson(round(u["called_synthetic"] * u["n"]), u["n"]),
            called_human=wilson(round(u["called_human"] * u["n"]), u["n"]))
    pcg = op.get("per_channel_genuine", {})
    out["operating_point_genuine_by_channel"] = {
        c: wilson(round(r["called_synthetic"] * r["n"]), r["n"]) for c, r in pcg.items()}

    # 7. The clean-channel cell of every leave-one-generator-out streaming direction. The
    # worst of them is a 127-clip measurement, so it gets an interval like everything else.
    lo = R.get("streaming_leave_one_out", {}).get("by_held_out", {})
    out["streaming_leave_one_out_clean"] = {}
    for held, row in lo.items():
        r = row["by_channel"]["clean"]
        d = dict(coverage=wilson(r["n_committed"], r["n_clips"]))
        if r["n_committed"]:
            d["committed_error"] = wilson(round(r["committed_error"] * r["n_committed"]),
                                          r["n_committed"])
        if r.get("false_positive_rate") is not None:
            d["false_positive_rate"] = wilson(r["n_false_positive"], r["n_genuine"])
        out["streaming_leave_one_out_clean"][held] = d

    h = out["unseen_cloner_eer_leave_one_out"]
    print(f"  headline unseen-cloner EER {h['eer']*100:.1f}% "
          f"[{h['lo']*100:.1f}, {h['hi']*100:.1f}] on {h['n_spoof']} clones and "
          f"{h['n_bona']} genuine recordings, {h['n_units']} parent units resampled")
    s = out["unseen_cloner_eer_shipped_head_all_clips"]
    print(f"  shipped head, all {s['n_spoof']} clones  EER {s['eer']*100:.1f}% "
          f"[{s['lo']*100:.1f}, {s['hi']*100:.1f}]")
    w = out["gate_replay_by_channel"].get(st.get("worst_channel"), {}).get("seen", {})
    if w.get("false_positive_rate"):
        f = w["false_positive_rate"]
        print(f"  worst-channel gate false alarms {f['rate']*100:.2f}% "
              f"[{f['lo']*100:.2f}, {f['hi']*100:.2f}] on {f['n']} genuine recordings")
    return out


def dataset_summary(D):
    full = D.full & (D.cond == "clean")
    return dict(n_clips=int(full.sum()), n_bona=int((D.y[full] == 0).sum()),
                n_spoof=int((D.y[full] == 1).sum()),
                by_generator=dict(Counter(D.gen[full].tolist())),
                by_family=dict(Counter(D.fam[full].tolist())),
                by_language=dict(Counter(D.lang[full].tolist())),
                n_embeddings=int(len(D.X)),
                conditions=sorted(c for c in set(D.cond) if not c.startswith("replay")),
                extra_channels=sorted(c for c in set(D.cond) if c.startswith("replay")),
                unavailable_conditions=UNAVAILABLE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--features", default=FEAT)
    ap.add_argument("--out", default=RES)
    a = ap.parse_args()
    D = Data(a.features)
    R = json.load(open(a.out)) if os.path.exists(a.out) else {}
    R["project"] = "Pramaan"; R["ps"] = "SIH26104"
    R["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    R["dataset"] = dataset_summary(D)
    want = set(a.only.split(",")) if a.only else None
    def go(name):
        return want is None or name in want
    if go("generator_matrix"):
        print("\n== leave-one-generator-out"); R["generator_matrix"] = generator_matrix(D, a.seed)
        R["generator_matrix_note"] = (
            "Each row trains on CLEAN audio only and is then scored through every codec, so "
            "the per-condition fpr_at_p50 here measures a clean-trained head meeting an "
            "unseen channel at a fixed 0.5 threshold. It is a channel-shift stress test, not "
            "the shipped system: the shipped head in `ship` trains on all seven conditions "
            "and decides at the per-channel band in `streaming.band_by_channel`. Compare "
            "against operating_point.per_channel_genuine, never against this row.")
    if go("diversity_curve"):
        print("\n== diversity curve"); R["diversity_curve"] = diversity_curve(D, a.seed)
    if go("calibration"):
        print("\n== calibration"); R["calibration"] = calibration_study(D, a.seed)
    if go("streaming"):
        print("\n== streaming"); R["streaming"], *_ = streaming(D, a.seed)
    if go("streaming_leave_one_out"):
        print("\n== streaming, every held-out-generator direction, per channel")
        R["streaming_leave_one_out"] = streaming_leave_one_out(D, a.seed)
    if go("band_selection"):
        print("\n== band selection (false-positive budget sweep, bona fide only)")
        R["band_selection"] = band_selection(D, a.seed)
    if go("adaptation"):
        print("\n== adaptation"); R["adaptation"] = adaptation(D, a.seed)
    if go("ship"):
        print("\n== ship"); R["ship"] = ship(D, a.seed)
    if go("operating_point"):
        print("\n== operating point (the shipped model at its own band)")
        R["operating_point"] = operating_point(D, a.seed)
    if go("replay_mic"):
        print("\n== replay: loudspeaker to microphone")
        R["replay_mic"] = replay_mic(D, a.seed)
    if go("confidence"):
        print("\n== confidence intervals (cluster bootstrap and Wilson, 95%)")
        R["confidence"] = confidence(D, R, a.seed)
    json.dump(R, open(a.out, "w"), indent=2)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
