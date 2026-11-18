# DATA_PLAN

> Written 2026-09-14. Execution plan for training-data acquisition and generation ahead of a
> rented A100, for the National Level SIH round.
>
> **The one sentence this whole plan exists to protect, taken from `docs/SOTA_GAP_ANALYSIS.md`
> section 5: training moves off the laptop, inference never does.** Every item below is either
> data acquisition or data generation. Nothing below changes what the shipped model needs at run
> time. The shipped head stays at 2,049 trainable parameters on a frozen frontend, RTF 0.046 on
> the M4 CPU (`eval/results/latency.json`), and the demo stays offline.
>
> Rules this file obeys, same as `docs/RUBRIC_ATTACK.md` and `docs/SOTA_GAP_ANALYSIS.md`:
> no claim is made with an adjective, every number names the file, the paper, the search result
> or the command it came from, and anything not verified on this machine is marked
> **[TO MEASURE]**, **[ESTIMATE]** or **[UNVERIFIED, NEEDS A HUMAN TO CHECK]**.
> No em dashes anywhere in this file.
>
> **Scope, negative.** This plan does NOT fine-tune the frontend, does NOT move inference to a
> GPU, does NOT touch `src/pramaan/`, `eval/`, `docs/NUMBERS.json`, `README.md`, the speaker
> scripts or `ppt/`. Those are owned by the concurrent G1/G2 narrowband-calibration work.

---

## 0. Read this first: the number that gates everything

```
$ df -h /System/Volumes/Data          # run 2026-09-14, this machine
Filesystem      Size    Used   Avail Capacity
/dev/disk3s5   228Gi   193Gi   274Mi   100%
```

**274 MB free. The machine is full.** The same command returned `1.0Gi` earlier in the same
session, so the figure is moving and is not stable enough to plan against. `GAPS.md` has carried
the disk blocker as open since 2026-09-03, when a clean isolated venv at `/tmp/kv-cloner` died on
`OSError: [Errno 28] No space left on device` after consuming 1.5 GB. That blocker was never
closed and the machine is now in a worse state than it was then.

**Nothing in Track A can start until a human runs `df -h` and frees space.** The reclaim
candidates are in section 1.1. Every disk figure in this document is measured with `du -sh` on
this machine on 2026-09-14 unless marked otherwise.

The second gating number, for cost: a 4 second clip at 16 kHz mono PCM16 is **128,044 bytes**,
measured on `data/clips/spoof/freevc24/spoof_freevc24_00106.wav`. Every disk estimate below is
that number times a clip count. Codec conditions are NOT stored: `src/pramaan/channels.py`
applies all 7 conditions at feature-extraction time via `apply_channel()`, so the 7-condition
grid costs zero extra disk on the clip side.

---

# TRACK A: prep now, on this laptop, zero GPU

## A1. Free the disk. This is item zero and it blocks everything else.

### 1.1 Reclaim candidates, measured

| Path | Size | Safe to remove | Note |
|---|---|---|---|
| `~/Downloads` | **8.3 GB** | Human decides | Largest single reclaim on the machine. Not project data. |
| `~/.cache/whisper` | **1.9 GB** | Likely | OpenAI whisper checkpoints. Nothing in `pramaan/src` imports `whisper`. **[TO MEASURE]** grep before deleting. |
| `~/.cache/huggingface/hub/models--ResembleAI--chatterbox` | **6.0 GB** | Judgement call | The A2 clips are already generated and sit in `data/clips/a2_cloner` (4.9 MB) and `data/clips/chatterbox` (3.8 MB). Deleting the weights frees 6.0 GB but makes A2 non-reproducible without a re-download. **Recommendation: move to an external disk, do not delete.** |
| `~/.cache/huggingface/hub/models--Systran--faster-whisper-small` + `--base.en` | 605 MB | Likely | Same check as above. |
| `~/.cache/hyperframes` | 196 MB | Yes | Unrelated to this project. |
| `~/.cache/prisma` | 56 MB | Yes | Unrelated to this project. |
| `~/.cache/huggingface/hub/models--BAAI--bge-small-en-v1.5` | 128 MB | Yes | Text embedding model, unrelated. |
| `~/.cache/huggingface/hub/models--depth-anything--Depth-Anything-V2-Small-hf` | 95 MB | Yes | Vision model, unrelated. |
| `~/.cache/huggingface/hub/models--cross-encoder--ms-marco-MiniLM-L6-v2` | 88 MB | Yes | Reranker, unrelated. |

**Reclaimable without touching any project artifact: roughly 10.9 GB** (Downloads 8.3 + whisper
1.9 + hyperframes 0.196 + prisma 0.056 + bge 0.128 + depth-anything 0.095 + cross-encoder 0.088,
summing to 10.76 GB, rounded). With Chatterbox moved to external storage rather than deleted,
16.8 GB.

### 1.2 Do NOT delete these. They are load-bearing.

| Path | Size | Why it must stay |
|---|---|---|
| `~/.cache/huggingface/hub/models--facebook--wav2vec2-xls-r-300m` | **2.4 GB** | The frozen frontend. Deleting it breaks every experiment in the repo and the offline demo. |
| `~/.cache/huggingface/hub/datasets--google--fleurs` | 1.3 GB | The bona fide source for all 510 parent recordings. |
| `~/.cache/huggingface/hub/datasets--vdivyasharma--IndicSynth` | 1.5 GB | Training spoof source for the xtts_v2 and freevc24 families. |
| `models--facebook--encodec_24khz` | 89 MB | Generates the `samecorpus` matched pairs, the project's headline finding. |
| `models--facebook--mms-tts-hin` / `--tam` / `--tel` | 417 MB total | The `mms_vits` family, 510 clips in `data/manifest_all.csv`. |
| `models--hexgrad--Kokoro-82M` | 314 MB | The `kokoro` family, 170 clips. |

### 1.3 Do NOT touch `pramaan/eval/` this week

`pramaan/eval/` is **1.0 GB**, of which the feature caches are:

| File | Size |
|---|---|
| `eval/results/features.npz` | 427.1 MB |
| `eval/results/features_interim.npz` | 321.4 MB |
| `eval/results/features_prefix_legacy.npz` | 262.9 MB |
| `eval/results/features_samecorpus_legacy.npz` | 51.9 MB |
| `eval/results/features_legacy.npz` | 51.4 MB |

