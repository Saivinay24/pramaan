# SOTA_GAP_ANALYSIS

> Written 2026-09-14, for the National Level SIH round. Same 10 x 10 rubric as the internal round,
> plus a live demo in front of judges who may know this field.
>
> Rules this file obeys, taken from `docs/RUBRIC_ATTACK.md` and `eval/BAR.md`:
> no criterion is answered with an adjective, every Pramaan number here is traceable to
> `pramaan/eval/results.json`, `pramaan/eval/results/latency.json` or `pramaan/docs/NUMBERS.json`,
> every external number names the paper or the product it came from, and anything we have not run
> is marked **[TO MEASURE]** or **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** instead of being asserted.
> No em dashes anywhere in this file.
>
> This file adds gaps that are **not already in `GAPS.md`**. It does not restate the four that are
> (no cloner outside IndicSynth until Chatterbox, reverse-direction streaming table, cross-session
> enrolment out of scope, watermarking not robust). Where a new finding touches one of those, it
> says so and adds the part that is new. One of the four has since been restated here in full,
> the reverse-direction streaming table (G16), because reading the current code showed the gap
> was not the one that sentence described.

---

## 1. Where Pramaan sits today, honestly

Pramaan is competitive with the published field on exactly three axes and behind or unmeasured on
five. Where it is genuinely ahead: **latency on commodity hardware**, at 184.7 ms median per
4 s window on the M4 CPU with no GPU, real-time factor 0.046 (`eval/results/latency.json`), which
is faster than every named commercial detector with a published real-time factor in the Podonos
benchmark of 14 August 2026 except Corsound AI at RTF 0.035 (see the correction under G9: four
beaten, one faster, six systems with a published RTF in total), while Reality Defender there runs at RTF 1.52
and therefore cannot keep up with a live stream at all; **evaluation honesty**, in that the
leave-one-generator-out grid publishes a 24.4% clean EER cell for EnCodec resynthesis and a 13.2%
clean EER for the held-out 2025 cloner cloning the exact recording it is scored against, a
same-speaker same-sentence control that none of the commercial vendors publish and that only a
handful of 2026 papers implement; and **prevention as a first-class layer**, where the streaming
Gate, the live challenge and the out-of-band device approval mean a high-value action is never
cleared by the voice alone, which is half the problem statement's title and is where nearly every
competing system stops. Where it is behind: the **absolute accuracy** on a modern cloner is 13.2%
EER against SATYAM's 3.27% on Indic-CodecFake (arXiv 2604.19949, April 2026) and Wav2DF-TSL's
6.83% on In-the-Wild (arXiv 2509.04161), though those are different corpora and are not directly
comparable, which is the exact lesson this team already paid for once; the **training set is 8
generator families and 2,919 spoof clips**, against LRLspoof's 24 TTS systems and 2,732 hours
(arXiv 2603.02364, June 2026) and AUDETER's scale; **adversarial robustness is measured only in
the black box**, closed on 2026-09-14 by a 9-filter Malafide-style convolutive sweep that left EER
at 0.00% and the catch rate at 100.0% on all 9 filters (see G8), while **the white-box gradient
attack remains entirely unmeasured**, and 2025 to 2026 work shows the vulnerability is rooted in
the SSL representation geometry itself, which is precisely the frontend Pramaan freezes;
**calibration under narrowband
codecs was measurably broken** in a way `eval/results.json` recorded but no outward artifact
reported, closed on 2026-09-14 by deriving the commit band per channel from bona fide speech alone
(see G1 and G2), worst-channel false-alarm rate now 0.79% and published as such; and **no public baseline detector has ever been run on Pramaan's own data**, so every
"we sit near published work" statement is currently an argument from literature rather than a
measurement. The single most important thing to understand before the national round is that the
first four of those are cheap to close on the existing laptop and the fifth is a demo-day hazard.

---

## 2. Comparison table

Corpus names are attached to every EER because cross-corpus and same-corpus numbers are not
comparable. This team learned that the hard way: 0.59% on a corpus-confounded benchmark became
32.03% under a matched-pairs control (`HONEST_LOG.md`, 2026-09-03, A1).

### 2a. Detection quality and evaluation protocol

| System | Best reported EER, with the corpus named | Protocol strength | Language coverage |
|---|---|---|---|
| **Pramaan (ours)** | 0.0% XTTS-v2, 0.8% Meta MMS, 0.0% FreeVC, 24.4% EnCodec, all leave-one-generator-out on FLEURS Hindi/Tamil/Telugu, clean channel. **13.2% on Chatterbox 2025, held out entirely, same speaker and same sentence as the bona fide clip it is scored against.** | Same-speaker same-sentence held-out cloner. Recording-level splits. Grid published including failing cells. | Hindi, Tamil, Telugu bona fide in every test. Unseen-cloner test is **Hindi only**. |
| SZU-AFS (ASVspoof 5, Interspeech 2024 workshop) | 4.04% EER, minDCF 0.115, ASVspoof 5 eval | Challenge-controlled, closed and open conditions | English |
| AASIST3 (Borodin et al., ASVspoof 2024 workshop, arXiv 2408.17352) | minDCF 0.1414 open condition, ASVspoof 5 | Challenge-controlled | English |
| Wav2DF-TSL (arXiv 2509.04161) | **6.83% EER on In-the-Wild**, reported as state of the art there | Cross-domain, real-world corpus | English |
| SATYAM (arXiv 2604.19949, April 2026) | **3.27% EER on Indic-CodecFake**, 2.34% Hindi to 4.11% Tamil. AASIST baseline in the same paper: **12.47%** | Indic, 12 languages, neural-audio-codec deepfakes | 12 Indic languages including Tamil and Telugu |
| SSL-AASIST baseline, RADAR Challenge 2026 (arXiv 2605.09568) | **42.6% EER** on the multilingual, media-transformed eval set | Media transformations applied at test time | Multilingual |
| LRLspoof / 11 public countermeasures (arXiv 2603.02364, June 2026) | Per-language table across 66 languages, 24 TTS systems, 2,732 hours. Finding: countermeasures "do not transfer reliably under language shift" and language identity is an independent source of domain shift | Language-shift controlled, detector and TTS held fixed | **66 languages, 45 low-resource, includes Tamil and Telugu** |
| Resemble AI Detect | 98.05% accuracy, F1 0.981, FPR 2.5%, on the Podonos benchmark, 4,524 clips, **English only**, 14 August 2026 | Vendor-independent third-party benchmark | English-first, no published per-language grid |
| Pindrop | 95.05% accuracy, FPR 6.2% on the same Podonos benchmark. Pindrop's own public claim is ~99%, which is self-reported and not on an independent private benchmark | Third-party number exists and is lower than the marketing number | English-first |
| Reality Defender | 71.27% accuracy, **FPR 53.7%** on the same Podonos benchmark | Third-party | English-first |
| Corsound AI | 87.79% accuracy, FPR 1.0%, FNR 23.1%, same benchmark | Third-party | English-first |
| Open-source models as benchmarked by Podonos (Wav2Vec2, RawNet2, LCNN, AASIST) | 47.63% to 62.89% accuracy | Third-party | English-first |

### 2b. Deployment axes

| Axis | Pramaan | Academic SOTA | Commercial |
|---|---|---|---|
| Latency / RTF | **184.7 ms median, RTF 0.046, CPU fp32, 4 s window**; 103.9 ms, RTF 0.026 on MPS (`eval/results/latency.json`) | Not usually reported. SSL-AASIST is 318M params and is reported as batch, whole-file | Pindrop 282 ms, RTF 0.076; Corsound 180 ms, RTF 0.035; Resemble 1,164 ms, RTF 0.40; Reality Defender 5,718 ms, RTF 1.52 (Podonos, 14 Aug 2026) |
| Streaming / partial audio | First legal decision at 1.5 s, score every 0.5 s, never tile-padded. Unseen-cloner EER by prefix: 38.1% at 0.5 s, 30.2% at 1.0 s, 17.4% at 1.5 s, 13.2% at 2.0 s, 9.1% at 4.0 s (`results.json`, `streaming.per_prefix`, remeasured 2026-09-14 with the streaming head trained through the codec grid) | Semjonovs, rs-10257178, Aug 2026, sequential commit-or-defer under telephony codecs. "Audio Deepfake Detection at the First Greeting: Hi!" arXiv 2601.19573, ultra-short 0.5 to 2.0 s inputs, S-MGAA | Hydaway RealityChek shipped streaming audio detection to enterprise in July 2026; Modulate advertises detection "seconds after receiving audio". **Streaming is no longer an unclaimed differentiator in the market** |
| Language coverage | Hindi, Tamil, Telugu bona fide. Unseen-cloner test Hindi only | LRLspoof 66 languages, IndicSynth 12, Indic-CodecFake 12, XMAD-Bench cross-domain multilingual (arXiv 2506.00462) | English-first. Bachao.AI markets Indian regional language coverage including Hindi, Tamil, Telugu, WhatsApp-based, ~30 s verdict. HyperVerge markets Indian-language KYC-integrated APIs. **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether either publishes a per-language accuracy number |
| Prevention, not just detection | Challenge from 160,000 combinations, out-of-band push to the registered device, callback, operator block. High-value action never cleared by voice alone, enforced in `src/pramaan/stream.py` | PITCH, ACM AsiaCCS 2025, 56.0% to 88.7% AUROC with a challenge. D-CAPTCHA and **D-CAPTCHA++ (arXiv 2409.07390) show the challenge-response protocol itself falls to transferable imperceptible adversarial attack** | Step-up verification is a workflow feature, not a published mechanism. No vendor publishes a challenge space size |
| Adversarial robustness | **Black box measured, white box not.** 9-filter Malafide-style convolutive sweep, 505 held-out spoof clips from 6 seen families against 127 held-out genuine recordings: EER 0.00% and catch rate 100.0% on all 9 filters, no retraining or recalibration (G8, closed 2026-09-14). The white-box gradient attack remains unmeasured | Malafide convolutive noise attack (arXiv 2306.07655). Universal adversarial perturbations vs AASIST and vocoder-fingerprint detectors (Future Internet 18(7):344). Transferable attacks, WACVW 2025. "Escaping the Linearity Trap" (arXiv 2605.30366) locates the vulnerability in **the transferable representation geometry of SSL models**, not the classifier head | Not published by any vendor |
| On-device / edge | **Yes, fully. Wi-Fi off, no model or CDN fetched at run time, 2,049 trainable parameters, 5.4 streams per CPU core at a 1 s hop, 37 cores for 200 seats** (`latency.json`, `capacity.cpu_hop_1.0`) | SATYAM uses a frozen Qwen2-7B decoder, so it is not laptop-deployable. SSL-AASIST at 318M params is borderline | All seven named commercial systems are cloud APIs. This is Pramaan's clearest structural advantage and it is also the privacy posture the PS asks for |
| Authorization / provenance layer | Cited in `docs/SPEAKER_S6.md`, **not implemented in `pramaan/src`**. The hash-chained ledger is implemented (`src/pramaan/ledger.py`) | C2PA, STIR/SHAKEN, SASV, MerkleSpeech. AudioMarkBench (NeurIPS 2024). Newer and worse for watermarking: "SoK: How Robust is Audio Watermarking in Generative AI models?" (arXiv 2503.19176), "Learning to Evade" (arXiv 2606.22310), "How Fragile Is Your Watermark? Training-Free Structural Removal" (arXiv 2608.16566) | STIR/SHAKEN attests roughly 35% of US calls at full attestation and overseas-originated calls bypass it. India's CNAP rollout under TRAI is the India-relevant primitive and is **not currently named anywhere in Pramaan's artifacts** |

