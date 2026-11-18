# Pramaan

**SIH 2026 | PS SIH26104 | AICTE Cyber Security Cell | Software | Blockchain and Cybersecurity**
*AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks*

Pramaan (प्रमाण, proof) is a real-time voice-clone defence for high-value phone approvals. It listens to the live call on the device, scores it every half second, and never lets the voice be the last factor: uncertain calls get a challenge, high-value actions get device approval, and every step is written to a tamper-evident ledger.

Every number in this file is produced by `eval/experiments.py` and `eval/latency.py` into `eval/results.json` and `eval/results/latency.json`, and this README is generated from those files by `scripts/fill_numbers.py`.

## What it does

| Part | What it is |
|---|---|
| **Listener** | Frozen `facebook/wav2vec2-xls-r-300m` (128 languages), layer 5, mean+std pooling. A head of {{n_trainable}} trained parameters. Isotonic calibration per prefix length, so 0.8 means 80%. |
| **Gate** | Streaming commit-or-defer. Commits only after {{min_commit}} s of real audio (never tile-padded), outside an uncertain band, stable for three updates. The band is derived per channel from bona fide speech alone at a {{fpr_budget}} false-positive budget, never hand-set: {{band_clean}} on the clean line, {{band_worst}} on a G.723.1 6.3 kbps line, because genuine speech scores higher the harder the codec squeezes it. |
| **Prevention ladder** | Live challenge (random digits and word in the caller's language, 160,000 combinations), out-of-band push to the claimed person's registered device, callback, operator block or clear. A high-value action is never cleared by the voice alone. |
| **Warrant** | Authorization, not detection. A disclosed voice agent is synthetic on purpose, so a signed attestation on the channel lowers the actionable risk while the synthetic verdict stands. Monotone by construction: a warrant may only ever lower risk, never raise it, enforced by an `assert` in `src/pramaan/warrant.py`, because every audio provenance signal published so far is forgeable in both directions (removal and forgery). Absent or invalid changes nothing, which is the ordinary state of a human call. Token path only; this repo embeds and detects no audio watermark. |
| **Ledger** | SHA-256 hash chain per call. Every score, verdict, challenge and approval is a block; editing any past block breaks every later hash. Verify endpoint, exportable for on-chain anchoring. |
| **Telephony** | Seven codec conditions applied at train and test time: clean, Opus 24k, Opus 8k, G.722, G.726, G.723.1, Speex WB. AMR-WB and EVS are listed as absent because the toolchain cannot encode them. |

## Results

Bona fide speech: FLEURS Hindi, Tamil, Telugu ({{n_bona}} recordings, CC-BY 4.0). Synthetic speech: {{n_seen}} generator families built locally from the same sentences, plus a 2025 zero-shot cloner (Chatterbox) held out entirely. {{n_embeddings}} cached embeddings across codecs and prefix lengths.

**Generalisation vs generator diversity.** Hold out the 2025 cloner. Train with k families, over random subsets. With few families the outcome depends on which you have (as bad as {{div_worst_small}}); with all {{n_seen}} it is {{div_kN}} regardless. The previous build of this project, trained on two families with an unweighted PCA head, scored {{legacy_unseen}} on the same cloner.

**Leave-one-generator-out, clean channel.** Train on every other family, score the held-out one against held-out genuine speech:

| held out | EER |
|---|---|
{{gm_table_rows}}

The unseen-cloner row is the honest headline. It clones the exact recording it is scored against, so corpus, speaker and content cannot be the tell. It is also why the prevention ladder is mandatory for high-value actions.

**Error bars, and the two clip counts.** The headline {{gm_chatterbox}} is an EER over **{{n_unseen_clones}} held-out clones and {{n_unseen_bona}} held-out genuine recordings**, so its 95% interval is wide: **{{ci_unseen_eer}}**, from a cluster bootstrap that resamples parent recordings rather than clips, because a bona fide recording and the clone made from it are one unit under this protocol and not two independent draws. The corpus holds **{{n_unseen_total}}** Chatterbox clips in total; {{n_unseen_clones}} of them fall in the test split of parent recordings, which is the subset the leave-one-generator-out headline is scored on. The shipped head never trains on any Chatterbox clip, so it can be scored on all {{n_unseen_total}}, and there its EER is **{{shipped_unseen_eer_ci}}**. Both counts are correct and they belong to different protocols. Every interval in this repo is in `eval/results.json` under `confidence`.

**Streaming.** First decision at {{min_commit}} s. Gate replay on seen families, **clean channel**: coverage {{cov_seen}}, committed-call error {{err_seen}}, false alarms on genuine speech {{fpr_seen}}, median decision at {{ttd_seen}} s.

**Gate replay per channel.** The band is derived per channel, so the replay is run per channel. No false-alarm number in this repo is quoted without the channel it was measured on.

| channel | gate coverage | committed-call error | false alarms on genuine speech |
|---|---|---|---|
| clean | {{cov_clean}} | {{err_clean}} | {{fpr_clean}} |
| Opus 24 kbps | {{cov_opus_24k}} | {{err_opus_24k}} | {{fpr_opus_24k}} |
| G.722 64 kbps | {{cov_g722_64k}} | {{err_g722_64k}} | {{fpr_g722_64k}} |
| G.726 32 kbps | {{cov_g726_32k}} | {{err_g726_32k}} | {{fpr_g726_32k}} |
| Speex WB | {{cov_speex_wb_q4}} | {{err_speex_wb_q4}} | {{fpr_speex_wb_q4}} |
| Opus 8 kbps | {{cov_opus_8k}} | {{err_opus_8k}} | {{fpr_opus_8k}} |
| G.723.1 6.3 kbps | {{cov_g723_1_6k3}} | {{err_g723_1_6k3}} | {{fpr_g723_1_6k3}} |

Worst false-alarm cell across the seven channels: **{{fpr_worst}} on {{fpr_worst_chan}}**, 95% CI {{ci_fpr_worst}}, which is one false alarm in {{n_unseen_bona}} genuine recordings on that channel and not a rate measured to two decimal places. Coverage on the six codec channels is {{cov_codec_lo}} to {{cov_codec_hi}} against {{cov_clean}} on clean for a cached-data reason, not a model reason, and the reason is the generator rather than the channel: only {{n_fam_multi_prefix_codec}} of the {{loo_n_directions}} generator families, counting the held-out cloner, are cached at more than one prefix length on a codec channel, every other family is cached at 4.0 s alone, and the Gate needs three stable updates at or above {{min_commit}} s before it may commit. Genuine speech, which is cached at four or eight prefixes on every channel, commits at {{cov_clean_genuine}} on clean. The clips it does not commit on are deferred, not decided wrongly.

**The same Gate, in every held-out-generator direction.** The table above replays one head that trained on every family it is then scored on, so its committed-call error is in sample and is not a generalisation claim. This table trains a separate head per direction on the other families only and replays the Gate on the held-out one against held-out genuine speech, clean channel, which is the only channel where every direction is measurable:

| held out of training | held-out clones | gate coverage on those clones | committed-call error, 95% CI | false alarms on genuine speech |
|---|---|---|---|---|
{{loo_table_rows}}

{{loo_worst}} is the worst direction at **{{loo_worst_err}}** committed-call error (95% CI {{loo_worst_err_ci}}) on {{loo_worst_n}} held-out clones, which is the same family the leave-one-generator-out EER table already reports as the hardest cell, and the Gate commits on it rather than deferring. Holding out {{loo_worst_fp}} is the worst false-alarm direction at {{loo_worst_fp_rate}} (95% CI {{loo_worst_fp_ci}}) against {{fpr_clean}} for the in-sample head. On the six codec channels {{loo_n_blocked}} of the {{loo_n_cells}} cells cannot commit on the held-out clones at all, because those clones are cached at 4.0 s alone there; their genuine halves are still measured and are in `eval/results.json` under `streaming_leave_one_out`.

At the shipped band on full 4 s clips, genuine speech is called synthetic **{{op_fpr_clean}} of the time on the clean channel** and **{{op_fpr_allchan}} pooled across all {{n_channels_scored}} channels ({{n_bona_allchan}} genuine recordings)**, worst channel {{op_fpr_worst}} on {{op_fpr_worst_chan}}.

**Loudspeaker to microphone.** A clip played out of a speaker and recorded back through the laptop microphone is a real attack path and the one a judge is most likely to trigger by holding a phone up to the laptop. The channel is not part of the seven-codec telephony grid, so the live path falls back to the most degrading band it has measured, {{replay_band_chan}} (`src/pramaan/stream.py`). Two rows, because one alone would mislead:

| channel | clips | EER, shipped head | EER, channel held out of training | clones called synthetic | genuine called synthetic |
|---|---|---|---|---|---|
| replay_mic | {{rm_replay_mic_n}} ({{rm_replay_mic_n_bona}} genuine, {{rm_replay_mic_n_spoof}} clones) | {{rm_replay_mic_shipped_eer}} | **{{rm_replay_mic_channel_heldout_eer}}** (95% CI {{rm_replay_mic_channel_heldout_ci}}) | {{rm_replay_mic_channel_heldout_catch}} | {{rm_replay_mic_channel_heldout_fpr}} |
| replay_mic_v0.4 | {{rm_replay_mic_v0_4_n}} ({{rm_replay_mic_v0_4_n_bona}} genuine, {{rm_replay_mic_v0_4_n_spoof}} clones) | {{rm_replay_mic_v0_4_shipped_eer}} | **{{rm_replay_mic_v0_4_channel_heldout_eer}}** (95% CI {{rm_replay_mic_v0_4_channel_heldout_ci}}) | {{rm_replay_mic_v0_4_channel_heldout_catch}} | {{rm_replay_mic_v0_4_channel_heldout_fpr}} |

The shipped column is **in sample**: `ship()` trains on these rows at a weight of 30 because the demo runs on this path, so {{rm_replay_mic_shipped_eer}} is not a generalisation claim and is printed only so the two are not confused. The held-out column removes every replay row from training and is the number that answers "what happens on a channel you did not train on"; the recordings themselves are still in training through their clean and codec versions, so it is a channel-shift measurement and not a held-out-clip one. **The false-alarm figure is the larger problem**: {{rm_replay_mic_channel_heldout_fpr}} of genuine speech through the speaker is called synthetic on the held-out head, against {{op_fpr_allchan}} on the telephony grid. This is the worst surface in the project and it is printed rather than hidden.

**Calibration.** Expected calibration error on the unseen cloner: raw sigmoid {{cal_raw}}, Platt {{cal_platt}}, isotonic {{cal_iso}}.

**Repair cost.** Adapting on {{ad_shotsN}} labelled recordings of the unseen cloner takes held-out error on it from {{ad_base}} to {{ad_eerN}}, scored on speakers the adapted model never saw.

**Latency on a MacBook Air M4.** {{lat_cpu4}} ms per update on CPU for a 4 s window (RTF {{rtf_cpu4}}), {{lat_mps4}} ms on MPS. {{cap_streams}} concurrent calls per CPU core at a 1 s update; {{cap_cores}} cores for a 200-seat centre at full concurrency, no GPU.

## Run it

```bash
make features   # cache frozen embeddings (resumable)
make eval       # every number, then the shipped model
make latency    # forward latency on this machine
make samples    # bundle the demo samples with their true origins
make deck       # ppt/Pramaan_SIH2026_Idea.pptx from results.json
make demo       # operator console on http://127.0.0.1:8770, offline
```

The console streams either the laptop microphone or a bundled sample through the same live pipeline, chunk by chunk in real time, and always displays the sample's true origin.

## Licences

XLS-R (Apache-2.0), FLEURS (CC-BY-4.0), EnCodec (MIT), Kokoro-82M (Apache-2.0), Chatterbox (MIT). IndicSynth (CC-BY-NC) and Meta MMS-TTS (CC-BY-NC-4.0) are research-only; a production model retrains on licensed or self-generated data.

## Layout

```
src/pramaan/     frontend, model, gate, stream, challenge, ledger, channels, server, ui/
eval/            build_features, experiments, latency, head_sweep, results.json
scripts/         generators, samples, deck, diagram, fill_numbers, demo.sh
docs/            PRESENTATION_SCRIPT, QA_PREP, RUBRIC_MAP, RUNSHEET (generated from templates/)
ppt/             SIH template, generated deck, chart assets
```