The three `*_legacy*` and `*_interim*` files total **687.6 MB** and look reclaimable.
**They are not this plan's to reclaim.** A separate agent is mid-edit on `eval/` for the G1/G2
narrowband calibration work, and `experiments.py` and `results.json` both carry a 2026-09-14
mtime. Re-deriving a deleted feature cache costs an XLS-R forward pass over the whole dataset.
Revisit after the G1/G2 work lands and a human has confirmed which caches the shipped
calibration still reads.

### 1.4 There is no external volume on this machine

```
$ ls /Volumes/
Macintosh HD
```

If the A100 plan proceeds, an external SSD is a real purchase line item and it is the cheapest
item in the whole plan. `SOTA_GAP_ANALYSIS.md` section 5 already ranks it: "Disk, external or
internal. Unblocks LRLspoof, IndicSynth at scale and IndicF5, all of which `GAPS.md` records as
disk-blocked since 2026-09-03. Nothing. Arguably this belongs in P1, not the appendix."
**[UNVERIFIED, NEEDS A HUMAN TO CHECK]** current retail price of a 1 TB external NVMe SSD in
India. No price is asserted here because none was looked up.

---

## A2. LRLspoof: the gap doc's plan does not survive contact with the actual hosting

`SOTA_GAP_ANALYSIS.md` G5 says: "pull only the Tamil and Telugu partitions, cap at a few hundred
clips to fit the disk". That instruction assumed per-language downloadable partitions.
**Checked on 2026-09-14 against the HuggingFace dataset card, that is not how it ships.**

### 2.1 What was found