---

## 3. Prioritized gap list

Ranked by rubric points at stake and by effort on a 16GB M4 with no GPU. Assume as little as one
week. Everything in P0 and P1 runs on the existing laptop with the existing environment.

### P0. Do these first. Hours, not days, and each one is a demo-day or credibility hazard.

**G1. The shipped band produces catastrophic false positives under narrowband codecs, and no
outward artifact says so.**
`eval/results.json` records `fpr_at_p50` per generator per condition. On the XTTS-v2 row it is
0.79% clean but **96.85% on opus_8k and 98.43% on g723_1_6k3**. The pattern repeats on every
generator row. Expected calibration error on those cells is 0.646 and 0.658 against 0.013 clean.
Meanwhile `docs/NUMBERS.json` carries `fpr_seen: 0.0%` with no channel attached, and the README
says "false alarms on genuine speech 0.0%". Those two facts are both true and they are about
different channels.
*Why it matters:* criterion 6 and criterion 8. The Gate's fixed band is `[0.15, 0.85]` and a judge
who asks for an 8 kbps line during the live demo gets a system that calls a real human synthetic.
It also contradicts the strongest single sentence in the deck, that the system misses clones
rather than accusing humans.
*Smallest step:* compute gate-replay coverage, committed error and false-positive rate **per
condition**, not pooled, and put the per-channel false-positive row in the grid. Re-fit the
per-prefix isotonic calibrators per bandwidth class (`channels.BANDWIDTH` already splits wb and
nb) or, at minimum, state the clean-channel scope on every slide that prints 0.0%.
*Hardware:* laptop. Features are already cached, 58,524 embeddings. Minutes of compute.

> **CLOSED 2026-09-14.** Root cause measured, not guessed. The 96.85% and 98.43% cells are
> `fpr_at_p50` inside the leave-one-generator-out protocol, which trained on **clean audio
> only** (`train_conds=("clean",)`) and then scored through every codec at a fixed 0.5
> threshold. On the shipped head, genuine 98th-percentile log-odds sits at -3.11 clean and
> +1.95 on G.723.1 6.3 kbps; on the clean-trained diagnostic head the same quantile moves
> to +7.29, crossing the boundary, while spoof scores barely move (+7.87 to +8.88). The
> shift is on the genuine side and it tracks bitrate, not sample rate: Opus 8 kbps is
> wideband by `channels.BANDWIDTH` and behaves like the 6.3 kbps narrowband line.
> Three changes: `streaming()` now trains and calibrates through the whole codec grid, as
> `ship()` already did; the gate replay runs **per channel** and `results.json` carries
> `streaming.gate_replay_by_channel` and `operating_point.per_channel_genuine`; and every
> outward false-alarm claim now names its channel. Measured after: gate false-alarm rate on
> genuine speech is 0.00% on clean, Opus 24k, G.722 and Opus 8k, and 0.79% on G.726, Speex
> WB and G.723.1, so the honest worst cell across seven channels is **0.79%**, not 0.0%.
> At the shipped band on full 4 s clips it is 0.2% clean, 0.9% pooled over 3,570 genuine
> recordings on all seven channels, worst channel 1.6% on Opus 24k. All five demo samples
> of genuine speech read HUMAN on all seven channels through the live pipeline.
> `generator_matrix` keeps the failing cells and now carries `generator_matrix_note`
> saying what protocol they belong to.

**G2. The Gate's band is a hardcoded constant, which is a regression from the method the parent
repo already proved.**
`src/pramaan/config.py` has no band. `results.json` `ship.band` is `0.85 / 0.15` at every prefix.
The parent repo's `eval/select_operating_point.py` derives the band **from the bona fide
distribution alone against a false-positive budget**, precisely because `HONEST_LOG.md`
2026-09-03 measured that spoof score location does not transfer across cloners while genuine
score location does. Pramaan's own `operating_point` block reproduces that failure: on the unseen
cloner the band calls 12.8% synthetic, defers 20.5% and waves **66.7% through**, even though the
ranking EER is 7.6%.
*Why it matters:* criterion 4. "Why is your threshold 0.85?" currently has no answer better than
"we picked it". With the FPR-budget derivation it has a principled one, and it is the same answer
that survives a new cloner.
*Smallest step:* port `select_operating_point.py` into `eval/experiments.py`, derive the band per
prefix at a stated FPR budget on genuine speech only, report the band it selects next to the fixed
one. If the derived band is close to 0.15/0.85, say so and keep the constant, now justified.
*Hardware:* laptop. Seconds of compute on cached features.

> **CLOSED 2026-09-14.** The derivation was present but dead: `experiments.py` wrapped both
> quantiles in `max(q, 0.85)` and `min(q, 0.15)`, and both clamps bound at every prefix, so
> `ship.band` was the constant. The clamps are gone. `pramaan.model.band_from_genuine`
> ports the parent repo's method: `tau_clone` is the lowest calibrator step strictly above
> the (1 - budget) quantile of bona fide calibrated scores and `tau_human` is their 90th
> percentile, at a stated 2% false-positive budget, bona fide only, no spoof clip of any
> generator consulted. Derived per channel rather than per bandwidth class, because the
> measurement says bitrate is the axis, and pooled over prefixes at or above MIN_COMMIT_S
> because there are only 76 genuine calibration clips per (channel, prefix) and a
> 98th-percentile quantile on 76 samples produced a clean band that swung from 0.99 at
> 2.5 s to 0.036 at 4.0 s with no mechanism behind it. Pooling puts 304 to 456 clips behind
> each threshold and the resulting band rises monotonically with codec severity:
> [0.010, 0.013] clean to [0.013, 0.714] on G.723.1 6.3 kbps, a 55x move in `tau_clone`
> that the fixed 0.85 could not express.
> The effect on the answer "why 0.85?" is that there is now a table: `results.json`
> `band_selection` sweeps budgets 0.002 to 0.05 against the parent repo's unmoved
> `eval/BAR.md` bar and reports honestly that the worst-channel false-positive rate is flat
> at 0.79% across the whole grid, so the budget is **not identified** by the sweep and 2%
> is a declared choice inside the flat region rather than a fit.
> The effect on behaviour is larger than expected and is the answer to G2's own criticism:
> on the unseen 2025 cloner the shipped band now calls **69.2% synthetic and waves 30.8%
> through**, against 12.8% and 66.7% under the fixed band. The `operating_point` headline
> sentence in `results.json` is regenerated to match. The live path uses it: the bundle
> carries `band_by_channel`, `stream.py` selects by the call's declared channel and falls
> back to the most degrading condition measured, never to clean.

**G3. The headline number rests on n = 39 clips with no confidence interval, and the count is
inconsistent across artifacts.**
`dataset.by_generator.chatterbox` is 39. `docs/NUMBERS.json` carries `n_chatterbox: 39` and
`n_unseen_clones: 23`. The parent repo's `challenge_eval.py` reports Wilson intervals because "a
rate from nine calls without an error bar is not a measurement"; Pramaan's `results.json` carries
no interval on any EER.
*Why it matters:* criterion 2 and 5. The single most likely hostile question from a judge who
knows statistics is "what is the error bar on 13.2% from 39 clips?", and the answer
"[TO MEASURE]" is much worse than a printed interval.
*Smallest step:* bootstrap 95% CIs for the unseen-cloner EER and the gate-replay rates, and
reconcile 23 vs 39 in one place. **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** which of the two is the
scored subset.
*Hardware:* laptop, seconds.

> **CLOSED 2026-09-14.** The 23-vs-39 question is settled by reading the masks in
> `eval/experiments.py`, not by choosing. **Both counts are correct and they belong to
> different protocols.** 39 is every Chatterbox clip in the corpus
> (`dataset.by_generator.chatterbox`); the shipped head trains only on `seen` generators, so
> no Chatterbox clip is ever in its training set and all 39 are legitimately held out at the
> operating point. 23 is the subset that lands in the 25% test split of parent recordings,
> which is what `generator_matrix` scores, because the leave-one-generator-out protocol also
> needs its **genuine** side held out from the head's training split. The headline 13.2% is
> therefore an EER over **23 clones and 127 genuine recordings**, and the 39-clip cell is the
> shipped head at 7.6%. `results.json` `confidence.clip_count_reconciliation` states this in
> the file itself so the question cannot come back.
> New `confidence` protocol in `experiments.py`. EERs get a **cluster bootstrap that
> resamples parent recordings, not clips**, because under the same-speaker same-sentence
> protocol a bona fide recording and the clone made from it are one unit and not two
> independent draws; the clip-level bootstrap would be narrower and would be wrong. Rates get
> **Wilson score intervals**, because several of them are zero and the normal approximation
> collapses to a point there. 2,000 resamples, seed 0.
> Measured: headline unseen-cloner EER **13.2%, 95% CI 5.6% to 22.1%**. Shipped head on all
> 39 clips **7.6%, 95% CI 3.3% to 9.6%**. Shipped band on the unseen cloner calls 69.2%
> synthetic, **95% CI 53.6% to 81.4%**, and waves 30.8% through, **95% CI 18.6% to 46.4%**.
> Worst-channel gate false alarms **0.79%, 95% CI 0.14% to 4.33%**, which is one false alarm
> in 127 genuine recordings and not a rate known to two decimal places. The protocol
> reproduces every published `generator_matrix` Chatterbox cell to the digit, per channel,
> which is itself a check that the interval is an interval on the number the deck quotes.
> Published in README, QA_PREP (a new "what is the error bar" answer), TEAM_GUIDE's numbers
> table, RUBRIC_MAP criterion 5 and SPEAKER_S4's numbers table and evidence section.

