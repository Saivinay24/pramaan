#!/usr/bin/env python3
"""Fill every {{placeholder}} in docs/templates/*.md from results.json and latency.json.

One source of truth for every number a human says on stage. Fails loudly on an unknown
placeholder so a stale token can never reach a rehearsal.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, "eval", "results.json")))
LAT = json.load(open(os.path.join(ROOT, "eval", "results", "latency.json")))
UNSEEN_GEN = "chatterbox"
GEN_LABEL = {"xtts_v2": "XTTS-v2", "freevc24": "FreeVC voice conversion", "encodec": "EnCodec resynthesis",
             "mac_say": "Apple on-device TTS", "mms_vits": "Meta MMS", "kokoro": "Kokoro-82M",
             "espeak_ng": "eSpeak NG formant synthesis", "piper": "Piper", "chatterbox": "Chatterbox"}
CHAN_LABEL = {"clean": "clean", "opus_24k": "Opus 24 kbps", "opus_8k": "Opus 8 kbps",
              "g722_64k": "G.722 64 kbps", "g726_32k": "G.726 32 kbps",
              "g723_1_6k3": "G.723.1 6.3 kbps", "speex_wb_q4": "Speex WB"}


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def span(d, dec=1):
    """The low and high ends of a 95% interval, as text. Used everywhere an interval is
    printed, so a point estimate never reaches a doc without its error bar beside it."""
    return f"{pct(d['lo'], dec)} to {pct(d['hi'], dec)}"


gm = R["generator_matrix"]; seen = [g for g in gm if g != "chatterbox"]
best = min(seen, key=lambda g: gm[g]["clean_eer"]); worst = max(seen, key=lambda g: gm[g]["clean_eer"])
dc = R["diversity_curve"]["curve"]; ad = R["adaptation"]; cal = R["calibration"]["unseen_cloner"]
st = R["streaming"]; g_seen = st["gate_replay"]["seen"]; g_unseen = st["gate_replay"]["unseen"]
cpu4 = [r for r in LAT["rows"] if r["device"] == "cpu" and r["window_s"] == 4.0][0]
mps4 = [r for r in LAT["rows"] if r["device"] == "mps" and r["window_s"] == 4.0][0]
cap = LAT["capacity"]["cpu_hop_1.0"]
unseen_clean = gm["chatterbox"]["clean_eer"]
pair_caught = unseen_clean < 0.15

V = {
    "n_seen": str(len(seen)), "n_gen_total": str(len(gm)), "n_clips": str(R["dataset"]["n_clips"]), "n_bona": str(R["dataset"]["n_bona"]),
    "n_spoof": str(R["dataset"]["n_spoof"]), "n_embeddings": f"{R['dataset']['n_embeddings']:,}",
    "n_conditions": str(len([c for c in R["dataset"]["conditions"] if not c.startswith("replay")])),
    "div_k1": pct(dc[0]["eer_mean"]), "div_kN": pct(dc[-1]["eer_mean"]), "div_kN_min": pct(dc[-1]["eer_min"]),
    "div_k1_min": pct(dc[0]["eer_min"]), "div_k1_max": pct(dc[0]["eer_max"]),
    "div_worst_small": pct(max(p["eer_max"] for p in dc[:-1])), "cal_iso_seen": f"{R['calibration']['seen_generators']['isotonic']['ece']:.2f}",
    "legacy_unseen": "35.9%",
    "unseen_clean_eer": pct(unseen_clean), "unseen_auroc": f"{gm['chatterbox']['per_condition']['clean']['auroc']:.2f}",
    "n_unseen_clones": str(gm["chatterbox"]["per_condition"]["clean"]["n_spoof"]),
    "gm_best": GEN_LABEL[best], "gm_best_eer": pct(gm[best]["clean_eer"]),
    "gm_worst": GEN_LABEL[worst], "gm_worst_eer": pct(gm[worst]["clean_eer"]),
    "ad_shots0": str(ad[1]["shots"]) if len(ad) > 1 else "0", "ad_eer0": pct(ad[1]["eer_unseen_heldout"]) if len(ad) > 1 else "",
    "ad_shotsN": str(ad[-1]["shots"]), "ad_eerN": pct(ad[-1]["eer_unseen_heldout"]),
    "ad_base": pct(ad[0]["eer_unseen_heldout"]),
    "cal_raw": f"{cal['raw_sigmoid']['ece']:.2f}", "cal_iso": f"{cal['isotonic']['ece']:.2f}", "cal_platt": f"{cal['platt']['ece']:.2f}",
    "min_commit": str(st["min_commit_s"]), "fpr_seen": pct(g_seen["false_positive_rate"]),
    "ttd_seen": str(g_seen["median_time_to_decision_s"]), "cov_seen": pct(g_seen["coverage"]),
    "err_seen": pct(g_seen["committed_error"]), "cov_unseen": pct(g_unseen["coverage"]),
    "err_unseen": pct(g_unseen["committed_error"]),
    "lat_cpu4": f"{cpu4['median_ms']:.0f}", "rtf_cpu4": f"{cpu4['rtf']:.3f}",
    "lat_mps4": f"{mps4['median_ms']:.0f}", "rtf_mps4": f"{mps4['rtf']:.3f}",
    "cap_streams": f"{cap['streams_per_core']:.1f}", "cap_cores": str(cap["cores_for_200_seats"]),
    "n_trainable": f"{R['ship']['n_trainable']:,}",
    "op_catch_unseen": pct(R["operating_point"]["per_generator"]["chatterbox"]["called_synthetic"]),
    "op_miss_unseen": pct(R["operating_point"]["per_generator"]["chatterbox"]["called_human"]),
    "op_defer_unseen": pct(R["operating_point"]["per_generator"]["chatterbox"]["deferred"]),
    "op_catch_seen": pct(min(v["called_synthetic"] for k, v in R["operating_point"]["per_generator"].items() if k not in ("human", "chatterbox"))),
    "op_fpr": pct(R["operating_point"]["per_generator"]["human"]["called_synthetic"]),
    "demo_decide_s": str(st["min_commit_s"]),
}
# Every false-alarm number carries the channel it was measured on. A rate measured on clean
# audio is a claim about one of the seven lines a caller can be on, and saying it unscoped
# is what G1 in docs/SOTA_GAP_ANALYSIS.md was about.
op = R["operating_point"]; pcg = op["per_channel_genuine"]
gfpr = st["false_positive_rate_by_channel"]
g_worst = st["worst_channel"]
V.update({
    "fpr_clean": pct(gfpr["clean"], 2), "fpr_worst": pct(st["worst_channel_fpr"], 2),
    "fpr_worst_chan": CHAN_LABEL[g_worst],
    "op_fpr_clean": pct(pcg["clean"]["called_synthetic"]),
    "op_fpr_worst": pct(op["worst_channel_fpr"]),
    "op_fpr_worst_chan": CHAN_LABEL[op["worst_channel"]],
    "op_fpr_allchan": pct(op["fpr_pooled_all_channels"]),
    "n_channels_scored": str(len(pcg)),
    "n_bona_allchan": f"{sum(r['n'] for r in pcg.values()):,}",
    "band_clean": f"[{op['tau_human']:.3f}, {op['tau_clone']:.3f}]",
    # The band we quote publicly must be the one the shipped bundle actually uses, because the
    # console prints it on screen during the demo. streaming.band_by_channel is the eval-time
    # band and differs; quoting it made the script contradict the screen.
    "band_worst": "[{:.3f}, {:.3f}]".format(
        R["ship"]["band_by_channel"]["g723_1_6k3"][str(4.0)]["tau_human"],
        R["ship"]["band_by_channel"]["g723_1_6k3"][str(4.0)]["tau_clone"]),
    "fpr_budget": f"{st['fpr_budget']:.0%}",
})
V.update({f"fpr_{c}": pct(v, 2) for c, v in gfpr.items()})
V.update({f"op_fpr_{c}": pct(r["called_synthetic"]) for c, r in pcg.items()})
V.update({f"cov_{c}": pct(st["gate_replay_by_channel"][c]["seen"]["coverage"]) for c in gfpr})
V.update({f"err_{c}": pct(st["gate_replay_by_channel"][c]["seen"]["committed_error"]) for c in gfpr})
bg = R["dataset"]["by_generator"]
V.update({f"n_{g}": f"{n:,}" for g, n in bg.items()})
V["n_ai_train"] = f"{sum(n for g, n in bg.items() if g not in ('none', UNSEEN_GEN)):,}"
V["n_ai_heldout"] = f"{bg.get(UNSEEN_GEN, 0):,}"
V["n_hindi"] = f"{R['dataset']['by_language']['hindi']:,}"
V["n_tamil"] = f"{R['dataset']['by_language']['tamil']:,}"
V["n_telugu"] = f"{R['dataset']['by_language']['telugu']:,}"
V["audio_minutes"] = f"{R['dataset']['n_clips'] * 4 / 60:.0f}"
V["n_defer_seen"] = str(st["gate_replay"]["seen"]["deferred"])
V["n_clips_seen_test"] = str(st["gate_replay"]["seen"]["n_clips"])
V.update({f"gm_{g}": pct(gm[g]["clean_eer"]) for g in gm})
# Generated row by row for the same reason div_table_rows is: the hand-typed six-row version
# of this table silently dropped espeak_ng and piper when they were added on 2026-09-14.
V["gm_table_rows"] = "\n".join(
    ("| **{g} 2025, same speaker and sentence** | **{e}** (95% CI {ci}) |" if g == UNSEEN_GEN
     else "| {g} | {e} |").format(
        g=GEN_LABEL[g], e=pct(gm[g]["clean_eer"]),
        ci=span(R["confidence"]["unseen_cloner_eer_leave_one_out"]))
    for g in list(seen) + [UNSEEN_GEN])
V.update({f"gm_{g}_{c}": pct(v["eer"]) for g in gm for c, v in gm[g]["per_condition"].items()})
V.update({f"div_k{p['k']}": pct(p["eer_mean"]) for p in dc})
# The diversity curve's mean does NOT fall with k. What falls is the spread. G12 in
# docs/SOTA_GAP_ANALYSIS.md: any wording stronger than variance reduction is a claim the
# curve does not support, so the min and max per k are exported and the docs quote them.
V.update({f"div_k{p['k']}_min": pct(p["eer_min"]) for p in dc})
V.update({f"div_k{p['k']}_max": pct(p["eer_max"]) for p in dc})
V.update({f"div_k{p['k']}_span": f"{pct(p['eer_max'] - p['eer_min'])} wide" for p in dc})
V["div_kN_max"] = pct(dc[-1]["eer_max"])
V["div_kN_span"] = f"{pct(dc[-1]['eer_max'] - dc[-1]['eer_min'])} wide"
V["n_div_subsets"] = str(dc[-1]["n_subsets"])
# The curve grows a row every time a generator family is added, so the table and the mean
# sequence are generated rather than typed. A hand-typed k=1..6 table silently drops the new
# rows, which is exactly the drift docs/RUBRIC_ATTACK.md's numbers sweep exists to stop.
V["div_table_rows"] = "\n".join(
    ("| **{k}** | **{m}** | {lo} | {hi} | **{sp}** |" if p is dc[-1] else
     "| {k} | {m} | {lo} | {hi} | {sp} |").format(
        k=p["k"], m=pct(p["eer_mean"]), lo=pct(p["eer_min"]), hi=pct(p["eer_max"]),
        sp=f"{pct(p['eer_max'] - p['eer_min'])} wide")
    for p in dc)
V["div_mean_seq"] = ", ".join(pct(p["eer_mean"]) for p in dc)

# 95% intervals. G3 in docs/SOTA_GAP_ANALYSIS.md: a headline computed on a few dozen clips
# with no error bar is not a measurement. Every point estimate below ships with the interval
# next to it so "what is the error bar on that?" has a printed answer instead of a pause.
ci = R["confidence"]
h = ci["unseen_cloner_eer_leave_one_out"]
sh = ci["unseen_cloner_eer_shipped_head_all_clips"]
rec = ci["clip_count_reconciliation"]
gw = ci["gate_replay_by_channel"][st["worst_channel"]]["seen"]["false_positive_rate"]
ou = ci["operating_point_unseen"]
V.update({
    "ci_unseen_eer": span(h), "ci_unseen_lo": pct(h["lo"]), "ci_unseen_hi": pct(h["hi"]),
    "unseen_eer_ci": f"{pct(h['eer'])} (95% CI {span(h)})",
    "ci_shipped_unseen_eer": span(sh),
    "shipped_unseen_eer_ci": f"{pct(sh['eer'])} (95% CI {span(sh)})",
    "n_unseen_bona": str(rec["headline_n_bona"]),
    "n_unseen_total": str(rec["n_chatterbox_total"]),
    "ci_fpr_worst": span(gw, 2),
    "fpr_worst_ci": f"{pct(gw['rate'], 2)} (95% CI {span(gw, 2)})",
    "ci_op_catch_unseen": span(ou["called_synthetic"]),
    "op_catch_unseen_ci": f"{pct(ou['called_synthetic']['rate'])} (95% CI {span(ou['called_synthetic'])})",
    "ci_op_miss_unseen": span(ou["called_human"]),
})
V.update({f"ci_gm_chatterbox_{c}": span(d)
          for c, d in ci["unseen_cloner_eer_by_channel"].items()})

# The loudspeaker-to-microphone channel. G14: it was in dataset.extra_channels and in the
# RUNSHEET demo beat, and in no results grid. Two numbers per channel, because the shipped
# head trains on these rows and its cell is in-sample; the channel-held-out cell is the one
# that answers "what happens when a judge holds a phone up to the laptop".
rm = R["replay_mic"]
V["replay_band_chan"] = CHAN_LABEL[rm["band_used"]["channel"]]
V["replay_worst"] = rm["worst_channel"]
for c, row in rm["rows"].items():
    key = c.replace(".", "_")
    V[f"rm_{key}_n"] = str(row["n_clips"])
    V[f"rm_{key}_n_bona"] = str(row["n_bona"])
    V[f"rm_{key}_n_spoof"] = str(row["n_spoof"])
    for w in ("shipped", "channel_heldout"):
        d = row[w]
        V[f"rm_{key}_{w}_eer"] = pct(d["eer"])
        V[f"rm_{key}_{w}_ci"] = span(d["ci"])
        V[f"rm_{key}_{w}_catch"] = pct(d["spoof_called_synthetic"])
        V[f"rm_{key}_{w}_defer"] = pct(d["spoof_deferred"])
        V[f"rm_{key}_{w}_fpr"] = pct(d["genuine_called_synthetic"])

# The streaming Gate in every held-out-generator direction. GAPS.md's "reverse cloner
# direction" gap, reopened against the current 8-family setup where there is no pair and so
# no reverse, only nine leave-one-generator-out directions. The published per-channel table
# above replays a head that trained on every family it is scored on, so its committed-call
# error is in sample; these rows are not, and they are worse. The table is generated row by
# row so it grows when a family is added.
lo = R["streaming_leave_one_out"]; lob = lo["by_held_out"]; los = lo["summary"]
lci = ci["streaming_leave_one_out_clean"]
V["loo_table_rows"] = "\n".join(
    "| {g} | {n} | {cov} | {err} | {fp} |".format(
        g=GEN_LABEL[g] + (" (held-out 2025 cloner)" if g == UNSEEN_GEN else ""),
        n=lob[g]["by_channel"]["clean"]["n_spoof"],
        cov=pct(lob[g]["by_channel"]["clean"]["coverage_spoof"]),
        err=("**" + pct(lob[g]["clean_committed_error"]) + "**"
             if lob[g]["clean_committed_error"] >= 0.10 else pct(lob[g]["clean_committed_error"]))
            + f" ({span(lci[g]['committed_error'])})",
        fp=pct(lob[g]["clean_false_positive_rate"], 2))
    for g in lob)
lw, lf = los["worst_direction_clean"], los["worst_false_alarm_direction_clean"]
V.update({
    "loo_n_directions": str(los["n_directions"]),
    "loo_worst": GEN_LABEL[lw],
    "loo_worst_err": pct(los["worst_direction_clean_committed_error"]),
    "loo_worst_err_ci": span(lci[lw]["committed_error"]),
    "loo_worst_n": str(lob[lw]["by_channel"]["clean"]["n_spoof"]),
    "loo_worst_fp": GEN_LABEL[lf],
    "loo_worst_fp_rate": pct(los["worst_false_alarm_clean"], 2),
    "loo_worst_fp_ci": span(lci[lf]["false_positive_rate"], 2),
    "loo_n_blocked": str(los["n_cells_gate_cannot_commit"]),
    "loo_n_cells": str(los["n_cells_total"]),
    "loo_best": ", ".join(GEN_LABEL[g] for g in lob if lob[g]["clean_committed_error"] == 0.0),
})
# The codec-channel coverage figure, derived rather than typed, because it moved from around
# 40% to around 30% the moment two more families were added and the sentence explaining it
# did not move with it.
_codec_cov = [st["gate_replay_by_channel"][c]["seen"]["coverage"] for c in gfpr if c != "clean"]
V["cov_codec_lo"] = pct(min(_codec_cov))
V["cov_codec_hi"] = pct(max(_codec_cov))
V["cov_clean_genuine"] = pct(st["gate_replay_by_channel"]["clean"]["seen"]["coverage_genuine"])
V["n_fam_multi_prefix_codec"] = str(sum(
    1 for g in lob if len(lob[g]["by_channel"]["g722_64k"]
                          ["held_out_prefixes_at_or_above_min_commit"]) >= 3))

# The black-box convolutive attack. G8: adversarial robustness was unmeasured and the likely
# judge question is "what if the attacker knows your detector". A null result is still a
# measurement, so the range it was null over and the distortion floor it held to are both
# exported. The attacker's real bound is perceptual, so the aggressive end of the bank is
# ranked by measured signal-to-distortion and not by the nominal knob.
adv = R["adversarial_malafide"]
adv_hard = min(adv["per_filter"], key=lambda r: r["distortion_db_median"])
adv_push = max(adv["per_filter"], key=lambda r: r["median_score_shift"])
V.update({
    "adv_n_filters": str(adv["n_filters"]),
    "adv_n_spoof": str(adv["n_spoof"]), "adv_n_bona": str(adv["n_bona"]),
    "adv_n_families": str(len({g for r in adv["per_filter"]
                               for g in r["catch_rate_by_generator"]})),
    "adv_taps_lo": str(adv["taps"][0]), "adv_taps_hi": str(adv["taps"][-1]),
    "adv_side_lo": f"{adv['off_centre_energy'][0]:g}",
    "adv_side_hi": f"{adv['off_centre_energy'][-1]:g}",
    "adv_eer_before": pct(adv["before"]["eer"], 2),
    "adv_eer_worst": pct(adv["worst_case"]["by_eer"]["eer"], 2),
    "adv_catch_before": pct(adv["before"]["catch_rate"]),
    "adv_catch_worst": pct(adv["worst_case"]["by_catch_rate"]["catch_rate"]),
    "adv_dist_max": f"{max(r['distortion_db_median'] for r in adv['per_filter']):.1f} dB",
    "adv_dist_min": f"{adv_hard['distortion_db_median']:.1f} dB",
    "adv_hard_filter": adv_hard["filter"],
    "adv_hard_shift": f"{adv_hard['median_score_shift']:+.3f}",
    "adv_push_shift": f"{adv_push['median_score_shift']:+.3f}",
    "adv_push_filter": adv_push["filter"],
    "adv_broke": "yes" if adv["broke_detection"] else "no",
})

pat = re.compile(r"\{\{(\w+)\}\}")
for src in glob.glob(os.path.join(ROOT, "docs", "templates", "*.md")):
    s = open(src, encoding="utf-8").read()
    missing = sorted(set(pat.findall(s)) - set(V))
    if missing:
        sys.exit(f"{os.path.basename(src)}: unknown placeholders {missing}")
    out = pat.sub(lambda m: V[m.group(1)], s)
    dst = os.path.join(ROOT, "docs", os.path.basename(src))
    open(dst, "w", encoding="utf-8").write(out)
    print("wrote", dst)
    if os.path.basename(src) == "README.md":
        open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(out)
json.dump(V, open(os.path.join(ROOT, "docs", "NUMBERS.json"), "w"), indent=1)