Source: [huggingface.co/datasets/MTUCI/LRLspoof](https://huggingface.co/datasets/MTUCI/LRLspoof),
fetched 2026-09-14, and the paper HTML at
[arxiv.org/html/2603.02364v2](https://arxiv.org/html/2603.02364v2), fetched 2026-09-14.

| Fact | Value | Source | Consequence |
|---|---|---|---|
| Total size on disk | **452 GB** | HF dataset card | Does not fit on this machine under any reclaim scenario in section 1.1. |
| Packaging | Multi-part tarball, `lrl_spoof.tar.gz.part_*`, extracted as `<language>/<tts_model>/<file>.wav`. Access is by tarball extraction, **not** `load_dataset`. | HF dataset card | `streaming=True` per-language selection, the trick `research/03_data.md` uses for IndicSynth's 845 GB, **does not apply here**. |
| Content | 1,304,455 TTS utterances, **spoof only, no bona fide samples** | HF dataset card | See 2.2. This is the important one. |
| Telugu volume | **22.12 hours, 1 supported synthesizer** | Paper, Table 2 | One synthesizer is not a held-out-cloner grid. It is one cell. |
| Tamil volume | **Not present in Table 2** | Paper, Table 2 | **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether Tamil is in the corpus at all. The abstract says 66 languages and the gap doc asserts Tamil; the per-language table as fetched does not list it. |
| Licence | **MIT** on the HF card, **CC BY 4.0** in the paper | HF card vs paper | Two different licences for the same artifact. A human must resolve this before any slide names a licence. |
| Metadata | `data/labels.parquet`, utterance IDs and labels | HF dataset card | Small. Worth pulling on its own to confirm Tamil and Telugu clip counts before committing to 452 GB. |

### 2.2 The finding that changes G5's value: LRLspoof is spoof only

A spoof-only corpus cannot be evaluated on its own. The bona fide side has to come from
somewhere else, and that is **exactly the confound this team already measured and published**.
`HONEST_LOG.md`, 2026-09-03, A1: the shipped detector scored 0.59% EER when bona fide came from
FLEURS and spoof came from IndicSynth, and 32.03% EER when the matched-pairs control forced both
sides to come from the same FLEURS recording. The score medians settled it: cross-corpus spoof at
+0.01, same-corpus spoof at -9.38, cross-corpus bona fide at -11.14. "The detector had learned
where the audio came from."

**Therefore: LRLspoof clips scored against FLEURS bona fide clips reproduce the A1 error.** Any
Tamil or Telugu EER produced that way is a cross-corpus number and must be reported as one, with
the A1 caveat printed next to it, or not reported at all. This is a correction to
`SOTA_GAP_ANALYSIS.md` G5, which reads as if LRLspoof closes the Tamil and Telugu gap cleanly. It
does not. It closes a weaker version of it.

### 2.3 Decision, and it is a decision not a download

**Do not start a 452 GB pull.** At a sustained 50 Mbit/s that is **[ESTIMATE]** 20.1 hours of
download (452 GB x 8 = 3,616 Gbit, divided by 0.05 Gbit/s = 72,320 s), and at 100 Mbit/s roughly
10 hours, before any disk is available to land it on. The ordered alternatives:

1. **Pull `data/labels.parquet` alone first.** Small, gives exact Tamil and Telugu clip counts,
   and settles whether Tamil exists in the corpus. This is the only LRLspoof action that should
   happen before disk is freed.
2. **Check ModelScope for per-file access.**
   [modelscope.cn/datasets/lab260/LRLspoof](https://modelscope.cn/datasets/lab260/LRLspoof).
   **[UNVERIFIED, NEEDS A HUMAN TO CHECK]**, the file listing could not be read by automated
   fetch on 2026-09-14. If ModelScope exposes per-language files, the whole 452 GB problem
   disappears and this becomes a 1 to 2 GB pull.
3. **If neither works, stream-filter the tarball.** `curl` the parts into a pipe, `tar -xzf -
   --wildcards 'ta/*' 'te/*'` and discard everything else. This costs full download bandwidth but
   near-zero disk, since only the matching members are written. **[TO MEASURE]** whether the
   multi-part split allows a clean concatenated stream.
4. **If the download budget is not there, say so on the roadmap slide with the number**, the same
   way `SOTA_GAP_ANALYSIS.md` G7 instructs for API credits. "452 GB, spoof only, per-language
   access unconfirmed" is a better answer to a judge than silence.

### 2.4 The better Indic corpus for the same gap

> **SUPERSEDED 2026-09-14, later the same day, by bytes rather than by cards. Read this box
> before acting on 2.4 or on 2.3.** The two small fetches item 5 of "Do this today" asked for
> were made. Everything below in 2.4 that names SEA-Spoof as the replacement target is wrong,
> and 2.3's ordered alternatives 1, 2 and 3 are all now closed rather than open. The full
> evidence table is in `docs/SOTA_GAP_ANALYSIS.md` under G5's SECOND CORRECTION. The short form:
>
> | Claim in 2.3 and 2.4 | Status after the fetch |
> |---|---|
> | "Pull `labels.parquet` first, it settles whether Tamil exists" | **Done.** 6,345,951 bytes pulled from `lab260/LRLspoof`. 1,304,455 rows, `label` is `1` on every single one, so spoof-only is now proven and not quoted. **Tamil is absent**: zero utterance IDs start with `tamil/`. Telugu is **12,000 clips from 1 synthesizer (`indictts`)**. Hindi is 16,000 from 2. |
> | "452 GB" | **Exact.** 43 parts x 10,737,418,240 bytes = 452,045,616,080 bytes. |
> | "Check ModelScope for per-file access, the 452 GB problem could become a 1 to 2 GB pull" | **Closed, negative.** Both `oss/tree` endpoints return `"Data":[]`. No file listing is exposed. The 1 to 2 GB pull does not exist. |
> | "SEA-Spoof is the better target, paired, includes Tamil" | **Half right and therefore unusable.** Live, yes. Paired, yes. Tamil, yes. **Telugu, no**: the language tags are exactly `en, hi, id, ms, ta, th, vi`. And it is `"gated": "manual"` with author email approval, so nothing can be pulled without a human being approved. 81.5 GB, sharded by index not by language, smallest shard 1.35 GB. |
> | Priority order "SEA-Spoof first, LRLspoof second" | **Both dropped.** No public corpus reachable from this laptop covers Tamil and Telugu together. |
>
> **The replacement is IndicF5**, `ai4bharat/IndicF5`, MIT, one 1.4 GB weight file,
> `"gated": "auto"` so one account and one accepted licence rather than an email thread. It is
> a cloner, so it runs the same-speaker same-sentence matched-pairs protocol against the FLEURS
> Tamil and Telugu parents already on this disk, which is the protocol that keeps the 32.03%
> A1 confound out of the number. **[TO MEASURE]** whether `f5_tts` installs against the pinned
> py3.14 stack; expect a side venv, the pattern kokoro, chatterbox and now piper already use.


`research/03_data.md` line 22 already names **SEA-Spoof** (arXiv 2509.19865): 300+ hours of
**paired real and spoof** across Tamil, Hindi, Thai, Indonesian, Malay and Vietnamese, from 10
open-source and 4 commercial TTS/VC systems. **Paired** is the word that matters: it has a bona
fide side, so it does not reproduce the A1 confound the way LRLspoof does. Hosting is stated in
the paper as
[huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof](https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof).
**[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether that repo is live, its size on disk, and its
licence. `research/03_data.md` marked it "Directly relevant" on 2026-08-29 and nobody has opened
it since.

**Priority order for the language gap: SEA-Spoof labels first (paired, Tamil, 4 commercial
systems), LRLspoof labels second (spoof only, Telugu 22.12 h, Tamil unconfirmed).** This inverts
the order `SOTA_GAP_ANALYSIS.md` G5 implies, and the reason is the A1 finding, which is this
team's own result.

---

## A3. Paid cloner accounts. Open these today, they need no GPU.

This closes G7 properly. `SOTA_GAP_ANALYSIS.md` G7: the demo plays an ElevenLabs clone
(`ElevenLabs_2026-09-05T02_03_21_...mp3`, 103,164 bytes, sitting in the repo root) that appears
in no row of `eval/results.json`. The protocol to match is the one already used for Chatterbox in
`data/manifest_a2.csv`: **same speaker, same sentence, cloned from the exact FLEURS recording it
is scored against**, with `parent_clip_id` filled so the pairing is checkable.

All prices below come from web search on 2026-09-14 and are third-party summaries, not vendor
invoices. **Verify on the vendor's own pricing page before paying.** Rupee conversion is not done
here because no exchange rate was looked up.

| Vendor | Minimum tier | What it buys | Enough for G7? | Source |
|---|---|---|---|---|
| **ElevenLabs** | **$22/month** Creator (roughly $18.33/mo billed annually at $220/yr) | **121,000 credits/month**, 3 professional voice clones. Multilingual v2 charges 1 character = 1 credit, so ~1,000 credits is ~1 minute of speech. | **Yes, by a wide margin.** G7 asks for 20 to 40 clips. FLEURS Hindi sentences in `data/manifest_a2.csv` run roughly 150 to 250 characters, so 40 clips is **[ESTIMATE] 6,000 to 10,000 credits**, under 9% of one month's allowance. One month buys roughly 480 to 800 clips at that sentence length. | [happyrobot.ai](https://www.happyrobot.ai/hub/elevenlabs-pricing), [casrai.org](https://casrai.org/guides/elevenlabs-pricing) |
| **MiniMax** | Pay as you go. **speech-02-turbo $60 per million characters**, **speech-02-HD $100 per million characters**. Voice cloning **$1.50 per voice** one-off (one source) or **$3 per voice** (another source, the two disagree). | Per-voice clone plus per-character synthesis. | **Yes and it is the cheapest.** 40 clips at 200 chars is 8,000 characters. At the HD rate of $100/M that is **$0.80** of synthesis. The cost is the per-voice clone fee, and the matched-pairs protocol needs one cloned voice per FLEURS speaker. **[TO MEASURE]** how many distinct speakers the 510 FLEURS parents cover; at $1.50 to $3 per voice that number is the entire MiniMax bill. | [minimax-ai.chat](https://minimax-ai.chat/audio/), [knowara.com](https://knowara.com/ai-tools/voice/minimax-speech-review/) |
| **PlayHT** | Historically **$39/month** Creator (about $31.20/mo billed annually), roughly 3M characters/year, 10 instant voice clones. | Would have been a third commercial family. | **Probably not purchasable.** One search result states PlayHT's first-party sites stopped resolving after Meta's July 2025 acquisition and the standalone product was discontinued. **[UNVERIFIED, NEEDS A HUMAN TO CHECK]**, this is a single third-party claim, not a vendor statement. **Do not budget for PlayHT until someone loads play.ht in a browser.** | [voice.ai](https://voice.ai/hub/tts/play-ht-pricing/), [thetoolsverse.com](https://thetoolsverse.com/tools/play-ht-ai-voice-generator-cloning) |

### 3.1 Total Track A cash, minimum viable

**ElevenLabs Creator $22 + MiniMax top-up, call it $10 to cover clone fees and synthesis =
roughly $32 for one month**, which buys two commercial cloner families under the matched-pairs
protocol and closes G7 for both. `SOTA_GAP_ANALYSIS.md` section 5 already ranks this: "Paid
cloner API credits. Nothing. This is the highest value per rupee on the list and the cheapest."
That ranking survives the pricing check.

### 3.2 Consent and licence, before any key is used

`research/03_data.md` line 181 is a hard rule and it applies to paid APIs as well:
**clone only from public research corpora with distribution licences, never from a real person's
audio, and never from a judge's or teammate's voice on stage without written consent on the
slide.** FLEURS is CC-BY-4.0, which is the reason the existing matched-pairs work is clean. Keep
every paid-API clone sourced from FLEURS parents for the same reason.

Second rule, from `CLAUDE.md` and from this repo's own history: **API keys go into `.env`
immediately and never into a commit.** Run a secrets grep before any push that touches this work.

---

## A4. Reaching 30 to 50 generator families: the named list

`SOTA_GAP_ANALYSIS.md` section 5 names "30 to 50 generator families instead of 6" as the lever.
The current count, from `cut -d, -f5 data/manifest_all.csv | sort | uniq -c` on 2026-09-14:

| family | clips |
|---|---|
| `none` (bona fide) | 510 |
| `mms_vits` | 510 |
| `encodec` | 510 |
| `mac_say` | 340 |
| `xtts_v2` | 250 |
| `freevc24` | 250 |
| `kokoro` | 170 |
| `chatterbox` | 39 |

**UPDATED 2026-09-14, after Group 1 items 1 and 2 were built.** The same command now returns:

| family | clips | added |
|---|---|---|
| `none` (bona fide) | 510 | |
| `mms_vits` | 510 | |
| `encodec` | 510 | |
| `espeak_ng` | **510** | **2026-09-14** |
| `mac_say` | 340 | |
| `piper` | **340** | **2026-09-14** |
| `xtts_v2` | 250 | |
| `freevc24` | 250 | |
| `kokoro` | 170 | |
| `chatterbox` | 39 | |

**9 spoof families today, 850 new clips, 106 MB on disk. 21 more reaches 30.** The estimate in
section 4.1 was 196 MB for three families; two families came in at 106 MB measured
(`du -sh`: `espeak_ng` 64 MB, `piper` 42 MB), which is in line with it.

~~**7 spoof families today. 23 more reaches 30.**~~ The list below is named, not "more data". The
source for the bulk of it is LRLspoof's own 24-system roster (arXiv 2603.02364, fetched
2026-09-14), which is the most recent published enumeration of open-source TTS systems used for
exactly this purpose, plus the Indic-specific systems from `research/03_data.md`.

### 4.1 Group 1: CPU only, no GPU, no cost. Do these in Track A, this week.

| # | Family | Indic coverage | Licence | Note |
|---|---|---|---|---|
| 1 | **eSpeak NG** | **CONFIRMED 2026-09-14: Hindi, Tamil, Telugu, all three present in `espeak-ng --voices` (1.52.0).** | GPL-3.0 | Formant synthesis. Trivially different from every neural family in the set, which is the point: breadth. Runs in milliseconds per clip. **Built, 510 clips.** |
| 2 | **Piper** | **SETTLED 2026-09-14: Hindi yes (3 voices), Telugu yes (3 voices), Tamil NO (0 voices).** | MIT | Named in LRLspoof's roster. CPU-real-time by design. Read off `rhasspy/piper-voices` `voices.json`, 176 voices total. Piper is therefore a two-language family, the same shape as `mac_say`, not the three-language family this row assumed. **Built, 340 clips.** |
| 3 | **RHVoice** | **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** Indic coverage, its strength is Slavic and Turkic | LGPL | Only worth adding if an Indic voice exists. |
| 4 | **EnCodec at other bitrates** (1.5, 3, 12, 24 kbps) | Language agnostic | MIT | Weights already cached locally at 89 MB. **Honest caveat: this is depth within one family, not breadth.** The diversity curve counts families. Add it for the calibration story, not for the family count. |

Group 1 costs **zero dollars and zero GPU hours**. At 170 clips per language x 3 languages = 510
clips per family, three families is 1,530 clips x 128,044 B = **196 MB**.

### 4.2 Group 2: GPU, Indic-native. Highest value on the A100.

| # | Family | Indic coverage | Licence | Source |
|---|---|---|---|---|
| 5 | **IndicF5** (AI4Bharat) | **11 languages including Tamil and Telugu.** Trained on 1,417 h. | Model card requires explicit permission to clone a voice. **Exact licence UNVERIFIED**, `research/03_data.md` line 95 flags this. | [HF ai4bharat/IndicF5](https://huggingface.co/ai4bharat/IndicF5) |
| 6 | **Indic-Parler-TTS** (AI4Bharat + HF audio team) | **21 languages including Tamil and Telugu.** Trained on 1,806 h. | **Apache 2.0**, which is the cleanest licence in this whole table. | [HF ai4bharat/indic-parler-tts](https://huggingface.co/ai4bharat/indic-parler-tts) |
| 7 | **AI4Bharat Indic-TTS** (FastPitch + HiFiGAN) | Multiple Indian languages | **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** | [github.com/AI4Bharat/Indic-TTS](https://github.com/AI4Bharat/Indic-TTS) |
| 8 | **MMS-TTS, additional Indic languages** beyond hin/tam/tel | Meta MMS covers many more | CC-BY-NC-4.0 | Already have 3 checkpoints cached. Depth, not breadth, unless new languages enter the plan. |

**IndicF5 is the single highest-value item in this entire document.** `GAPS.md` line 98 has
carried "A2 is Hindi only. Chatterbox Multilingual supports 23 languages and Tamil and Telugu are
not among them. A held-out cloner in those two languages is unmeasured. IndicF5 is the named
candidate" as open since 2026-09-04. IndicF5 clones from a reference prompt, which means it can
run the **same-speaker same-sentence matched-pairs protocol in Tamil and Telugu**, which is
exactly what LRLspoof cannot do because it has no bona fide side. One cloner closes the gap that
a 452 GB corpus does not.

### 4.3 Group 3: GPU, multilingual zero-shot cloners

All named in LRLspoof's 24-system roster unless noted.

| # | Family | Note |
|---|---|---|
| 9 | **F5-TTS** | CC-BY-NC-4.0 per `research/03_data.md` line 99. Non-commercial, evaluation only. |
| 10 | **CosyVoice / CosyVoice 2** | |
| 11 | **Fish-Speech** | Non-commercial per `research/03_data.md` line 179. |
| 12 | **OuteTTS** | |
| 13 | **Zonos** | |
| 14 | **XTTS v1** | Distinct checkpoint from the held xtts_v2. CPML non-commercial. |
| 15 | **MeloTTS** | |
| 16 | **Matcha-TTS** | |
| 17 | **SpeechT5** | |
| 18 | **FastPitch** | |
| 19 | **Silero** | |
| 20 | **IMS Toucan** | Explicitly a low-resource-language system. |
| 21 | **Parler-TTS** (base) | English. Breadth for the family count, not for the Indic claim. |
| 22 | **StyleTTS 2** | MIT, **with the caveat in `research/03_data.md` line 101**: issue #37 flags the licence info as possibly misleading. Check before claiming. |

### 4.4 Group 4: neural audio codec resynthesis, genuinely different families

The `samecorpus` build already proved this pathway works: EnCodec resynthesis of a FLEURS
recording produces a spoof that sits in the bona fide score cloud (`HONEST_LOG.md`, A1, median
-9.38 versus -11.06). Different **codec architectures** are different families, unlike different
bitrates of the same codec.

| # | Family | Note |
|---|---|---|
| 23 | **DAC** (Descript Audio Codec) | |
| 24 | **Mimi** (Kyutai) | |
| 25 | **SpeechTokenizer** | |
| 26 | **WavTokenizer** | |
| 27 | **SoundStream / Lyra** | **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** whether an open checkpoint exists. |

This group is also where the honest comparison to **Indic-CodecFake** (arXiv 2604.19949) lives,
since ICF is built from neural audio codecs and SATYAM's 3.27% is measured on it.

### 4.5 Group 5: paid commercial APIs, Track A, no GPU

| # | Family | Note |
|---|---|---|
| 28 | **ElevenLabs Multilingual v2** | Closes G7. |
| 29 | **MiniMax speech-02-HD** | |
| 30 | **PlayHT** | Only if section A3 confirms it still exists. |

**7 existing + 23 new from groups 1 through 5 = 30 families**, which is the bottom of the
appendix's "30 to 50" range. Reaching 50 means adding depth per family across languages, and the
diversity curve does not yet say that helps.

### 4.6 What 30 families actually buys, stated honestly

`eval/results.json` `diversity_curve` mean EER by k: **8.1% at k=1, 12.8% at k=2, 13.2% at k=3,
13.8% at k=4, 13.0% at k=5, 13.2% at k=6.** Mean EER does **not** improve with more families.
What improves is spread: at k=1 the range is 4.1% to 13.2%, at k=6 it is 13.2% to 13.2%. This is
G12 in `SOTA_GAP_ANALYSIS.md` and it is the correct framing.

So the claim this plan can support after 30 families is **variance reduction, not mean
improvement**: "with few families the outcome depends on which you have, as bad as 26.0%; with
all 6 it is 13.2% regardless" (`GAPS.md` / diversity-curve finding). Going to 30 tests whether the
mean finally moves. **It might not.** Pre-register that: if the mean EER at k=30 is still near
13%, publish it. A negative result on the team's own claimed contribution, published, is a
criterion-2 point. `CLAUDE.md`'s rule applies: smaller honest numbers beat bigger soft ones.

---

## A5. Manifest format. Nothing enters the dataset without provenance.

The existing discipline, read off the three live manifests on 2026-09-14:

```
data/manifest_all.csv          clip_id,path,label,source,generator,family,language,duration_s,licence,parent
data/manifest_samecorpus.csv   clip_id,path,label,source,cloner,language,duration_s,licence,parent_clip_id,generator
data/manifest_a2.csv           clip_id,path,label,source,cloner,language,duration_s,licence,parent_clip_id,generator,device,text
```

Three rules the existing files already enforce and the new data must not break:

1. **One row per clip.** 347,382 bytes of `manifest_all.csv` for 2,579 clips, no aggregation.
2. **`parent` / `parent_clip_id` names the exact bona fide recording** the clip was derived from,
   so the matched-pairs protocol is checkable rather than asserted (`HONEST_LOG.md`, A1: "names
   the parent clip for every spoof clip, so the pairing is checkable rather than asserted").
3. **`licence` is carried per clip**, with compound values where the derivation stacks, for
   example `CC-BY-4.0+MIT` for a FLEURS recording pushed through EnCodec.

### 5.1 New file: `data/manifest_breadth.csv`

**New data goes in a new file. It is never mixed into the three existing manifests.** Those three
are what every published number in `eval/results.json` was computed from, and silently growing
them would invalidate the existing grid. The new file is a superset of `manifest_all.csv`'s
columns plus five provenance columns that the A100 run requires:

```csv
clip_id,path,label,source,generator,family,language,duration_s,licence,parent,voice_matched,gen_params,run_id,generated_utc,sha256
```

| Column | Meaning | Why it is new |
|---|---|---|
| `voice_matched` | `1` if the generator cloned the parent's voice (IndicF5, ElevenLabs, MiniMax, Chatterbox), `0` if it only reused the parent's sentence with a different voice (eSpeak NG, Piper, Indic-Parler-TTS in non-cloning mode, mms_vits, mac_say). | The existing manifests conflate these. `mms_vits` and `mac_say` have `parent` filled but do not clone the speaker. A judge asking "is this same-speaker or just same-sentence" currently has no column to read. This distinction decides which clips can enter a matched-pairs EER and which cannot. |
| `gen_params` | JSON string of the exact generation call: model revision or commit, sampling temperature, CFG scale, seed, reference audio path, device. | `SOTA_GAP_ANALYSIS.md`'s own rule and this repo's posture. Without it a family cannot be regenerated and the number cannot be defended. |
| `run_id` | The unique run ID that produced the clip, matching the existing `runs/call-<UTC>-<hash>.json` convention already used in `pramaan/runs/`. | Project non-negotiable: unique run IDs with isolated state. |
| `generated_utc` | ISO-8601 UTC timestamp. | Lets a clip be traced to a specific A100 session. |
| `sha256` | Hash of the wav bytes. | Detects silent corruption across the transfer from the rented box back to the laptop, which is a real risk on a 1.5 GB rsync. |

### 5.2 The rule that makes this non-negotiable

`SOTA_GAP_ANALYSIS.md` section 4 and `GAPS.md` line 26 both say the same thing in different
words: publish the absence, do not fake a channel we cannot produce. The data version of that
rule is: **a clip with no named source, no named licence and no recorded generation parameters is
worse than no clip, because it cannot be defended and it silently contaminates every number
computed from the set it sits in.** Any clip that arrives from the A100 without all fifteen
columns filled gets deleted, not imported.

---

# TRACK B: the A100 runbook

Execute in this order the moment the box is up. Nothing here needs a decision made on the day.

## B0. Before the clock starts, on the laptop

| Step | Action | Done when |
|---|---|---|
| B0.1 | Push `data/manifest_all.csv`, the 510 bona fide parent wavs (64 MB, `data/clips/bonafide`) and the sentence texts to a location the rented box can pull from. | The box can rebuild every parent without touching this laptop. |
| B0.2 | Write `scripts/gen_family.py` as a **one family per invocation** script taking `--family`, `--language`, `--run-id`, `--out`. One generator per process, one venv per family. | `--help` runs. |
| B0.3 | Pin a `requirements-<family>.txt` per family. | See B4, this is the actual hard part. |
| B0.4 | Decide the per-family clip target. **Recommendation: 170 clips per language x 3 languages = 510 clips per family, one clip per bona fide parent.** | Written into the script defaults. |

**Why 510 and not more.** One clip per parent preserves the matched-pairs protocol exactly: every
spoof row gets a real `parent`, and the bona fide side is the existing 510 FLEURS recordings that
every published number already uses. Going above 510 per family means either reusing parents
(which breaks the one-to-one pairing) or importing new bona fide audio (which reintroduces the A1
corpus confound). **The diversity curve says breadth, not depth, so spend the GPU on family 24
rather than on clip 511 of family 5.** This is the whole ranking principle of Track B.

## B1. Generation order, ranked by the diversity lever

Breadth first, and within breadth, Indic-native first, since the PS names Indian languages.

| Batch | Families | Clips | Why this order |
|---|---|---|---|
| **B1.1** | IndicF5, Indic-Parler-TTS, AI4Bharat Indic-TTS (3 families) | 1,530 | Closes `GAPS.md` line 98, open since 2026-09-04. IndicF5 gives a **voice-cloning** Tamil and Telugu attack, which is the thing that does not exist anywhere else in this plan. If the A100 dies after one hour, this is the batch that must have run. |
| **B1.2** | F5-TTS, CosyVoice 2, Fish-Speech, OuteTTS, Zonos, XTTS v1 (6 families) | 3,060 | Zero-shot cloners, so `voice_matched=1`. Highest realism per clip and closest to the actual threat model. |
| **B1.3** | MeloTTS, Matcha-TTS, SpeechT5, FastPitch, Silero, IMS Toucan, Parler-TTS base, StyleTTS 2 (8 families) | 4,080 | Non-cloning neural TTS, `voice_matched=0`. Cheap breadth. Several of these are small enough to run on CPU if the GPU is busy. |
| **B1.4** | DAC, Mimi, SpeechTokenizer, WavTokenizer, SoundStream (5 families) | 2,550 | Codec resynthesis. Fast, and the only group that produces same-speaker spoof **without any cloning permission question**, since it resynthesises the parent recording itself. |
| **Total** | **22 new families** | **11,220 clips** | Plus Group 1's 3 CPU families from Track A reaches 25 new, 32 total. |

## B2. Cost, and it is smaller than expected

### 2.1 GPU rental rates, web search 2026-09-14

| Provider | A100 80GB, per hour | Source |
|---|---|---|
| **Vast.ai** | **~$0.72/hr** marketplace average, early 2026 | [madebyagents.com](https://www.madebyagents.com/hardware/gpu-rental-prices) |
| **RunPod** | **$1.49/hr**, some configs $1.19 to $1.39 | [buildmvpfast.com](https://www.buildmvpfast.com/blog/gpu-cloud-cost-comparison-runpod-lambda-labs-coreweave-2026) |
| **Lambda Labs** | **$2.06/hr** | same |

Range across providers as reported: $0.68/hr hyperscale spot to $4.10/hr on-demand.

### 2.2 GPU-hours needed

**[ESTIMATE], all of it.** No family in this plan has been benchmarked on an A100 by this team.

- Audio to synthesise: 11,220 clips x 4 s = 44,880 s = **12.5 hours of audio**.
- Zero-shot cloners on an A100 run at **[ESTIMATE]** RTF 0.1 to 0.3. At RTF 0.3 that is
  **3.7 GPU-hours of pure synthesis** for the whole set.
- Per-family overhead dominates: weight download, venv build, warm-up, a failed first attempt.
  **Budget 0.5 h per family x 22 = 11 hours.**
- **Total: [ESTIMATE] 15 GPU-hours**, with 20 as the padded figure.

### 2.3 The bill

| Provider | 20 GPU-hours |
|---|---|
| Vast.ai at $0.72/hr | **$14.40** |
| RunPod at $1.49/hr | **$29.80** |
| Lambda at $2.06/hr | **$41.20** |

**The A100 rental is a $15 to $41 line item, not a major spend.** Added to Track A's roughly $32
of API credits, **the entire data plan costs under $75 of compute and credits** before any
external SSD. The honest conclusion from that arithmetic: **the A100 is not the expensive part of
this plan and it is not the bottleneck either.** The bottleneck is section B4.

## B3. Checkpoint and resume discipline

Non-negotiables, matching `CLAUDE.md` and this repo's existing `runs/` convention.

| Rule | Implementation |
|---|---|
| **Unique run ID, isolated state** | `run_id = gen-<UTC>-<5 hex>`, matching the existing `runs/call-20260914-095949-c142c.json` shape. Every family gets its own run ID and its own output directory. No two families ever write the same path. |
| **Checkpoint and resume** | One JSON per run recording the list of `parent` IDs already generated. On restart the script skips completed parents. A dropped spot instance costs the current clip, never the batch. |
| **Back up before any reset** | `rsync` each family's directory plus its manifest rows back to durable storage **immediately when that family finishes**, not at the end of the session. A spot instance that disappears at hour 12 must not take 11 families with it. |
| **Preserve every generated artifact** | Nothing is deleted on the box, including failed and clipped outputs. Failures are recorded in the manifest with `label` and a `gen_params` note, because a family that produces silence is itself a finding worth publishing. |
| **Config over hardcoding** | Family list, per-family clip target, language list and output root all come from one config file, not from edits to the script. |
| **Verify before trusting** | `sha256` is computed on the box and re-checked on the laptop after transfer. A manifest row whose hash does not match its file is deleted, not fixed. |
| **Shut the box down** | The rental is billed by the hour. Terminate on completion. **[TO MEASURE]** whether the chosen provider bills for a stopped-but-not-terminated instance. |

## B4. The actual risk, and it is not compute

`GAPS.md` lines 62 to 74 record what happened the last time this team added one generator family:
`pip install chatterbox-tts` "would downgrade **transformers 5.16.1 to 5.2.0, librosa 1.0.0 to
0.11.0** plus safetensors and tokenizers, inside the pinned py3.14 stack that D0 verified and the
whole matrix runs on."

**Twenty-two families means twenty-two dependency graphs, and several of them will conflict with
each other as badly as Chatterbox conflicted with the pinned stack.** The mitigations:

1. **One isolated venv per family on the rented box.** Never a shared environment. This is
   affordable on cloud disk and was impossible on the laptop, where the same attempt died at
   `Errno 28` with 533 MB left.
2. **Nothing from those venvs ever comes back to the laptop.** Only wav files and manifest rows
   cross the boundary. The pinned py3.14 stack on the M4 is untouched by this entire plan. This
   is the operational meaning of "training moves off the laptop, inference never does".
3. **Budget the failures explicitly.** **[ESTIMATE] expect 4 to 8 of the 22 families to fail to
   install or to produce unusable audio in Indic languages.** Publish the list of families that
   failed and why. `GAPS.md` line 26 already establishes the precedent for this with AMR-WB and
   EVS: "Drop them from the grid and publish the absence. Do not fake a channel we cannot
   produce."
4. **`torchaudio.load()` is broken on this stack and everything must use `soundfile`**
   (`HONEST_LOG.md`, carried forward in `SOTA_GAP_ANALYSIS.md` G6). Write every generation script
   with `soundfile` from the first line so the clips import cleanly on the laptop.

## B5. What comes back, and what it costs on the laptop

| Artifact | Size |
|---|---|
| 11,220 new clips at 128,044 B | **1.44 GB** |
| `data/manifest_breadth.csv` | **[ESTIMATE] 4 MB**, scaling `manifest_all.csv`'s 347 KB for 2,579 rows by 4.35x and adding 5 columns |
| Feature cache growth | **[ESTIMATE] 1.5 to 2 GB.** `eval/results/features.npz` is 427 MB for the current set; the clip count rises roughly 4.3x |
| **Total new disk needed on the laptop** | **[ESTIMATE] 3.5 GB** |

**3.5 GB against 274 MB free.** Section A1 is not optional and it is not a nice-to-have. It is the
precondition for Track B being importable at all.

---

# What NOT to do with the A100

Each of these contradicts something the team already argues on stage.

### 1. Never fine-tune XLS-R end to end.

`SOTA_GAP_ANALYSIS.md` section 4 and section 5 both refuse this, and section 5 calls it "the one
to refuse". The evidence is **Pascu et al., Interspeech 2024**: a frozen SSL frontend with under
2,000 trainable parameters beat RawNet2's 25M trainable parameters out of domain, **30.9% to 8.8%
mean OOD EER**. `GAPS.md` line 12 records the same result as the reason the GPU requirement was
removed from this project in the first place.

Fine-tuning would contradict three live claims at once: the 2,049-trainable-parameter
architecture answer, the Pascu justification spoken on stage, and the RTF 0.046 on-CPU number
that beats five of seven named commercial systems in the Podonos benchmark. **A rented GPU that
generates data leaves all three intact. A rented GPU that trains the frontend destroys all
three.** The rental is for data, and the tokens for the head still train in about 40 seconds on
the M4 CPU.

### 2. Never let inference depend on GPU availability.

The shipped path must stay: Wi-Fi off, no model or CDN fetched at run time, 5.4 streams per CPU
core at a 1 s hop, 37 cores for 200 seats (`eval/results/latency.json`,
`capacity.cpu_hop_1.0`). `SOTA_GAP_ANALYSIS.md` section 5: "It runs on a laptop with no GPU
currently carries three of the ten criteria at once (feasibility, scalability, privacy under
relevance) and it is the only axis on which Pramaan structurally beats seven named commercial
systems, all of which are cloud APIs."

Concretely: **no MPS-only or CUDA-only code path may enter `src/pramaan/`** as a result of this
plan. The generation scripts live in `scripts/`, run on the rented box, and are not imported by
anything the demo executes.

### 3. Never generate synthetic data without full provenance.

Every clip carries source, licence and generation parameters, or it does not enter the manifest.
This is section A5.2 restated because it is the rule most likely to be broken at 2 a.m. on an
hourly-billed box. A clip with no `gen_params` cannot be regenerated, so its contribution to any
EER cannot be defended, so it silently weakens every number computed from the set containing it.
**Delete it, do not import it.**

Two corollaries with teeth:

- **Non-commercial licences stay labelled.** `GAPS.md` line 31: IndicSynth, MLAAD, XTTS-v2 and
  F5-TTS are non-commercial. `SOTA_GAP_ANALYSIS.md` section 4: "Production ready never appears on
  the same slide as either." Several Group 3 families above are NC. The `licence` column is how
  that rule stays enforceable at slide-build time rather than at slide-review time.
- **Cloning consent applies to generated data too.** `research/03_data.md` line 181. Every clone
  in this plan is sourced from a CC-BY-4.0 FLEURS recording. Nothing is cloned from a teammate, a
  judge or a public figure.

### 4. Do not let the family count become the claim.

"We have 30 generator families" is an adjective dressed as a number. The claim the data can
support is the one in section A4.6: the measured spread across generator subsets, before and
after. If the mean EER does not move, say so.

---

# Do this today

Five actions. Zero GPU, zero new hardware, all startable within the hour. Ranked.

1. **Free disk, and run `df -h` first so the starting number is on the record.** The measured
   floor right now is **274 MB**. Clear `~/Downloads` (**8.3 GB**) and `~/.cache/whisper`
   (**1.9 GB**), plus the four unrelated model caches in section 1.1 (**467 MB**). Do **not**
   delete `models--facebook--wav2vec2-xls-r-300m` (2.4 GB), `datasets--google--fleurs` (1.3 GB),
   `datasets--vdivyasharma--IndicSynth` (1.5 GB), `encodec_24khz`, the three `mms-tts-*`
   checkpoints or `Kokoro-82M`. Do **not** touch `pramaan/eval/` at all this week, a separate
   agent is working in it. Target: **10 GB free**, which is 3x the 3.5 GB Track B needs to land.

2. **Open the ElevenLabs Creator plan, $22/month, 121,000 credits.** This is the single highest
   value per rupee item in `SOTA_GAP_ANALYSIS.md` section 5 and the pricing check confirms it:
   40 clips at FLEURS sentence length is **[ESTIMATE] 6,000 to 10,000 credits**, under 9% of one
   month. It closes G7, which currently has an ElevenLabs mp3 in the repo root and no ElevenLabs
   row anywhere in `eval/results.json`. Key straight into `.env`, never into a commit.

3. **Open a MiniMax account and top up roughly $10.** speech-02-HD is **$100 per million
   characters**, so 40 clips is **$0.80** of synthesis; the real cost is **$1.50 to $3 per cloned
   voice** and the two sources disagree on which. First job on the account: count how many
   distinct speakers the 510 FLEURS parents cover, because that number times the clone fee is the
   entire MiniMax bill. **Skip PlayHT** until someone loads play.ht in a browser; one source
   reports the standalone product was discontinued after Meta's July 2025 acquisition and that is
   **[UNVERIFIED]**.

4. **Install eSpeak NG and Piper and generate two CPU-only generator families.** 510 clips each,
   one per bona fide parent, hi/ta/te, **196 MB total for three families including the extra
   EnCodec bitrates**. Zero dollars, zero GPU, and it moves the family count from 7 to 9 before
   the A100 exists. Write them straight into the new `data/manifest_breadth.csv` with all fifteen
   columns filled, which also proves the manifest format works before 11,220 clips depend on it.

5. **DONE 2026-09-14, and the answer changed the plan. See the SUPERSEDED box at the top of
   section 2.4 and G5's SECOND CORRECTION in `docs/SOTA_GAP_ANALYSIS.md`.** One file was
   pulled, `labels.parquet` at 6,345,951 bytes. No part of the 452 GB tarball and no part of
   SEA-Spoof's 81.5 GB was touched. Result: **Tamil is absent from LRLspoof entirely** (zero of
   1,304,455 utterance IDs), Telugu is **12,000 clips from 1 synthesizer**, every row is
   `label=1` so spoof-only is proven, ModelScope exposes **no** file listing so the per-language
   escape does not exist, and SEA-Spoof **has Tamil but not Telugu** and is `"gated": "manual"`
   behind author email approval at 81.5 GB. Next candidate: **IndicF5**, 1.4 GB, MIT,
   `"gated": "auto"`. The original instruction is kept below.

   ~~**Settle LRLspoof with two small fetches, and do not start the 452 GB pull.** Pull~~
   `data/labels.parquet` from
   [MTUCI/LRLspoof](https://huggingface.co/datasets/MTUCI/LRLspoof) to get the exact Tamil and
   Telugu clip counts and to confirm whether Tamil is in the corpus at all, since the paper's
   Table 2 lists Telugu at 22.12 hours with 1 synthesizer and does not list Tamil. Then open
   [ModelScope](https://modelscope.cn/datasets/lab260/LRLspoof) in a browser and check for
   per-language files; if they exist the 452 GB problem becomes a 1 to 2 GB pull. In the same
   sitting, open
   [Jack-ppkdczgx/SEA-Spoof](https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof) and check
   whether it is live, because SEA-Spoof is **paired real and spoof** including Tamil, and
   LRLspoof is **spoof only**, which means LRLspoof scored against FLEURS reproduces the exact
   corpus confound this team measured at 32.03% EER on 2026-09-03.

---

## Sources for every external number in this file

Pricing and hardware, all web search 2026-09-14, all third-party summaries rather than vendor
invoices, all to be verified on the vendor's own page before payment:
[ElevenLabs pricing, happyrobot.ai](https://www.happyrobot.ai/hub/elevenlabs-pricing) ·
[ElevenLabs pricing, casrai.org](https://casrai.org/guides/elevenlabs-pricing) ·
[MiniMax audio pricing](https://minimax-ai.chat/audio/) ·
[MiniMax speech review, knowara.com](https://knowara.com/ai-tools/voice/minimax-speech-review/) ·
[PlayHT pricing, voice.ai](https://voice.ai/hub/tts/play-ht-pricing/) ·
[PlayHT review, thetoolsverse.com](https://thetoolsverse.com/tools/play-ht-ai-voice-generator-cloning) ·
[GPU rental prices, madebyagents.com](https://www.madebyagents.com/hardware/gpu-rental-prices) ·
[GPU cloud comparison, buildmvpfast.com](https://www.buildmvpfast.com/blog/gpu-cloud-cost-comparison-runpod-lambda-labs-coreweave-2026)

Datasets and models, fetched 2026-09-14:
[LRLspoof on HuggingFace](https://huggingface.co/datasets/MTUCI/LRLspoof) ·
[LRLspoof paper, arXiv 2603.02364](https://arxiv.org/html/2603.02364v2) ·
[LRLspoof on ModelScope](https://modelscope.cn/datasets/lab260/LRLspoof) ·
[SEA-Spoof, arXiv 2509.19865](https://arxiv.org/abs/2509.19865) ·
[SEA-Spoof on HuggingFace](https://huggingface.co/datasets/Jack-ppkdczgx/SEA-Spoof) ·
[IndicF5](https://huggingface.co/ai4bharat/IndicF5) ·
[Indic Parler-TTS](https://huggingface.co/ai4bharat/indic-parler-tts) ·
[AI4Bharat Indic-TTS](https://github.com/AI4Bharat/Indic-TTS) ·
[Indic-CodecFake and SATYAM, arXiv 2604.19949](https://arxiv.org/html/2604.19949v1)

Internal, all measured or read on this machine on 2026-09-14:
`df -h /System/Volumes/Data` · `du -sh` on `~/.cache/*` and `~/Downloads` ·
`ls -la data/clips/spoof/freevc24/spoof_freevc24_00106.wav` ·
`cut -d, -f5 pramaan/data/manifest_all.csv | sort | uniq -c` ·
`pramaan/src/pramaan/channels.py` · `pramaan/docs/SOTA_GAP_ANALYSIS.md` ·
`pramaan/eval/results.json` · `GAPS.md` · `HONEST_LOG.md` · `research/03_data.md` ·
`docs/RUBRIC_ATTACK.md`