**G4. Two external numbers on the deck are now contestable by a judge with a phone.**
First, the 40.32% figure for English-trained AASIST on Indic-CodecFake. The Indic-CodecFake paper
itself (arXiv 2604.19949, April 2026) reports **AASIST at 12.47% EER** on ICF. Those are almost
certainly different training conditions, but a judge reading the paper sees 12.47% and hears
40.32% from the stage. Second, the challenge space: `src/pramaan/challenge.py` gives
10^4 digits x 16 lexicon words x 1 template = **160,000**, which the Pramaan README states
correctly, while the parent repo and the original architecture note say ~480,000 (three task
templates).
*Why it matters:* criterion 10 and criterion 2. `RUBRIC_ATTACK.md` already mandates a
cross-artifact numbers sweep. These are two live failures of it.
*Smallest step:* either state the 40.32% with its exact training condition attached or drop it and
cite the paper's own 12.47% AASIST baseline plus SATYAM's 3.27% as the honest Indic reference
points. Fix 160,000 vs 480,000 to one number everywhere, or restore the third template in code.
*Hardware:* none.

> **CLOSED 2026-09-14.** Both halves, and this entry itself was partly wrong about where the
> numbers live.
> **(a) The 40.32%.** No artifact in this repo prints 40.32%. What it printed was the same
> claim in rounded prose, in `docs/templates/SPEAKER_S4.md`: "Published research puts
> English-trained detectors at around 40% on Indian-language fakes, so 13.2% on a cloner
> released this year is a strong place for a one-week laptop build to be." That sentence puts
> our EER next to a foreign corpus's EER, which `RUBRIC_ATTACK.md` bans and which this team
> already published a document explaining. **No training condition producing 40.32% could be
> verified from a real source, so the number is dropped rather than re-sourced.** The sentence
> is replaced with the paper's own figures, quoted as reference points and explicitly not as a
> comparison: Indic-CodecFake (arXiv 2604.19949, April 2026) reports **AASIST at 12.47% EER**
> and **SATYAM at 3.27% EER** on Indic-CodecFake, a different corpus with different cloners
> and a different protocol. S4 now says out loud that nobody has run those systems on our data
> and we have not run ours on theirs, and that this is a named roadmap gap rather than a
> number we may invent. That is G6 restated as a sentence a speaker can say.
> **(b) The challenge space.** Reconciled to **160,000, which is what the code does**, and the
> premise of this entry was wrong: no Pramaan document, template, script or slide has ever
> said 480,000. `grep` over the whole repo finds 160,000 in README, TEAM_GUIDE, QA_PREP,
> SPEAKER_S2, `scripts/draw_architecture.py` and the console, and 480,000 nowhere. The
> 480,000 belongs to the **parent repo's** `src/kempelen/challenge.py`, whose `ChallengeBank`
> carries three task templates per language (`digits_then_word`, `word_then_digits`,
> `digits_reversed`) and correctly reports 10^4 x 16 x 3.
> **The third template is deliberately not restored**, and the reason is `docs/RUNSHEET.md`
> demo beat 3: the operator reads the issued challenge aloud off the console, and
> `digits_reversed` changes what the caller is being asked to do. Landing a new challenge
> form days before a live demo buys a bigger number and risks a rehearsed beat. It is a
> one-line change and it is deferred, stated as such in `src/pramaan/challenge.py` next to a
> named `N_TEMPLATES = 1` constant, so the arithmetic is visible rather than folded into a
> literal.
> Two supporting changes so the number cannot drift again: `space_size()` gains the docstring
> that says which repo's number is which, and `src/pramaan/ui/index.html` no longer hardcodes
> "1 of 160,000"; the `Challenge` dataclass carries `space` and the console renders it. The
> console now cannot disagree with the code.

### P1. Days, not weeks. Each converts an argument into a measurement.

**G5. ~~A free, already-published, Tamil and Telugu held-out cloner evaluation now exists and nobody
on this team has seen it.~~ ~~CORRECTED 2026-09-14: the corpus this entry named does not do what
this entry says. SEA-Spoof is the near-term target, not LRLspoof.~~ CORRECTED A SECOND TIME
2026-09-14: SEA-Spoof is not the near-term target either. No public corpus reachable from this
laptop covers Tamil AND Telugu. The target is IndicF5, a 1.4 GB cloner, not a corpus.**

> **SECOND CORRECTION, 2026-09-14, and this one is from fetched bytes rather than from dataset
> cards.** The first correction below was right that LRLspoof fails and right about why. It was
> wrong to name SEA-Spoof as the replacement, and it left two questions marked
> **[UNVERIFIED, NEEDS A HUMAN TO CHECK]**. Both are now settled by direct fetch. A second
> correction is cheaper than a standing wrong claim, so here it is.
>
> **What was actually fetched, 2026-09-14, and the exact evidence.**
>
> | Question the first correction left open | Answer, measured | How it was measured |
> |---|---|---|
> | Is Tamil in LRLspoof at all? | **No.** Zero of the 1,304,455 utterance IDs begin with `tamil/`. | Pulled `data/labels.parquet` (6,345,951 bytes, not gated) from `lab260/LRLspoof` and grouped every `utterance_id` by its first path segment. 66 languages, none of them Tamil. |
> | How much Telugu, and from how many synthesizers? | **12,000 clips from exactly 1 synthesizer, `indictts`.** Hindi, for comparison, is 16,000 clips from 2 (`indictts` 4,000, `kokoro` 12,000). | Same labels.parquet, grouped by the second path segment. |
> | Is LRLspoof really spoof only? | **Yes, proven rather than quoted.** The `label` column is `1` for all 1,304,455 rows. There is not one bona fide row. | Value count over the `label` column. |
> | Is the 452 GB figure right? | **Yes, exactly.** 43 parts x 10,737,418,240 bytes = 452,045,616,080 bytes = 452.0 GB. | HuggingFace tree API, recursive listing of `lab260/LRLspoof`. |
> | Does ModelScope expose per-language files? | **No file listing is exposed at all.** Both the recursive and the non-recursive `oss/tree` endpoints return `"Data":[]`. The ModelScope README repeats the same 66 languages and Tamil is absent there too. | `modelscope.cn/api/v1/datasets/lab260/LRLspoof/oss/tree`, two query shapes. |
> | Is `Jack-ppkdczgx/SEA-Spoof` live? | **Yes**, HTTP 200 on the dataset API, 899 downloads, DOI 10.57967/hf/9195. | HuggingFace dataset API. |
> | Does SEA-Spoof cover Tamil AND Telugu? | **Tamil yes. Telugu NO.** The language tags are exactly `en, hi, id, ms, ta, th, vi`. Telugu is not in the corpus. The first correction assumed Tamil and said nothing about Telugu, and half of the gap is Telugu. | Language tags on the dataset API response. |
> | Can it be pulled? | **No, not without a human being approved by the authors.** `"gated": "manual"`. Fetching any file returns `Access to dataset Jack-ppkdczgx/SEA-Spoof is restricted. You must have access to it and be authenticated to access it.` The card requires emailing `wu_jinyang@a-star.edu.sg` and `imcc.sg@gmail.com` first, restricts use to approved non-commercial academic researchers, and says each request is reviewed by hand. | Direct `resolve/main` fetch of `metadata/dataset_metadata.json`. |
> | How big is it, and is `streaming=True` a way in? | **81.5 GB** (81,538,998,805 bytes: train 439,362 examples, validation 57,158, evaluation 57,226). Shards are `data/train/train-000NN.parquet`, split **by index, not by language**; the smallest train shard measured is 1,348,858,640 bytes = 1.35 GB. So even with access there is no per-language file to pull. Streaming and filtering on the `language` column would work the way `research/03_data.md` pulls IndicSynth, but it must read whole shards until enough Tamil rows appear. **[TO MEASURE]** how many GB that costs, and it cannot be measured until access is granted. | HuggingFace tree API on `data/train`, plus the `dataset_info` block on the dataset API. |
>
> **The conclusion, stated plainly: no public corpus reachable from this laptop today covers
> both Tamil and Telugu.** LRLspoof has Telugu and not Tamil, is spoof only, and is locked in a
> 452 GB tarball with no per-language access on either host. SEA-Spoof has Tamil and not Telugu,
> and is locked behind a manual email approval. Neither of them alone closes G5 even if the
> download budget existed, and together they still would not, because neither has a bona fide
> side that pairs with Telugu.
>
> **The next real candidate is IndicF5, and it is a cloner, not a corpus.** `ai4bharat/IndicF5`,
> checked 2026-09-14: text-to-speech, `license:mit`, 27,758 downloads, one weight file
> `model.safetensors` of 1,402,789,408 bytes = **1.4 GB**, against 81.5 GB and 452 GB. Its gate
> is `"gated": "auto"`, not `manual`: fetching `README.md` unauthenticated returns
> `Access to model ai4bharat/IndicF5 is restricted`, so it needs a HuggingFace account, one
> click to accept the terms and a token, and no human reviewer on the far side. It is more
> tractable than either corpus by three orders of magnitude of download and by one whole
> approval step. **[TO MEASURE]** whether the `f5_tts` dependency stack installs against the
> pinned py3.14 environment; `HONEST_LOG.md` in the parent repo already records `fairseq` and
> `chatterbox-tts` conflicting with these pins, so the side-venv pattern is the expected answer.
>
> **And the reason IndicF5 is the right answer is this team's own A1 result, not its file size.**
> A cloner run against the FLEURS Tamil and Telugu parents **already on this laptop** produces
> same-speaker same-sentence matched pairs, which is the only protocol that keeps the 32.03%
> corpus confound out of the number. A downloaded spoof-only corpus cannot do that at any size.
> One 1.4 GB cloner closes the gap that a 452 GB download does not.
>
> **What landed instead, this session.** Tamil and Telugu are no longer absent from the grid.
> `espeak_ng` contributes 170 Tamil and 170 Telugu spoof clips and `piper` contributes 170
> Telugu, all generated on this laptop from the same FLEURS Tamil and Telugu parents the bona
> fide clips speak, so they are same-corpus and same-sentence. They are **not** voice-matched
> (`voice_matched=0` in `data/manifest_breadth.csv`), so they are a same-sentence comparison and
> not a matched-pairs one, and they must not be quoted as if they were. That distinction is the
> whole reason DATA_PLAN A5.1 added the column.
>
> **Cost of this second correction: two small fetches and no download.** `labels.parquet` at
> 6.3 MB is the only file pulled. No part of the 452 GB tarball and no part of the 81.5 GB
> parquet set was touched.
>
> The first correction is kept below unedited, because it is still right about LRLspoof and a
> reader should see what changed rather than find a silently rewritten file.

> **CORRECTION, 2026-09-14, from `docs/DATA_PLAN.md` section A2, which checked the actual
> hosting instead of the abstract.** This entry as originally written is wrong in three ways
> and the wrong version must not be worked from.
>
> 1. **LRLspoof is spoof only. It has no bona fide side** (HuggingFace dataset card,
>    `MTUCI/LRLspoof`, fetched 2026-09-14: 1,304,455 TTS utterances, spoof only). Scoring it
>    therefore means taking the genuine side from FLEURS, which reproduces **exactly the
>    corpus confound this team already measured and published**: `HONEST_LOG.md` 2026-09-03
>    A1, 0.59% EER cross-corpus against **32.03%** under the matched-pairs control, with the
>    score medians settling it (cross-corpus spoof +0.01, same-corpus spoof -9.38,
>    cross-corpus bona fide -11.14). "Download a test set and score our shipped head on it"
>    would hand a judge our own published mistake, run a second time, on purpose.
> 2. **There is no easy per-language pull.** It ships as a 452 GB multi-part tarball
>    (`lrl_spoof.tar.gz.part_*`), extracted as `<language>/<tts_model>/<file>.wav`, not via
>    `load_dataset`, so the `streaming=True` per-language trick does not apply. 452 GB does
>    not fit on this machine under any reclaim scenario in `DATA_PLAN.md` section 1.1, which
>    measured 274 MB free.
> 3. **Tamil is absent from the paper's per-language table entirely**, and Telugu is 22.12
>    hours from **one** synthesizer (arXiv 2603.02364, Table 2, fetched 2026-09-14). One
>    synthesizer is one cell, not a held-out-cloner grid.
>    **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether Tamil is in the corpus at all; the
>    abstract says 66 languages and this entry asserted Tamil, and the table as fetched does
>    not list it.
>
> **The replacement target is SEA-Spoof (arXiv 2509.19865): 300+ hours of PAIRED real and
> spoof across Tamil, Hindi, Thai, Indonesian, Malay and Vietnamese, from 10 open-source and
> 4 commercial TTS/VC systems.** Paired is the word that matters, because a bona fide side
> from the same corpus is what keeps the A1 confound out of the number.
> **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether
> `huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof` is live, its size on disk and its licence.
> Two licences are also in conflict for LRLspoof itself, MIT on the HF card against CC BY 4.0
> in the paper, and a human must resolve that before any slide names one.
>
> **Priority order is inverted from what this entry says: SEA-Spoof labels first, LRLspoof
> labels second.** And the single highest-value item for the Tamil and Telugu gap is neither
> corpus: it is **IndicF5**, which clones from a reference prompt and can therefore run the
> same-speaker same-sentence matched-pairs protocol in Tamil and Telugu, which is the thing
> neither corpus can do. One cloner closes the gap that a 452 GB download does not.
> See `docs/DATA_PLAN.md` sections A2 and A4.2.
>
> **Nothing outward cited the wrong version.** `grep` for LRLspoof, SEA-Spoof, "66 languages"
> and "2,732 hours" across `docs/`, `scripts/`, `README.md` and the deck builder returns
> nothing outside this file and `DATA_PLAN.md`, so no slide or speaker script had to be
> corrected. `docs/QA_PREP.md` already answers the Tamil and Telugu question with IndicF5 as
> the roadmap item, which is the correct answer under this correction.
>
> The original text of this entry is kept below, struck through in the heading, so a reader
> can see what changed rather than finding a silently edited file.
`GAPS.md` logs "A2 is Hindi only, Tamil and Telugu unmeasured, IndicF5 is the named candidate".
**LRLspoof (arXiv 2603.02364, Borodin et al., June 2026) is 2,732 hours from 24 open-source TTS
systems across 66 languages including Tamil and Telugu, with 11 public countermeasures already
scored on it.** That turns the single biggest open gap in `GAPS.md` from "build a cloner" into
"download a test set and score our shipped head on it", and it hands over a published baseline
table to compare against on the same data.
*Why it matters:* criterion 3 directly, because the PS names Indian languages and dialects as a
requirement, and criterion 2, because the paper's central finding, that language identity is an
independent source of domain shift, is the same class of finding as this team's own corpus-shortcut
result and should be cited as such rather than rediscovered.
*Smallest step:* pull only the Tamil and Telugu partitions, cap at a few hundred clips to fit the
disk, embed with the existing frozen frontend, score the shipped head, publish the two cells even
if they are bad. Do not retrain.
*Hardware:* laptop. Disk is the constraint, not compute. `GAPS.md` already records the disk
blocker from 2026-09-03, so free space first.

**G6. No public baseline detector has ever been run on Pramaan's own data.**
Every comparative statement in the deck is literature-to-literature. `RUBRIC_ATTACK.md` bans
putting any foreign-corpus EER next to our own for exactly this reason, and G4 closed the one
place this repo did it in prose.
*Why it matters:* criterion 2 and criterion 4. "How do you compare to AASIST?" currently gets a
citation. With one baseline run it gets a row in our own grid, on our own data, which is a far
stronger answer and costs one afternoon.
*Smallest step:* take one public inference-only checkpoint (the RADAR 2026 and LRLspoof papers
both name `ssl_aasist` and `w2v2_300` as public countermeasures) and score it on the existing
FLEURS + 6-family test split and on the Chatterbox set. Inference only, no training. Publish
whichever way it lands, including if the baseline wins.
*Hardware:* laptop, CPU inference. 318M-parameter forward passes over roughly 800 test clips are
minutes, not hours. **[TO MEASURE]** whether the checkpoint loads on the pinned py3.14 stack;
`HONEST_LOG.md` already records that `torchaudio.load()` is broken here and everything must use
`soundfile`.

> **STILL OPEN 2026-09-14, and the blocker is now measured rather than suspected.** The
> "[TO MEASURE] whether the checkpoint loads on the pinned py3.14 stack" above is now
> measured, and the answer is no, for the canonical route.
> `ssl_aasist` as published (Tak et al., the SSL_Anti-spoofing line the RADAR 2026 and
> LRLspoof papers both name) loads its XLS-R frontend through **fairseq**, not through
> `transformers`. Measured on this machine on 2026-09-14, `pip install --dry-run fairseq`
> against the pinned environment:
>
> ```
> ERROR: Failed to build 'fairseq' when getting requirements to build wheel
>   FileNotFoundError: [Errno 2] No such file or directory: 'fairseq/version.txt'
> ```
>
> fairseq has no wheel for CPython 3.14 and its source build fails before dependency
> resolution even finishes. The resolution it did reach is independently disqualifying:
> fairseq 0.12.2 pins **`omegaconf<2.1`** and **`hydra-core<1.1,>=1.0.7`**, against
> `omegaconf 2.3.1` installed here. That is the same class of event as the Chatterbox install
> `GAPS.md` records, which would have downgraded transformers 5.16.1 to 5.2.0 and librosa
> 1.0.0 to 0.11.0 inside the stack every published number in this repo was computed on.
> **Stopped rather than forced**, per this entry's own instruction and `HONEST_LOG.md`'s
> warning about disturbing the pinned stack. The honest statement for the roadmap and for a
> judge is: **no public baseline detector has been run on Pramaan's own data, the blocker is a
> dependency conflict and not compute or disk, and every comparative statement in the deck is
> literature to literature until it is closed.**
> **What would close it, for whoever picks it up**, in order of cost:
> 1. A `transformers`-native reimplementation of SSL-AASIST, or any published checkpoint whose
>    loader does not import fairseq. **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether one
>    exists with weights, and whether its numbers are the ones the papers report.
> 2. An isolated venv on an older Python, on the rented box rather than on this laptop, which
>    is the same rule `docs/DATA_PLAN.md` B4 already sets for generator families: nothing from
>    that venv ever comes back, only scores.
> 3. Nothing else. Do not install fairseq into this environment for any reason.
>
> Disk is no longer the constraint: `df -h /System/Volumes/Data` reported **21 Gi free** on
> 2026-09-14, against the 274 MB `DATA_PLAN.md` measured earlier the same day.
> **S5's new latency table and S4's rewritten EER glossary both already point at this gap by
> name**, so the deck states the absence rather than papering over it.

**G7. The demo uses an ElevenLabs clone that appears in no evaluation.**
`data/samples/clone_elevenlabs.json` and a 103 KB ElevenLabs mp3 sit in the repo, and
`docs/RUNSHEET.md` says the ElevenLabs clone played through the microphone reads as synthetic at
1.5 s. There is no ElevenLabs row anywhere in `eval/results.json`, and `SPEAKER_S6.md` says the
finals roadmap includes "the paid cloners attackers actually use".
*Why it matters:* criterion 5 and criterion 9. A commercial-grade cloner is what the threat model
actually describes, and the team already has the audio. A judge who notices the demo plays a
cloner that is not in the grid will ask why.
*Smallest step:* generate 20 to 40 ElevenLabs clones of test-split FLEURS Hindi recordings under
the same same-speaker same-sentence protocol as Chatterbox, embed, score the shipped head, add
one row. If the budget for API credits is the blocker, say so on the roadmap slide with the number
of clips it would take.
*Hardware:* laptop plus a paid API. This is the one P1 item with a rupee cost attached, and it is
small.

**G8. Adversarial robustness is entirely unmeasured, and the 2026 literature aims directly at
frozen SSL frontends.**
The likely judge question is "what if the attacker knows your detector". There is no answer in any
artifact. The relevant finding is not generic: "Escaping the Linearity Trap" (arXiv 2605.30366)
places the vulnerability in the transferable representation geometry of SSL models themselves,
which means freezing XLS-R does not avoid it and may make transfer attacks easier, since the
frontend is public and identical for the attacker.
*Why it matters:* criterion 4, and it is the highest-leverage unanswered question in the whole
deck. Answering it with a measured degradation curve is a criterion-2 point as well.
*Smallest step:* run a **Malafide-style convolutive noise attack (arXiv 2306.07655)**, not a
gradient attack. It is a short linear filter applied to spoof audio, needs no backward pass, runs
on CPU in minutes, and models an attacker with only black-box access. Report EER before and after
on the seen families. Then state plainly that a white-box gradient attack is not measured and that
adversarial training is out of scope on this hardware.
*Hardware:* laptop. Deliberately chosen because it needs no gradients.

> **CLOSED 2026-09-14, and the result is a null one.** `eval/malafide.py` runs the black-box
> Malafide variant and writes `eval/results.json["adversarial_malafide"]`. Surface: 505 held-out
> spoof clips from the 6 seen families against 127 held-out genuine recordings, filter applied to
> spoof audio only, detector the shipped bundle with no retraining, refitting or recalibration.
> Bank: 9 random non-causal FIR filters, 129, 257 and 513 taps at 16 kHz crossed with 0.05, 0.15
> and 0.35 off-centre energy, seed 0.
>
> | filter | taps | EER | AUROC | called synthetic | median score shift | median S/D |
> |---|---|---|---|---|---|---|
> | *before the attack* | 1 | 0.00% | 1.0000 | 100.0% | 0.000 | n/a |
> | `fir129_s0.05` | 129 | 0.00% | 1.0000 | 100.0% | -0.018 | 26.2 dB |
> | `fir129_s0.15` | 129 | 0.00% | 1.0000 | 100.0% | -0.134 | 19.2 dB |
> | `fir129_s0.35` | 129 | 0.00% | 1.0000 | 100.0% | +0.162 | 15.5 dB |
> | `fir257_s0.05` | 257 | 0.00% | 1.0000 | 100.0% | +0.040 | 28.6 dB |
> | `fir257_s0.15` | 257 | 0.00% | 1.0000 | 100.0% | +0.115 | 14.4 dB |
> | `fir257_s0.35` | 257 | 0.00% | 1.0000 | 100.0% | +0.508 | 9.3 dB |
> | `fir513_s0.05` | 513 | 0.00% | 1.0000 | 100.0% | -0.011 | 29.7 dB |
> | `fir513_s0.15` | 513 | 0.00% | 1.0000 | 100.0% | +0.167 | 18.0 dB |
> | `fir513_s0.35` | 513 | 0.00% | 1.0000 | 100.0% | +1.257 | 10.8 dB |
>
> **The attack never lands inside this bank.** EER holds at 0.00% and the catch rate at the
> shipped band holds at 100.0% on all 9 filters and on all 6 seen families individually. It holds
> at the aggressive end too: `fir257_s0.35` leaves a median signal-to-distortion of 9.3 dB, at
> which the colouration is audible, so within this attack class the perceptual budget runs out
> before the detector's margin does. The score shift is the mechanism and it runs the wrong way
> for the attacker: the median spoof log-odds moves **towards** synthetic, up to +1.257 on
> `fir513_s0.35`, because a convolutive filter adds artefact for the head rather than removing it.
>
> **Why the range was not pushed further.** The script's own comments give both bounds and
> neither was invented here: taps are set to 129, 257 and 513 because Malafide reports filter
> orders in the low hundreds to about 1k, and the off-centre energy is *swept* rather than picked
> because, in the script's words, a filter that colours the audio audibly is not an attack, it is
> a broken clip. The measured signal-to-distortion is published next to every row so a reader can
> pick the perceptual quality they would accept and read the result off at that quality. Pushing
> past 0.35 buys a number only below 9.3 dB, where the clip is no longer a usable attack.
>
> **What this result does NOT say, and it must be said in the same breath.** This is the black-box
> variant, random filters with no access to the detector. The published Malafide optimises the
> filter coefficients against the countermeasure with gradients, so **every number above is a
> lower bound on the damage the published attack would do, not an all-clear**.
> **A white-box gradient attack against the frozen XLS-R frontend remains unmeasured, and
> adversarial training is out of scope on this hardware, because it needs gradients through a
> 300M-parameter frontend and no GPU is available for it.** The attack against the Gate's
> sequential decision, as opposed to a single 4 s score, is also unmeasured. The entry's own
> citation stands as the reason to keep this open: "Escaping the Linearity Trap" (arXiv
> 2605.30366) locates the vulnerability in the transferable representation geometry of SSL models,
> which a frozen public frontend does not escape.
>
> Carried on two outward surfaces: a new `docs/QA_PREP.md` answer under "What if the attacker
> knows your detector?", which that file's own ownership line puts on S4 with accuracy and
> evaluation, and a short speaking version in
> `docs/SPEAKER_S4.md` section 5 with the rule that the answer never ends on the measured half.
> Both are generated from `docs/templates/` through `scripts/fill_numbers.py`, so no number here
> is hand-typed into a doc. Reproduce with `python eval/malafide.py`, about 10 minutes on the
> laptop CPU, no GPU and no network.

**G9. The competitive latency claim is sitting on the table unused.**
`eval/results/latency.json` gives RTF 0.046 on CPU. The Podonos benchmark of 14 August 2026 gives
Reality Defender at RTF 1.52, Resemble at 0.40, Hive at 0.34, Pindrop at 0.076. Pramaan on a
laptop CPU is faster than five of those seven and within a factor of two of the fastest.
*Why it matters:* criterion 7 and criterion 9, and it is free. It also lets S5 answer "how is this
different from Pindrop" with a number instead of a posture.
*Smallest step:* one slide row. State the comparison as latency only, never as accuracy, because
the Podonos accuracy column is English-only on a different corpus and mixing them would be exactly
the error this team already published about. Say that out loud on stage and it becomes a
credibility beat rather than a risk.
*Hardware:* none.

> **CLOSED 2026-09-14.** A new section 3b in `docs/templates/SPEAKER_S5.md`, because
> `docs/RUBRIC_MAP.md` puts competitive positioning and criterion 9 on S5. It carries the
> real-time-factor table (Corsound 0.035, **Pramaan 0.046**, Pindrop 0.076, Hive 0.34,
> Resemble 0.40, Reality Defender 1.52, all Podonos 14 August 2026), a spoken line for the
> stage, and the rule printed next to the table: **latency only, never mixed with accuracy**,
> with the reason given as this team's own 0.59%-versus-32.03% result rather than as a
> general principle.
> **The count in this entry and in section 1 was wrong and is corrected here.** Section 1 says
> "faster than six of the seven" and G9 says "faster than five of those seven". Neither is
> supported: a published real-time factor could be found for exactly **six** systems including
> Pramaan, so the defensible claim is that Pramaan is faster than **four of the five named
> commercial systems with a published RTF** and slower than one, and is the only one of the six
> that runs on the caller's own device with the network off. S5 carries an
> **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** note telling the speaker not to say "seven".
> An accuracy comparison is deliberately not added anywhere; that is G6 and it stays open.

### P2. If there is time left. Real value, larger surface.

**G10. The Warrant is in the narrative and not in the code, and the 2026 watermarking literature
has moved past AudioMarkBench.**
`docs/SPEAKER_S6.md` carries the AudioMarkBench line and the "may only ever lower risk" rule, but
`grep` over `pramaan/src` finds no warrant, watermark, attestation or C2PA code. Three newer
results strengthen the rule and add a failure mode it does not yet cover: "SoK: How Robust is
Audio Watermarking in Generative AI models?" (arXiv 2503.19176) reports bit recovery accuracy
below 0.6 under pitch shift for every scheme tested including AudioSeal; "Learning to Evade"
(arXiv 2606.22310) and "How Fragile Is Your Watermark?" (arXiv 2608.16566) show training-free
structural removal at high perceptual quality; and **"The Watermark Shortcut" (arXiv 2606.23335)
shows a watermark can be stamped onto a genuine recording**, which is the forgery direction rather
than the removal direction.
*Why it matters:* criterion 3, because prevention is half the PS title and the traceability table
in `RUBRIC_ATTACK.md` lists the Warrant against the PS's prevention line.
*Smallest step:* either implement a minimal attestation check that can only ever lower risk, with
the `assert` the parent repo's `warrant.py` already has, or remove the Warrant from the spoken
architecture and let the prevention ladder carry that line alone. Do not leave it half-claimed.
Add one sentence to S6: forgery matters as well as removal, and the monotone rule handles both,
because a stamped watermark on a genuine caller can only lower an already-low risk.
*Hardware:* laptop.

> **CLOSED 2026-09-14. Option (a): ported, minimally, with the assert.** Option (b), deleting
> the Warrant from the narrative, was rejected because the line it carries is the answer to a
> real question the detector cannot answer, that a bank's own IVR is synthetic on purpose and
> the question for a high-value action is authorization rather than synthesis. A half-claim
> was the defect; a deletion would have removed the answer with it.
> **What was ported:** `src/pramaan/warrant.py`, the parent repo's token path plus the
> monotone `apply()` and **its `assert`**, and `src/pramaan/stream.py` calls it on every
> scored hop. Pure Python, **no new dependency**, no torch, no AudioSeal.
> **What was deliberately not ported, and the docs say so:** the parent's `attest()` and
> `verify_audio()`, which load AudioSeal to recover a payload from the signal itself. That is
> a neural model and a new dependency in the pinned py3.14 stack, days before a demo, and
> `HONEST_LOG.md` already records what adding one costs. **Nothing outward claims Pramaan
> detects watermarks**, and S6 carries an explicit "do not say we detect watermarks".
> **Blast radius on the demo: none, and it is proven rather than asserted.** `attestation`
> defaults to `None`, `check(None)` returns `NONE`, and `apply()` on `NONE` is the identity
> function, so every demo call scores exactly as before. Verified end to end through the live
> pipeline on all 10 bundled samples: `p_passive` equals `p` on every one with no attestation,
> and with a valid attestation injected the score halves and never rises. The monotone
> invariant was fuzzed over 40,000 random (probability, status) pairs including a garbage
> status, and holds.
> **The literature sentence now covers both directions**, on S6 and on deck slide 6: removal
> (SoK arXiv 2503.19176, "Learning to Evade" arXiv 2606.22310, "How Fragile Is Your Watermark"
> arXiv 2608.16566) **and forgery** ("The Watermark Shortcut" arXiv 2606.23335, which stamps a
> watermark onto a genuine recording). Both directions are read against the rule explicitly:
> strip a warrant off and the caller loses a discount, which is the safe direction; forge one
> on and the best it buys is a lower score on a call that still cannot move money without the
> registered device. **A forgeable signal that could raise risk is a weapon handed to the
> attacker**, since a forged invalid warrant on a genuine customer would get them blocked.
> That asymmetry is why the sign of the rule is the design and not a caveat.
> Deck slide 6 needs a manual re-export.

**G11. The India-specific authorization primitive is CNAP under TRAI, and it is nowhere in the
artifacts.**
STIR/SHAKEN is a US primitive and roughly 35% of US calls carry full attestation, with
overseas-originated calls bypassing it, which is where most fraud calls come from. India's CNAP
rollout puts a verified caller name on the network layer.
*Why it matters:* criterion 1 and criterion 9. Naming the Indian regulatory primitive rather than
only the American one signals that the adoption path was thought about in the country the PS is
written for.
*Smallest step:* one line on the prior-art slide and one line in the adoption path: CNAP tells you
the line, Pramaan tells you the voice on it, and the two are complementary layers.
*Hardware:* none. **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** the current CNAP rollout status before
stating it as deployed.

> **CLOSED 2026-09-14.** Three lines, one per surface, all saying the same thing: **CNAP
> verifies the line, Pramaan verifies the voice on it, and they are complementary layers.**
> Prior-art slide 6 gains a bullet in `scripts/build_deck.py`. `docs/templates/SPEAKER_S6.md`
> gains a CNAP row in the what-is-on-the-slide table so the speaker has a one-line answer if a
> judge points at it. `docs/templates/SPEAKER_S5.md` gains it in the adoption path, at the
> telecom rung where it belongs, with the point that an operator who has deployed CNAP still
> has no answer to a cloned voice on a correctly attributed line.
> **The rollout status is not asserted anywhere.** S5 carries
> **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** on it explicitly and tells the speaker not to say
> it is deployed, only that it is the India-relevant primitive and that Pramaan is designed to
> sit above it whatever stage it is at. No CNAP date, percentage or coverage figure is printed
> anywhere, because none was verified.
> Slide 6 needs a manual re-export after `make deck`.

**G12. The generator-diversity claim has a soft spot a sharp judge can open.**
`results.json` `diversity_curve` mean EER by k is 8.1% at k=1, 12.8% at k=2, 13.2% at k=3, 13.8%
at k=4, 13.0% at k=5, 13.2% at k=6. **Mean EER does not improve with more families.** What
improves is the spread: at k=1 the range is 4.1% to 13.2% and at k=6 it is 13.2% to 13.2%. The
README states this correctly as "with few families the outcome depends on which you have" but
`SPEAKER_S6.md` says "we reproduced AUDETER on Indian languages", which is a stronger claim than
the curve supports.
*Why it matters:* criterion 2. This is the claimed original contribution and it is the one a judge
can attack with the team's own JSON.
*Smallest step:* restate it precisely as variance reduction rather than mean improvement, using
those six numbers, and say that a mean improvement would require more families than 6 or more than
7 random subsets per k. That restatement is stronger than the current wording because it is
exactly what the data shows.
*Hardware:* none, unless the team wants more subsets per k, which is minutes on cached features.

> **CLOSED 2026-09-14.** `docs/templates/SPEAKER_S6.md` no longer says "we reproduced AUDETER
> on Indian languages" anywhere. Three places rewritten: the AUDETER line in the
> what-is-on-the-slide table, point 1 of "what is actually ours", and the "what is new here"
> answer. The claim everywhere is now **variance reduction and nothing stronger**, stated with
> the six real numbers, and S6 gains a printed table of the whole curve: mean EER 8.1%, 12.8%,
> 13.2%, 13.8%, 13.0%, 13.2% at k = 1 to 6, against a spread that goes 9.1%, 21.5%, 16.2%,
> 12.0%, 12.0%, 0.0% wide.
> **One thing this pass found that G12 did not say**, and S6 now says it before a judge can:
> the 0.0% spread at k=6 is trivial, because there is only one way to choose all 6 of 6, so
> all 7 subsets at that k are the same subset. The row carrying real evidence is k=2 at 21.5%
> wide against 12.0% at k=4 and k=5. The trend is real and the last row overstates it, and
> saying that out loud is the version that survives a sharp judge.
> `scripts/fill_numbers.py` exports `div_k<k>_min`, `_max` and `_span` so no doc can quote a
> spread that is not in `results.json`. README, QA_PREP, RUBRIC_MAP and the deck already read
> correctly ("with few families the outcome depends on which you have") and are unchanged.

**G13. The challenge-response layer is unmeasured in Pramaan, and the parent repo's measurement of
it was negative.**
`pramaan/eval/` has no challenge evaluation. The parent repo's `eval/challenge_eval.py` measured
it and found that in the honest regime the challenge settled 60.5% of deferred calls while getting
**47.8% of them wrong** (`HONEST_LOG.md`, 2026-09-03, B1). `docs/QA_PREP.md` currently says "we
measured the scoring half", which is true of the parent repo and not of this one. Separately,
D-CAPTCHA++ (arXiv 2409.07390) demonstrates that a challenge-response deepfake protocol falls to
transferable imperceptible adversarial attack, so the mechanism is not attack-proof either.
*Why it matters:* criterion 3 and 6. Prevention is half the title and its middle rung has no
number in this repo.
*Smallest step:* carry the parent repo's number explicitly with its provenance, or re-run the
evidence-fusion measurement here. Either way, say on stage that the challenge amplifies a detector
that can see the attack and cannot rescue one that cannot, which is why the device push is the
rung that does not depend on the detector at all. That sentence is already true and already
evidenced.
*Hardware:* laptop.

> **CLOSED 2026-09-14.** Carried with provenance rather than re-run. Re-running it here would
> mean porting `FusionRule` and a challenge evaluation into a repo that has neither, days
> before a live demo, to reproduce a number that is already measured and already negative.
> The misattribution is the real defect and it is fixed.
> `docs/QA_PREP.md` and `docs/TEAM_GUIDE.md` now both say plainly that **Pramaan has no
> challenge measurement and `eval/results.json` carries no challenge number**, and that the
> scoring half was measured in the parent repository `2026-sih-26104-kempelen`,
> `eval/challenge_eval.py`, logged in its `HONEST_LOG.md` on 2026-09-03 under B1, at commit
> `1f2f032`. Anyone saying "we measured it" about this repo is wrong and a judge who greps
> will find nothing.
> The parent's numbers are carried in full, including the unflattering row, with the Wilson
> intervals the parent already printed. Honest deployment regime, same-corpus, shipped
> detector, pooled over seven channels: challenge settles **60.5% of deferred calls
> [49.3, 70.8]** and gets **47.8% of them wrong [34.1, 61.9]**, against a passive committed
> error of 47.93%. The two regimes where the detector has signal are carried too, 78.9%
> settled at 10.5% error in domain and 68.7% at 7.1% cross-corpus, because those three rows
> together are what make the finding legible rather than just bad.
> The sentence is now printed in both docs: **the challenge amplifies a detector that can
> already see the attack and cannot rescue one that cannot**, because a second observation
> from a blind detector is two blind observations and not one sighted one, **which is why the
> device-approval rung does not depend on the detector at all** and is the rung that blocks
> the transfer in the demo. PITCH's 56.0% to 88.7% stays marked as theirs, on their data.

**G14. The microphone and replay channel is in the dataset and not in the results.**
`results.json` `dataset.extra_channels` lists `replay_mic` and `replay_mic_v0.4`, and
`docs/RUNSHEET.md` records that the Chatterbox clone played through the microphone reads as human.
That is a measured failure mode with no row in the grid, and it is the exact configuration a judge
is most likely to trigger by asking to test it live.
*Why it matters:* criterion 6. It is better to have this cell printed and failing than to discover
it on stage.
*Smallest step:* score the existing replay-mic clips and add a row. Publish the failing cell, which
is this project's whole posture anyway.
*Hardware:* laptop.

> **CLOSED 2026-09-14.** New `replay_mic` protocol in `eval/experiments.py`, `results.json`
> `replay_mic`, and rows in README, `SPEAKER_S4`'s hard-cells table and `SPEAKER_S3`'s
> microphone section.
> **Two rows per channel, because one alone would have been misleading.** `ship()` trains on
> every condition that is not "none", replay rows included, at `REPLAY_WEIGHT = 30`, so the
> shipped head's number on these clips is **in sample**. It is published, labelled as
> in-sample, and never quoted as generalisation. The second row retrains with every replay
> row removed, so the **channel** is held out; the recordings are not, since their clean and
> codec versions stay in training, which makes it a channel-shift measurement and the docs
> say so rather than implying a held-out-clip number.
>
> | channel | clips | shipped (in sample) | channel held out | clones called synthetic | genuine called synthetic |
> |---|---|---|---|---|---|
> | replay_mic | 99 (50 genuine, 49 clones) | 2.0% | **16.2%**, 95% CI 9.5% to 25.0% | 77.6% | **14.0%** |
> | replay_mic_v0.4 | 100 (50 genuine, 50 clones) | 2.0% | **10.0%**, 95% CI 4.2% to 18.2% | 86.0% | 6.0% |
>
> **The false-alarm column is the finding, not the EER column.** 14.0% of genuine speech
> played through a speaker and recorded back is called synthetic by the channel-held-out head,
> against 0.9% pooled on the telephony grid. A room is a channel, and it is the worst one this
> project has measured. That is now printed.
> No gate replay: replay rows are cached at the 4.0 s prefix only and the Gate needs three
> stable updates before it may commit, so there is nothing to replay. The decision rates above
> are the band applied to the full clip at the fallback channel the live path would choose for
> a line it has no band for, G.723.1 6.3 kbps (`src/pramaan/stream.py`), which is recorded in
> `replay_mic.band_used` rather than left implicit.

**G15. Speaker similarity is a frontend cosine, and cross-session consistency is a PS Key
Component that is scoped out.**
Already flagged in `GAPS.md` for the parent repo. It applies to Pramaan too: the PS names
"cross-session consistency checks comparing ongoing call features against historical genuine
samples" as a Key Component, and the SASV line of work is the named academic frame for fusing
speaker verification with anti-spoofing.
*Why it matters:* criterion 3, where the traceability table is scored line by line against the PS.
*Smallest step:* keep it scoped out, but say the exclusion out loud with the reason (no enrolled
speakers available, and enrolment is a deployment-side dataset, not a model), and name SASV as the
frame it would use. A stated exclusion reads as scope control.
*Hardware:* none for the statement. An ECAPA speaker embedding would be a new dependency in a
pinned stack that `HONEST_LOG.md` warns against disturbing.

> **CLOSED 2026-09-14.** `docs/RUBRIC_MAP.md` gains a section, "What the PS names that we
> deliberately did not build", where criterion 3 is scored line by line. It quotes the PS Key
> Component verbatim, states that Pramaan does not implement it, and gives the reason as **the
> dataset, not the model**: the check needs enrolled speakers, FLEURS gives one recording per
> speaker rather than a history per speaker, and standing enrolment up from two clips of the
> same FLEURS speaker would be a demonstration rather than a measurement.
> **SASV** is named as the academic frame it would use, with two points a judge can be handed:
> the PS's own "where available" already treats the history as optional, and the check answers
> a different question from ours. Cross-session consistency asks "is this the same person as
> last time"; Pramaan asks "is this a person at all", which is the question answerable on a
> first call from a number with no history, which is how the fraud actually arrives. The
> pinned-stack dependency cost is named too.
> The AMR-WB and EVS absence is folded into the same section so every stated exclusion sits in
> one place, plus the instruction for saying either on stage: name the exclusion, give the
> reason, name the frame, stop, do not apologise.

**G16. ~~The reverse cloner direction is not measured in the per-channel streaming table.~~ There
is no reverse direction any more. There are nine, and until 2026-09-15 the streaming table
carried none of them.**
This is one of the four gaps section 0 said it would not restate, because `GAPS.md` already
carries it. Restated here because reading the current code showed the gap is not the one the
sentence describes. `GAPS.md` was written on 2026-09-04 against the parent repo, which had two
cloners, so "the primary direction" meant `eval/per_channel.py` holding out `xtts_v2` and "the
reverse" meant `eval/train_combined.py --held-out-cloner freevc24`. Pramaan is a rebuild with
**8 trained generator families plus the held-out 2025 cloner**, so there is no pair and no
reverse: there are **9 leave-one-generator-out directions**. `generator_matrix` already carries
all 9 on full 4 s clips, per codec, which is the Honest Matrix the old note said carried both
directions. The streaming table did not carry one of the nine. Its two arms were `seen`, a head
trained on all 8 families and then replayed on those same 8, and `unseen`, the same head replayed
on Chatterbox. The first is **in sample by construction** and was being published as
"committed-call error 0.0%"; the second is one direction out of nine and is not a direction over
a trained family at all, since Chatterbox is never in training under any protocol.
*Why it matters:* criterion 5 and criterion 6. The single sentence the deck and README used to
make about streaming behaviour, "committed-call error 0.0% on the clean channel", was measured on
generators the replayed head had trained on. A judge who asks "is that held out?" gets the answer
no, and the honest held-out version of that number was not computed anywhere.
*Smallest step:* one head per direction on the existing cached features, exactly `streaming`'s
recipe minus the held-out family, band still derived from bona fide calibration clips alone.
*Hardware:* laptop. Features are already cached. Under a minute per direction.

> **CLOSED 2026-09-15.** `eval/experiments.py` gains `streaming_leave_one_out`, which trains a
> separate head per direction and replays the Gate on the held-out family against held-out
> genuine speech, on all 7 channels. `results.json` carries `streaming_leave_one_out`, its
> clean-channel Wilson intervals sit in `confidence.streaming_leave_one_out_clean`, and the
> README carries the table. Two correctness checks were run before the numbers were published:
> the refactor that `streaming` and `streaming_leave_one_out` now share leaves every existing
> `streaming` value byte-identical, and the Chatterbox direction of the new protocol reproduces
> the already-published `streaming.gate_replay_by_channel.*.unseen` row exactly on all 7
> channels, which it must, because holding out Chatterbox is the one direction whose training
> set is the same as the old table's.
> **What it measured.** On the clean channel the committed-call error runs from **0.0%** (Apple
> on-device TTS, Kokoro-82M, eSpeak NG, Piper) to **45.1%** (EnCodec resynthesis, 95% CI 39.0%
> to 51.4%, on 127 held-out clones), against the **0.0%** the in-sample arm reports. Chatterbox
> is **11.6%** (95% CI 7.3% to 17.7%). The worst false-alarm direction is holding out Meta MMS
> at **3.94%** (95% CI 1.69% to 8.89%) against 0.00% in sample. EnCodec being the worst is the
> expected result and not a surprise: `generator_matrix` already publishes 24.4% clean EER for
> that same family, and what is new is that the Gate **commits** on those clips rather than
> deferring, so the ranking error becomes a decision error.
> **A second finding, which was not the one being looked for.** Coverage on the six codec
> channels is not a channel property. Only bona fide speech, `xtts_v2` and `freevc24` are cached
> at more than one prefix length on a codec channel; the other six families are cached at 4.0 s
> alone, so the Gate cannot reach its three stable updates and **42 of the 63** direction-by-
> channel cells cannot commit on the held-out clones at all. Those cells are marked
> `gate_can_commit_on_held_out: false` rather than published as a 0% result. The README sentence
> that explained codec coverage as "clean and Opus 24k are cached at eight prefix lengths and the
> other five at four" was therefore incomplete, and it is corrected: the binding constraint is
> the generator's cache, not the channel's. `gate_replay` now also reports coverage split into
> its genuine and spoof halves so this cannot be misread again. Closing it properly means
> caching the remaining six families at the four codec prefixes, which is a `build_features.py`
> run and not a code change, and it is left open.

**G17. IndicF5 is the right instrument for the Tamil and Telugu held-out cloner, it does support
both languages, and it is blocked on one thing that no amount of compute on this laptop can
move: the weights are gated and this machine has no HuggingFace account attached to it.**
G5's second correction named IndicF5 as the target and left two things
**[TO MEASURE]**: whether the `f5_tts` dependency stack installs against the pinned py3.14
environment, and by implication whether the model is reachable at all. Attempted 2026-09-15.
Both are now measured. One is a hard stop for a human, the other is a hard stop for the pinned
venv, and neither is a reason to skip the entry quietly.
*Priority:* this sits under P2 only because the list is numbered in the order the gaps were
found. It is the continuation of **G5 in P1** and should be read at P1 priority. G16, directly
above it, is closed and its priority no longer matters.

> **STOPPED 2026-09-15, with the blocker measured rather than assumed.** Nothing was faked and
> no Tamil or Telugu number was produced. What was established, in order:
>
> **1. The language question is settled, and the answer is yes.** The model card at
> `ai4bharat/IndicF5` lists **"Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi,
> Odia, Punjabi, Tamil, Telugu"**, and the HuggingFace model API carries the tags `ta` and `te`
> alongside `hi`. So "no Tamil or Telugu support after all" is **not** the blocker. Also worth
> recording because it contradicts G5's second correction on one point: `README.md` now returns
> **HTTP 200 unauthenticated**, where on 2026-09-14 it returned `Access to model
> ai4bharat/IndicF5 is restricted`. The card is readable now. The weights are not.
>
> **2. The weights are still gated, and this machine has no token.** Fetching
> `resolve/main/model.safetensors` unauthenticated returns, verbatim:
>
> ```
> Access to model ai4bharat/IndicF5 is restricted. You must have access to it and be
> authenticated to access it. Please log in.
> ```
>
> and the model API still reports `"gated": "auto"`. There is no token anywhere on this
> machine to fix that with: `huggingface_hub.get_token()` returns `None`, there is no
> `~/.cache/huggingface/token` and no `~/.huggingface` directory, `HF_TOKEN` is unset, and
> `HfApi().whoami()` raises
> `LocalTokenNotFoundError: Token is required to call the /whoami-v2 endpoint, but no token
> found`.
> *What unblocks it, and only a human can do it:* log in to a HuggingFace account, open the
> model page, click through the terms once (`gated: auto` means a click, not an email and a
> reviewer, which is exactly why G5 ranked it above SEA-Spoof), then `hf auth login` on this
> machine. Nothing in this repo can do that step and nothing should pretend to.
>
> **3. Even with a token, it cannot go in the pinned venv, and now there is a specific reason
> instead of a suspicion.** IndicF5's `requirements.txt` and `setup.py` (package name `f5_tts`,
> fetched from `AI4Bharat/IndicF5`) pin **`numpy<=1.26.4`** and **`transformers<4.50`**. The
> pinned environment is **Python 3.14.6, numpy 2.5.2, transformers 5.16.1, torch 2.14.0**.
> numpy 1.26.4 publishes wheels for **cp39, cp310, cp311 and cp312 only**; there is no cp314
> wheel, so satisfying that pin inside `../.venv` means either building numpy 1.26.4 from
> source against a Python it predates by two releases, or downgrading numpy and transformers
> underneath torch and scikit-learn. `HONEST_LOG.md` already forbids the second and the first
> is not a thing that works. **The side-venv pattern is therefore confirmed as the only route**,
> as G5 predicted: `~/.venvs/chatterbox` is python 3.12 for exactly this reason, and
> `/opt/homebrew/bin/python3.12` is present, which is a version numpy 1.26.4 does ship a wheel
> for. That venv was not built, because building it costs a multi-gigabyte torch download for a
> model whose weights cannot be fetched yet, and disk was measured at **12 GB free on `/`**.
>
> **4. Everything on this side of the blocker is already in place, which is why this is worth
> resuming the moment a token exists.** `data/manifest_all.csv` holds **170 Tamil and 170 Telugu
> FLEURS bona fide parents**, the same recordings the Chatterbox Hindi test cloned, so the
> same-speaker same-sentence matched-pairs protocol can run unchanged the moment the cloner
> does. The generation script pattern is `scripts/build_chatterbox.py` behind
> `scripts/chatterbox_run.sh`, and `scripts/add_family.py` already exists to fold a new family
> into the manifest and the feature cache.
>
> **Where exactly this stopped:** at the token. Steps 1 and 3 are done and will not need redoing.
> The next session starts by checking whether a token is present, and if it is, builds
> `~/.venvs/indicf5` on python 3.12, pulls the 1.4 GB checkpoint, clones the 340 Tamil and
> Telugu parents, and runs it through `scripts/add_family.py`, `make features`, `make eval`.
> Until then `docs/QA_PREP.md` is still correct to call IndicF5 a roadmap item rather than a
> result, and no outward artifact claims a Tamil or Telugu held-out cloner number.

---

## 4. Do NOT chase

**Do not fine-tune XLS-R.** It would cost the no-GPU story, which is simultaneously the
feasibility answer (criterion 5), the scalability answer (criterion 7) and the privacy answer
(criterion 3, on-device inference). Pascu et al., Interspeech 2024, is already the published
justification for freezing it, and `docs/QA_PREP.md` already answers the question. Nothing found
in this research pass changes that.

**Do not chase an ASVspoof 5 or RADAR leaderboard number.** Those are English or
cross-domain-English benchmarks trained at a scale this hardware cannot reach, and a mid-table
entry would replace a differentiated Indic story with an undifferentiated English one.

**Do not build or copy SATYAM.** It is the best Indic number in the literature at 3.27% EER, and
it uses a frozen Qwen2-7B decoder plus Whisper and TRILLsson encoders. It does not run on this
laptop and it destroys the on-device claim. Cite it as the Indic state of the art, name it as the
thing Pramaan is behind on absolute accuracy, and say why the architecture choice is different.
Being able to name what beats you is a criterion-2 point.

**Do not claim streaming detection as novel.** rs-10257178 is already named as prior art, and as
of 2026 it is also a shipped commercial feature: Hydaway added streaming audio detection to
RealityChek in July 2026 and Modulate advertises near-real-time detection on live calls. The
defensible claim is not "we stream", it is "we stream, on-device, in Indian languages, over real
telephony codecs, and we publish where it breaks".

**Do not put Pramaan's EER next to the Podonos accuracy column.** Different corpus, English only,
different metric. Latency versus latency is a fair comparison and accuracy versus accuracy is not.
This is the same class of error as the 0.59% headline, and the team has already published a
document explaining why it is an error. Repeating it on stage would be self-inflicted.

**Do not adopt watermarking as a positive signal.** Every 2025 and 2026 result found in this pass
makes the case worse rather than better, and "The Watermark Shortcut" (arXiv 2606.23335) adds
forgery to removal. The monotone rule, that a warrant may only lower risk, is the correct design
and it now has four papers behind it instead of one.

**Do not retrain on IndicSynth or MLAAD at scale for a "production" claim.** Both are
non-commercial. `GAPS.md` and `README.md` already carry this rule. "Production ready" never
appears on the same slide as either.

**Do not attempt adversarial training.** It is the standard defence, it needs gradients through a
300M-parameter frontend, and it is a GPU workload. Measuring an attack (G8) is cheap and
defensible. Defending against it is not, on this hardware, in this time. G8 is now measured and
the black-box attack did not land, which strengthens the case for not chasing the defence: there
is no measured vulnerability in that attack class to defend against yet, and the honest next step
is the white-box measurement, not the training run.

**Do not build an actual blockchain.** The SHA-256 hash chain in `src/pramaan/ledger.py` is the
honest version and the QA answer for it is already written. A token would not make a decision more
auditable.

**Do not present the corpus-shortcut finding as unprecedented.** It is this team's best original
result and it should stay the centrepiece, but the field has adjacent published work: LRLspoof
(arXiv 2603.02364) shows language identity acting as an independent domain shift, "Circumventing
shortcuts in audio-visual deepfake detection datasets" (arXiv 2412.00175) shows a silence
classifier reaching over 98% on FakeAVCeleb and AV-Deepfake1M, HQ-MPSD (arXiv 2512.13012) builds
an artifact-controlled multilingual protocol, and "The Watermark Shortcut" releases WASP, a paired
corpus with matched clean-versus-watermarked pairs. **Name these on stage in the same breath as the
finding.** The claim that survives contact with a knowledgeable judge is narrower and stronger:
this team ran the matched-pairs control on Indian-language speech, against a 2025 cloner, on a
system it was about to demo, and published the cell where it failed. That is a real claim. "Nobody
has done this" is not.

---

## 5. Appendix: if there were a GPU or a budget

**Marked optional and stretch. Read the tradeoff first.**

The tradeoff is not close. "It runs on a laptop with no GPU" currently carries three of the ten
criteria at once (feasibility, scalability, privacy under relevance) and it is the only axis on
which Pramaan structurally beats seven named commercial systems, all of which are cloud APIs.
Buying hardware does not improve the demo and it weakens the story if the demo then needs it.
**The correct framing, if hardware is bought, is that training moves off the laptop and inference
never does.** That is the only version of this that keeps the differentiator intact, and it should
be said in exactly those words.

With that constraint, in rough order of value per rupee:

| Stretch item | What it buys | What it costs the story |
|---|---|---|
| Rented A100/H100 for **training data generation only**, not inference | 30 to 50 generator families instead of 6, which is the lever the diversity curve says reduces variance, and enough clips to move the unseen-cloner EER off 13.2% | Nothing, as long as the shipped model still runs at RTF 0.046 on the laptop CPU and the demo runs offline |
| Paid cloner API credits (ElevenLabs, PlayHT, MiniMax) | Closes G7 properly: the cloners attackers actually pay for, in the grid, under the same-speaker same-sentence protocol | Nothing. This is the highest value per rupee on the list and the cheapest |
| Disk, external or internal | Unblocks LRLspoof, IndicSynth at scale and IndicF5, all of which `GAPS.md` records as disk-blocked since 2026-09-03 | Nothing. Arguably this belongs in P1, not the appendix |
| GPU for the white-box half of G8, measurement before defence | G8's black-box sweep found nothing at 9 filters, so the open question is the gradient attack, not the defence. A GPU measures that first; adversarial training only becomes worth costing if it lands | Nothing, for the measurement. For the training run: real risk. If the defended model no longer runs on CPU, the feasibility and privacy answers both weaken |
| Fine-tuning XLS-R end to end | Possibly a better in-domain number | High. Contradicts the Pascu justification the team gives on stage, contradicts the 2,049-parameter architecture answer, and Pascu et al. report frozen-frontend generalisation beating RawNet2's 25M trainable parameters out of domain, 30.9% to 8.8% mean OOD EER. This is the one to refuse |

**One honest sentence for the roadmap slide, if hardware is raised in Q&A:** the bottleneck is
training data and disk, not compute for inference, and the thing money buys first is more
generator families and the paid cloners, not a faster model.

---

## Sources

Academic:
[SZU-AFS, ASVspoof 5](https://arxiv.org/pdf/2408.09933) ·
[AASIST3, arXiv 2408.17352](https://arxiv.org/abs/2408.17352) ·
[ASVspoof 5 overview, arXiv 2408.08739](https://arxiv.org/pdf/2408.08739) ·
[Wav2DF-TSL, arXiv 2509.04161](https://arxiv.org/pdf/2509.04161) ·
[RADAR Challenge 2026, arXiv 2605.09568](https://arxiv.org/pdf/2605.09568) ·
[Indic-CodecFake and SATYAM, arXiv 2604.19949](https://arxiv.org/html/2604.19949v1) ·
[LRLspoof, 66 languages, arXiv 2603.02364](https://arxiv.org/html/2603.02364) ·
[XMAD-Bench, arXiv 2506.00462](https://arxiv.org/pdf/2506.00462) ·
[HQ-MPSD, arXiv 2512.13012](https://arxiv.org/pdf/2512.13012) ·
[First Greeting "Hi!", arXiv 2601.19573](https://arxiv.org/html/2601.19573) ·
[rs-10257178, Semjonovs, streaming sequential decision](https://www.researchsquare.com/article/rs-10257178/v1) ·
[RawBoost, arXiv 2111.04433](https://arxiv.org/abs/2111.04433) ·
[Malafide, arXiv 2306.07655](https://arxiv.org/pdf/2306.07655) ·
[Escaping the Linearity Trap, arXiv 2605.30366](https://arxiv.org/pdf/2605.30366) ·
[Transferable Adversarial Attacks on ADD, WACVW 2025](https://openaccess.thecvf.com/content/WACV2025W/MAPA/papers/Farooq_Transferable_Adversarial_Attacks_on_Audio_Deepfake_Detection_WACVW_2025_paper.pdf) ·
[Adversarial Attacks on ADD benchmark, arXiv 2509.07132](https://arxiv.org/html/2509.07132) ·
[UAP vs deepfake audio and vocoder fingerprint detectors](https://doi.org/10.3390/fi18070344) ·
[D-CAPTCHA++, arXiv 2409.07390](https://arxiv.org/abs/2409.07390) ·
[AudioMarkBench, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5d9b7775296a641a1913ab6b4425d5e8-Paper-Datasets_and_Benchmarks_Track.pdf) ·
[SoK audio watermarking, arXiv 2503.19176](https://arxiv.org/pdf/2503.19176) ·
[Learning to Evade, arXiv 2606.22310](https://arxiv.org/html/2606.22310) ·
[How Fragile Is Your Watermark, arXiv 2608.16566](https://arxiv.org/abs/2608.16566) ·
[The Watermark Shortcut, arXiv 2606.23335](https://arxiv.org/html/2606.23335) ·
[Circumventing shortcuts, arXiv 2412.00175](https://arxiv.org/html/2412.00175v1) ·
[SSL benchmark for ADD, arXiv 2603.01482](https://arxiv.org/html/2603.01482v1)

Commercial and policy:
[Podonos audio deepfake detection benchmark, 14 Aug 2026](https://www.podonos.com/blog/audio-deepfake-detection-benchmark-the-production-bar-moves-to-four) ·
[Resemble AI 2026 benchmark writeup](https://www.resemble.ai/resources/audio-deepfake-detection-benchmark-results-how-8-systems-performed-in-2026) ·
[Hydaway RealityChek streaming audio detection, Jul 2026](https://www.biometricupdate.com/202607/hydaway-introduces-real-time-enterprise-audio-deepfake-detection) ·
[Modulate deepfake detection tools](https://www.modulate.ai/blog/best-deepfake-detection-tools) ·
[AI voice deepfake fraud India 2026, CNAP and TRAI context](https://caller.digital/blog/ai-voice-deepfake-fraud-caller-trust-india-2026) ·
[Bachao.AI deepfake detection India](https://www.bachao.ai/deepfake-detection) ·
[HyperVerge deepfake banking fraud, India](https://hyperverge.co/blog/deepfake-banking-fraud/)
