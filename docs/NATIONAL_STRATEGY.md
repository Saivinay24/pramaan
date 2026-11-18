# NATIONAL_STRATEGY

> Written 2026-09-18 for the SIH 2026 **National round** submission due 19 September 2026:
> one demo video under ten minutes, plus the idea PPT on the mandated SIH template.
>
> This file is the brief the deck agent and the video agent build from. It decides; it does not survey.
>
> **Number rule, inherited and non-negotiable.** Every Pramaan number in this file exists in
> `docs/NUMBERS.json`. Every external number names its source. If a number is not in
> `NUMBERS.json` and has no citation here, nobody may put it on a slide or say it on camera.
> **No em dashes anywhere in any outward artifact.**

---

## 1. The rubric, as best established

### 1.1 What is actually published

SIH has never published a weighted national-round marking sheet. What it publishes, and what has
been stable across SIH editions and is repeated verbatim by 2026 sources, is a **named criteria
list with no numbers attached**:

> novelty of the idea, complexity, clarity and details in the prescribed format, feasibility,
> practicability, sustainability, scale of impact, user experience, and potential for future work
> progression.

Sources:
- SIH 2026 rules summary, criteria list quoted as "novelty, complexity, clarity, completeness in
  the prescribed format, feasibility, practicability, sustainability, scale of impact, user
  experience, and future progression": https://sih-lemon-eight.vercel.app/rules
- Same list reproduced against sih.gov.in guidance for earlier editions:
  https://www.sgsits.ac.in/files/Guidelines_SIH2023.pdf and
  https://nitjsr.ac.in/backend/uploads/notices/713c2441-3091-4188-adca-9bc48c07abd8-Internal%20Idea%20Hackathon%20-%202023.pdf
- SIH 2026 participant guidance repeating "innovation, relevance of the problem, feasibility,
  effectiveness of the proposed solution, application of technology and quality of presentation"
  for national evaluation: https://whereuelevate.com/blogs/smart-india-hackathon-2026 and
  https://reskilll.com/blogs/smart-india-hackathon-2026-complete-guide-registration-themes-winning/

**Confidence: high on the criteria names, zero on any official weighting.**

### 1.2 The weightings that circulate, and what they are worth

One widely read 2026 guide assigns percentages: problem understanding and clarity 20%, innovation
and uniqueness 25%, technical feasibility 20%, impact and scalability 20%, presentation quality
and clarity 15% (https://reskilll.com/blogs/sih-2026-ppt-template-exact-format-slides-evaluators-score/).

**Confidence: low. This is a coaching blog, not MoE or AICTE.** It is also internally inconsistent
with the official template, since the same page prescribes a ten-slide deck while the mandated
`ppt/SIH2026-IDEA-Presentation-Format.pptx` says "Kindly keep the maximum slides limit up to six
(6). (Including the title slide)". **Where that guide and the official template disagree, the
template wins.** Treat the percentages as a directional hint only: novelty is the single heaviest
line, and presentation is the lightest but non-zero.

A search result also surfaced a "SIH 2023 Software Edition" marking sheet with Novelty 10,
Complexity 10, Clarity 10 and so on. **That is a false lead and must not be used.** The actual
document at https://damassets.autodesk.net/content/dam/autodesk/www/pdfs/sih-2023-software-edition.pdf
is Autodesk's own problem-statement brief, and its marking table reads Design Objective 10, Design
Process 10, Creativity and Novelty 30, Software Usage 30, Manufacturability 20, total 100. That is
a sponsor-specific CAD rubric, not the SIH software rubric. Do not cite it.

### 1.3 The working rubric we plan against

`docs/RUBRIC_MAP.md` already assumes "ten criteria, ten marks each". **That equal weighting is an
assumption this team made, not a published fact, and this file keeps it while labelling it as an
assumption.** It is the right assumption anyway: with no published weights, the dominant strategy
is to score every named criterion rather than to bet on one. The ten rows below merge the official
criteria list with the ten rows `RUBRIC_MAP.md` already runs on, so no existing work is thrown away.

| # | Criterion (working) | Official term it maps to |
|---|---|---|
| 1 | Problem understanding | clarity and details in the prescribed format |
| 2 | Novelty and uniqueness | novelty of the idea |
| 3 | Relevance to the problem statement | completeness in the prescribed format |
| 4 | Technical approach and complexity | complexity |
| 5 | Feasibility | feasibility, practicability |
| 6 | Prototype and completeness of solution | practicability |
| 7 | Scalability | scale of impact |
| 8 | Impact and usefulness | scale of impact, user experience |
| 9 | Sustainability and business model | sustainability, potential for future work progression |
| 10 | Presentation quality | quality of presentation |

**Plan for all ten. Assume none is worth zero and none is worth double.**

### 1.4 How a video-plus-PPT submission is scored

No official document describes the scoring of a demo video separately from the PPT. What is
established: the PPT must be the mandated template, maximum six slides including the title slide,
uploaded as PDF only, with the instructions slide deleted (the template's own slide 7 says all of
this). The safe planning assumption is that **the PDF carries criteria 1 to 5 and 9, and the video
carries 6, 7, 8 and 10**, with novelty needing to land in both. Build so that either artifact alone
would still score, because we cannot assume both are watched by the same person at the same time.

---

## 2. Per-criterion attack plan

Format for each: **strongest evidence we hold**, **where we currently under-sell**, **the exact
claim to make**. Sources are file paths in this repo unless stated.

### 1. Problem understanding
- **Strongest evidence.** `PS.md` is captured verbatim and the team's reading extracts five
  commitments the PS text actually makes: during the call, actionable score, prevention, on-device,
  Indian languages. Every one of them is traceable to a built component
  (`docs/RUBRIC_MAP.md` row 3).
- **Under-sold.** The current opening (`docs/PRESENTATION_SCRIPT.md`, S1) is a good human story,
  but it does not say out loud that **the PS title contains the word "Prevention" and most
  solutions answer only "Detection"**. That sentence is the whole positioning and it is buried.
- **Exact claim.** "The problem statement asks for five things. Detect during the call. Give an
  actionable score, not a label. Prevent the transaction. Run on the device. Work in Indian
  languages over real phone lines. Half the title is prevention, and that is the half this project
  is built around."

### 2. Novelty and uniqueness
- **Strongest evidence.** The generator-diversity result, measured, not argued: with one generator
  family the held-out error on an unseen 2025 cloner ranges from `div_k1_min` 4.5% to
  `div_k1_max` 39.6%, a span of 35.1%; with all 8 families it is `div_kN` 13.2% with a span of
  0.0% (`NUMBERS.json`, `div_table_rows`). The previous build of this project scored
  `legacy_unseen` 35.9% on the same cloner. Plus the same-speaker, same-sentence protocol: the
  held-out cloner clones the exact recording it is scored against, so corpus, speaker and content
  cannot be the tell (`README.md`, Results).
- **Under-sold.** The deck presents diversity as a nice chart. It is a **scaling law with a
  variance interpretation**: variety does not buy a lucky number, it removes the unlucky one. The
  deck never says the span shrinks from 35.1% wide to 0.0% wide, which is the actual finding.
- **Exact claim.** "Our contribution is not a model. It is a measured design rule: train on one or
  two synthesis families and your error against a cloner you have never seen is a lottery between
  4.5% and 39.6%. Train on all 8 and it is 13.2% every time. The spread collapses from 35.1 points
  wide to zero. Our own earlier build, on two families, sat at 35.9%."
- **And name the prior art in the same breath**, per `docs/SOTA_GAP_ANALYSIS.md` section 4: the
  shortcut-finding has adjacent published work (LRLspoof arXiv 2603.02364; arXiv 2412.00175;
  HQ-MPSD arXiv 2512.13012). The claim that survives a knowledgeable judge is "we ran the
  matched-pairs control on Indian-language speech against a 2025 cloner and published the cell
  where we failed", not "nobody has done this".

### 3. Relevance to the problem statement
- **Strongest evidence.** Line-by-line traceability already written in `docs/RUBRIC_MAP.md` row 3:
  acoustic artefacts (Listener), continuous risk score (Gate, every 0.5 s), configurable
  thresholds (the per-channel band), alerting and interaction layer (console), on-device inference
  (demo runs with Wi-Fi off), APIs (FastAPI plus WebSocket), Indian languages
  (`n_hindi` 1,729, `n_tamil` 680, `n_telugu` 1,020 clips), prevention (the ladder).
- **Under-sold.** The **deliberate exclusion** is not on any slide. `docs/RUBRIC_MAP.md` already
  has the right script for it: cross-session consistency against enrolled historical samples is a
  PS Key Component, it is not implemented, and the reason is the dataset (FLEURS gives one
  recording per speaker, so there is no speaker history to check against), not the model. Naming
  the academic frame, SASV, costs one line and earns criterion 2 and 3 at once.
- **Exact claim.** "One Key Component we did not build: cross-session consistency against enrolled
  historical samples. The frame for it is spoofing-aware speaker verification. It needs a bank's
  own stored recordings of that customer, which arrive with deployment, and the PS itself says
  'where available'. It also answers a different question: is this the same person as last time.
  We answer: is this a person at all. That is the one you can answer on a first call from a number
  with no history, which is how the fraud actually arrives."

### 4. Technical approach and complexity
- **Strongest evidence.** Frozen `facebook/wav2vec2-xls-r-300m` layer 5 with mean and std pooling,
  and `n_trainable` 2,049 trained parameters, with a published reason (Pascu et al., Interspeech
  2024). Isotonic calibration per prefix length. A sequential gate with three commit conditions and
  a band derived per channel from bona fide speech alone at a `fpr_budget` 2% false-positive budget,
  never hand-set: `band_clean` [0.010, 0.014] on a clean line, `band_worst` [0.036, 0.500] on a
  G.723.1 6.3 kbps line, because genuine speech scores higher the harder the codec squeezes it
  (`README.md`, What it does).
- **Under-sold.** Two things. First, **2,049 parameters is a complexity argument, not a simplicity
  apology**, and the deck currently lets it read as small. Second, the per-channel band is the most
  technically sophisticated thing in the system and it appears nowhere on a slide.
- **Exact claim.** "We train 2,049 parameters on top of a frozen 300-million-parameter multilingual
  frontend, and that is a decision with a published justification, not a shortcut: fine-tuning on
  the cloners you have memorises their fingerprints and fails on the next one. The consequence is
  that nothing in the critical path needs a GPU. And the decision threshold is not a constant we
  typed. It is derived per telephone channel from genuine speech alone at a 2% false-alarm budget,
  which is why it moves from [0.010, 0.014] on a clean line to [0.036, 0.500] on a narrowband
  G.723.1 line."

### 5. Feasibility
- **Strongest evidence.** Everything was built and measured on one laptop with no GPU and no
  budget: `n_clips` 3,429 clips, `audio_minutes` 229 minutes, `n_embeddings` 70,424 cached
  embeddings, `n_conditions` 7 channel conditions. Risk register with measured mitigations rather
  than promises: a new cloner costs `ad_shotsN` 12 labelled recordings to take held-out error from
  `ad_base` 18.8% to `ad_eerN` 0.0% on speakers the adapted model never saw; calibration ECE is
  `cal_raw` 0.05 raw and `cal_iso` 0.08 isotonic on the unseen cloner; licences are named
  (`README.md`, Licences).
- **Under-sold.** The failure grid. A judge reads a deck with no red cells as untested. Ours has
  red cells and the deck does show them, but nobody says the sentence that converts them into a
  score.
- **Exact claim.** "There are red cells in our grid on purpose. `gm_encodec` EnCodec resynthesis is
  24.4% held out. A grid with no red cells is a grid where nobody ran the hard test."

### 6. Prototype and completeness of solution
- **Strongest evidence.** All four layers exist and run: Listener, Gate, prevention ladder, ledger.
  The demo runs offline with Wi-Fi off, streams real Hindi speech chunk by chunk through the same
  live pipeline, and always displays each sample's true origin. First legal decision at
  `min_commit` 1.5 s, `lat_cpu4` 185 ms per update on CPU. The ledger tamper is demonstrable live:
  edit block 2, verify, every later hash breaks.
- **Under-sold.** The ladder is demonstrated but the **policy invariant** is not stated as an
  invariant. "A high-value action is never cleared by the voice" is enforced in
  `src/pramaan/stream.py`, not on a slide. That is the difference between a feature and a guarantee.
- **Exact claim.** "This is not a slide. Voice is never the last factor, and that is a rule in the
  code path, not a policy in a document. The clone the passive detector missed is the one the
  registered device blocked, and you just watched that happen."

### 7. Scalability
- **Strongest evidence.** `lat_cpu4` 185 ms per update on CPU at a 4 s window, `rtf_cpu4` 0.046;
  `lat_mps4` 104 ms on MPS, `rtf_mps4` 0.026. `cap_streams` 5.4 concurrent calls per CPU core at a
  1 s update, so `cap_cores` 37 cores covers a 200-seat centre, on one commodity server, no GPU.
- **Under-sold. This is the biggest single miss in the current deck.** The independent
  third-party latency comparison exists in `docs/SPEAKER_S5.md` and is on no slide and in no line
  of `scripts/build_deck.py`. From the Podonos audio deepfake detection benchmark of 14 August
  2026: Corsound AI real-time factor 0.035, Pindrop 0.076, Resemble 0.40, Reality Defender 1.52.
  Pramaan is 0.046, on a laptop CPU, offline. **Reality Defender above 1.0 cannot keep up with a
  live stream at all.** Latency against latency is the one axis where a cross-vendor comparison is
  methodologically fair, and this team is currently declining a fair fight it wins.
- **Exact claim.** "Real-time factor 0.046 on a laptop processor with the network off, against
  0.076 for Pindrop, 0.40 for Resemble and 1.52 for Reality Defender on the independent Podonos
  benchmark of 14 August 2026. Above 1.0 means the detector cannot keep up with a live call. Ours
  is the only one of those that is not a cloud API."
- **Guardrail, from `docs/SOTA_GAP_ANALYSIS.md` section 4.** Never put our EER next to the Podonos
  accuracy column. Different corpus, English only, different metric. **Latency versus latency only.**

### 8. Impact and usefulness
- **Strongest evidence.** The direction of the error is customer-safe: at the shipped operating
  point genuine speech is called synthetic `op_fpr_clean` 0.4% of the time on a clean line,
  `op_fpr_allchan` 1.1% pooled across all `n_channels_scored` 7 channels over `n_bona_allchan`
  3,570 genuine recordings, `op_fpr_worst` 1.6% on the worst channel (G.726 32 kbps). It misses
  clones rather than accusing customers. Decision at 1.5 s, inside the caller's first sentence.
- **Under-sold.** The public failure grid as a **market artifact**. Today a bank buying voice-fraud
  detection has no per-language, per-codec table showing where a product fails. Publishing ours has
  value to the whole market independent of whether anyone buys our software. That is a real impact
  claim and it currently sits as a bullet rather than as a headline.
- **Exact claim.** "1.1% false alarms across 3,570 genuine recordings on all seven telephone
  channels, 1.6% on the worst. A fraud system that insults real customers is switched off within a
  month, so the system defers and asks rather than accusing. And we publish the grid, including the
  cells we fail, because no vendor does, and a bank should be able to check a claim before buying."
- **Forbidden.** A market size in crores. `docs/RUBRIC_MAP.md` row 8 already names this as the trap.

### 9. Sustainability and business model
- **Strongest evidence.** The model decays when new cloners ship, **and the decay cost is
  measured**: `ad_shots0` 3 recordings gives `ad_eer0` 6.2%, `ad_shotsN` 12 recordings gives
  `ad_eerN` 0.0%, from a base of `ad_base` 18.8%. That converts "subscription" from a business
  cliche into a costed engineering fact. Per-seat on-premise licence plus a re-evaluation
  subscription; near-zero marginal cost per call because nothing goes to a third-party API.
- **Under-sold.** The licence path. Saying "IndicSynth and Meta MMS are research licences, so the
  production model is retrained on licensed or self-generated data, and that is a costed roadmap
  step" is a candour point most teams cannot make (`README.md`, Licences).
- **Exact claim.** "Our business model is the decay curve. A detector that was accurate the day it
  shipped is not accurate a year later, and we measured what the repair costs: 12 labelled
  recordings of a new cloner and seconds of retraining takes error on it from 18.8% to 0.0%. That
  quarterly re-evaluation is the subscription. A vendor who tells you their detector is permanent
  has not tested it against a cloner released after they shipped."

### 10. Presentation quality
- **Strongest evidence.** Every number in every artifact is generated from `eval/results.json` by
  one script, and the deck itself is built by `scripts/build_deck.py` from that file. Nothing is
  typed by hand. Six speakers, timed, one voice per slot, Q&A ownership pre-assigned
  (`docs/QA_PREP.md`).
- **Under-sold.** Say it on camera once, in one sentence. It is the strongest credibility signal in
  the whole submission and it takes four seconds.
- **Exact claim.** "Every number you will see is written into one results file by one script, and
  these slides are generated from that file. Nothing on them was typed by a human."

---

## 3. The three things that make this project undeniable

Ranked by **how hard another team can match them before tomorrow**, which is the only ranking that
matters. All five candidates were checked against the docs; two of them are true but not
differentiating, and that is stated.

### Rank 1. Honest measured generalisation against a 2025 cloner, with real confidence intervals

**Verified.** `NUMBERS.json` carries `unseen_eer_ci` "13.2% (95% CI 4.7% to 21.9%)" over
`n_unseen_total` 23 held-out clones and `n_unseen_bona` 127 held-out genuine recordings, from a
cluster bootstrap that resamples parent recordings rather than clips. It also carries the second,
more important number: at the shipped band the unseen cloner is called synthetic
`op_catch_unseen` 69.2% of the time (95% CI 53.6% to 81.4%), deferred `op_defer_unseen` 0.0% and
waved through `op_miss_unseen` 30.8%. Two clip counts, two protocols, both published
(`shipped_unseen_eer_ci` 5.7%, 95% CI 3.0% to 8.8% on all 39 Chatterbox clips).

**Why it cannot be matched.** Another team cannot fabricate a confidence interval that survives a
question about how it was computed. The cluster bootstrap over parent recordings, chosen because a
genuine recording and its clone are one unit and not two independent draws, is an answer no team
that vibed its numbers can give. And the same-speaker same-sentence protocol means we volunteered
the hardest possible test: `docs/SOTA_GAP_ANALYSIS.md` section 2a notes that no commercial vendor
publishes this control and only a handful of 2026 papers implement it. **Nothing in this submission
is harder to counterfeit than an error bar with a stated resampling unit.**

**How to deliver it.** Lead with the interval before a judge asks for it. Then immediately give
69.2%, because that is what the system actually does, and 13.2% is only what a threshold tuned on
the attack could do. `docs/SPEAKER_S4.md` already has the correct framing and it should be lifted
verbatim.

### Rank 2. Prevention: the voice is never the last factor, and the invariant is in the code

**Verified.** Four rungs: streaming gate, live challenge from 160,000 combinations in the caller's
own language, out-of-band push to the claimed person's registered device, callback or operator
block. Enforced in `src/pramaan/stream.py` (`docs/SOTA_GAP_ANALYSIS.md` section 2b, row
"Prevention, not just detection"). The demo shows the clone the detector missed being blocked by
the device.

**Why it cannot be matched.** It is half the PS title, and the SOTA analysis records that no vendor
publishes a challenge space size and that step-up verification is a workflow feature rather than a
published mechanism. Another team can add a slide saying "and then we escalate" overnight. It
cannot add a rung whose correctness is independent of the detector, demonstrate it live, and
survive the follow-up question.

**The honest strengthener, and it must be said.** The challenge rung was measured in the parent
repo and **the result was negative**: pooled across seven channels in the honest deployment regime
it settled 60.5% of deferred calls and got 47.8% of those wrong, while the passive layer was
committing at 47.93% error (`docs/QA_PREP.md`, "Does the challenge really stop a live cloner?").
The lesson is the strongest sentence in the whole project: **a challenge amplifies a detector that
can already see the attack and cannot rescue one that cannot, which is exactly why the third rung
does not depend on the detector at all.** Pramaan itself has no challenge evaluation and
`eval/results.json` carries no challenge number. Say that provenance out loud. A judge who greps
for it will find nothing.

### Rank 3. Full offline on-device operation, with a fair third-party latency comparison

**Verified.** `rtf_cpu4` 0.046, `lat_cpu4` 185 ms, `cap_streams` 5.4 streams per core,
`cap_cores` 37 cores for 200 seats, `n_trainable` 2,049 parameters, demo runs with Wi-Fi off and
no CDN or model fetched at run time. `docs/SOTA_GAP_ANALYSIS.md` section 2b calls this "Pramaan's
clearest structural advantage", and notes **all seven named commercial systems are cloud APIs**.

**Why it cannot be matched.** Architecture, not effort. A team whose pipeline calls an API cannot
turn off the Wi-Fi tomorrow. And the comparison is externally sourced rather than self-reported:
Podonos, 14 August 2026, Corsound 0.035, Pindrop 0.076, Resemble 0.40, Reality Defender 1.52.

**Why it is rank 3 and not rank 1.** `docs/SOTA_GAP_ANALYSIS.md` section 4 is explicit that
streaming detection is no longer an unclaimed differentiator: Hydaway shipped streaming audio
detection in July 2026 and Modulate advertises near-real-time detection. The defensible claim is
narrower: "we stream, on-device, in Indian languages, over real telephony codecs, and we publish
where it breaks."

### The two that did not make the cut, and why

- **The tamper-evident audit ledger.** Real and implemented (`src/pramaan/ledger.py`, SHA-256 hash
  chain, live tamper demo). But a hash chain is a weekend feature, and under a Blockchain and
  Cybersecurity theme half the room will have some ledger. **It is a demo beat and a theme-fit
  answer, not a differentiator.** Its one genuinely strong line is refusing to build a token:
  "a token would not make a decision more auditable" (`docs/QA_PREP.md`). Keep it to 25 seconds.
- **Real telephony codec conditions.** Real: `n_conditions` 7 conditions at train and test time,
  with AMR-WB and EVS listed as absent rather than faked. But it is a data-engineering investment
  another team could claim in one bullet. **It is what makes rank 1 credible rather than a
  differentiator of its own**, and it should be delivered as a property of the evidence, not as a
  feature.

---

## 4. The honest-weakness register, and how to present each

**Principle.** Never apologise. State the measurement, then state the design that handles it. A
weakness paired with a number and a mitigation scores; a weakness paired with an adjective loses.
Every framing below is truthful against the cited file.

| # | Weakness | The one-sentence framing, truthful and strong |
|---|---|---|
| 1 | The passive detector misses `op_miss_unseen` 30.8% of clips from an unseen 2025 cloner at the shipped band | "Against a cloner released this year that we never trained on, the listener alone catches 69.2% and lets 30.8% through, which is published behaviour for every passive detector including the commercial ones, and it is the entire reason a high-value transfer is never cleared by the voice." |
| 2 | The headline rests on small n: 23 held-out clones, 127 genuine recordings | "13.2% with a 95% interval of 4.7% to 21.9%, and we print the interval rather than the point, because that cell is 23 clones and 127 genuine recordings and a cluster bootstrap over parent recordings is the honest way to size it." |
| 3 | Loudspeaker-to-microphone replay is the worst surface in the project: `rm_replay_mic_channel_heldout_eer` 18.2% held out, and 14.0% of genuine speech called synthetic | "The worst surface we have is a clip played through a speaker into a microphone: on a head that never saw that channel, 18.2% error and 14.0% false alarms against 1.1% on the telephony grid, and we print it because it is the path a judge is most likely to trigger by holding a phone up to the laptop." |
| 4 | EnCodec resynthesis is the hardest family: `gm_encodec` 24.4% EER, and `loo_worst_err` 45.1% committed-call error in the leave-one-out gate replay | "Neural codec resynthesis is our hardest family at 24.4% held out, and in the leave-one-out gate replay it is worse, 45.1% committed-call error, because the gate commits on it instead of deferring, and that cell is on the slide rather than cropped out." |
| 5 | Adversarial robustness is measured only in the black box | "We ran the Malafide attack class in its black-box form, 9 filters on 505 held-out spoof clips, and error stayed at 0.00% and the catch rate at 100.0% on every filter, all the way down to 9.3 dB where the filter is audible; the white-box gradient attack is unmeasured and we say so rather than implying the first result covers the second." (`NUMBERS.json`: `adv_n_filters` 9, `adv_n_spoof` 505, `adv_eer_worst` 0.00%, `adv_catch_worst` 100.0%, `adv_dist_min` 9.3 dB) |
| 6 | Cross-session consistency, a PS Key Component, is not built | "Not implemented, and the reason is the dataset and not the model: it needs a bank's enrolled recordings of that customer, the PS itself says 'where available', and it answers whether this is the same person as last time while we answer whether it is a person at all." |
| 7 | The challenge rung's only measurement is in the parent repo and it was negative | "Measured in the parent repository, not this one, and the result was negative: it settled 60.5% of deferred calls and got 47.8% of those wrong, which is why the rung that actually blocks the transfer is the one that does not depend on the detector at all." |
| 8 | Two training sources are non-commercial research licences | "IndicSynth and Meta MMS output are research licences, so this is not the production model; the architecture and pipeline are production-shaped and the production model retrains on licensed or self-generated data, which is a costed roadmap step rather than a hidden flaw." |
| 9 | Tamil and Telugu have no held-out cloner | "Bona fide Tamil and Telugu are in every test, but the unseen-cloner test is Hindi only because Chatterbox does not speak them, and a Tamil and Telugu held-out cloner, IndicF5, is first on the roadmap." |
| 10 | Absolute accuracy is behind the Indic state of the art | "SATYAM reports 3.27% EER on Indic-CodecFake (arXiv 2604.19949) and we are behind it on absolute accuracy, and we can tell you why: it uses a frozen Qwen2-7B decoder and does not run on a laptop, and we chose the architecture that keeps inference on the device." |
| 11 | No public baseline detector has been run on Pramaan's own data | "Nobody has run a public baseline on our data and we have not run ours on theirs, so we do not offer a cross-corpus accuracy comparison; that measurement is a named roadmap item, not a number we are willing to invent." |
| 12 | AMR-WB and EVS are missing from the codec grid | "Our toolchain cannot encode AMR-WB or EVS, so they are listed as absent with the reason per codec in `src/pramaan/channels.py`, never faked." |

**The one line that frames the whole register, for the video:** "We found the shortcut in our own
benchmark before anyone else did, published the number it cost us, and rebuilt on the harder test."
That refers to the A1 result recorded in `HONEST_LOG.md` on 2026-09-03, where a corpus-confounded
benchmark read 0.59% and the matched-pairs control on the same detector read 32.03%.

---

## 5. What half the room will also do, and how we must visibly differ

### What half the room will do

1. **Open with news statistics.** A deepfake fraud headline, a crore figure, a stock photo of a
   hooded person. `docs/RUBRIC_MAP.md` row 1 already names this trap.
2. **Ship a binary deepfake classifier.** Upload a WAV, get "FAKE 97%". Often a fine-tuned Wav2Vec2
   or AASIST on an English dataset, with a whole-file accuracy number above 95% and no held-out
   generator, no codec grid and no error bar.
3. **Claim real time without measuring it.** No real-time factor, no capacity arithmetic.
4. **Bolt a blockchain on**, because the theme says so, usually a token or a public chain write
   that does not make any decision more auditable.
5. **Stop at detection.** No prevention, despite it being half the PS title.
6. **Quote one accuracy number** with no confidence interval and no named test set.

### How we must visibly differ, in the first 60 seconds of the video

The first minute is where a judge decides what kind of team this is. It must contain, in order:

- **Seconds 0 to 12. The attack, not a statistic.** Play two audio clips: the same speaker, same
  sentence, one genuine and one cloned. Do not say which is which. Let the judge fail.
- **Seconds 12 to 25. The reveal and the thesis.** "The second one was a clone, made by a tool
  released this year. You could not tell, and neither can a detector reliably. Pramaan's answer is
  not a better ear. It is that the voice is never the last factor."
- **Seconds 25 to 45. The one number nobody else will show.** "Against that cloner our passive
  detector catches 69.2% and lets 30.8% through. We are telling you our miss rate in the first
  minute, because everything after this is built for the case where the detector is wrong."
- **Seconds 45 to 60. The system in one breath, plus the offline proof.** Four layers named, then
  the shot of the Wi-Fi being switched off before the demo starts.

**Forbidden in the first 60 seconds:** any statistic about deepfake fraud growth, any logo montage,
any accuracy number above 95%, the word "revolutionary", a title card longer than three seconds.

### Slide 1 must differ in one visible way

Slide 1 is a mandated title page, so the differentiation budget is one line. That line is the
subtitle, and it must carry the thesis rather than a product description. Current:
"Real-time voice-clone defence for high-value phone approvals, on the device, in Indian languages."
That is accurate and forgettable. **Replace it with the invariant:**

> **Pramaan, proof before approval. The voice is never the last factor.**
> On-device, Indian languages, real telephony. Every number on these slides is generated from one
> results file.

Both sentences do work no other title slide in the room will be doing: the first states a policy
guarantee, the second pre-empts the credibility question before slide 2.

---

## 6. Slide-by-slide content direction

**The template is fixed.** `ppt/SIH2026-IDEA-Presentation-Format.pptx` contains 7 slides. Slide 7
is "IMPORTANT INSTRUCTIONS" and its own text says to delete it before upload, which
`scripts/build_deck.py` already does. **Six slides, including the title slide. The headings are
fixed and must not be reworded.** The template's own instruction, quoted exactly: "You can only
use provided template for making the PPT without changing the idea details pointers (mentioned in
previous slides)." Export to PDF; the portal accepts nothing else.

The six headings and their placeholder prompts, read from the template XML:

| # | Fixed heading | What the placeholder asks for |
|---|---|---|
| 1 | SMART INDIA HACKATHON 2026 / TITLE PAGE | Problem Statement ID, Problem Statement Title, Theme, PS Category, Team ID, Team Name |
| 2 | IDEA TITLE | Proposed solution, detailed explanation, how it addresses the problem, innovation and uniqueness |
| 3 | TECHNICAL APPROACH | Technologies used, methodology and process for implementation, flow charts, images, working prototype |
| 4 | FEASIBILITY AND VIABILITY | Feasibility analysis, potential challenges and risks, strategies for overcoming them |
| 5 | IMPACT AND BENEFITS | Potential impact on the target audience, benefits (social, economic, environmental) |
| 6 | RESEARCH AND REFERENCES | Details and links of reference and research work |

The deck agent edits `scripts/build_deck.py`, never the .pptx. Below: the one argument each slide
must land, the evidence, and the visual that carries it.

---

**Slide 1. TITLE PAGE**
- **Argument.** This team states a guarantee, not a feature list.
- **Evidence.** The two subtitle lines from section 5 above. Fill Team ID, which the template asks
  for and the current deck omits.
- **Visual.** Nothing added. Keep the template chrome intact. One line of blue, one of grey.
- **Change from current:** replace the descriptive subtitle with the invariant line; add Team ID.

---

**Slide 2. IDEA TITLE**
- **Argument.** Detection is a router, not a judge, and diversity is a measured design rule.
- **Evidence.** Left column: the four layers, one decision each (Listener with `n_trainable` 2,049
  trained parameters, Gate with `min_commit` 1.5 s first decision, prevention ladder with device
  approval, ledger). Right column: the diversity finding stated as variance collapse (`div_k1_min`
  4.5% to `div_k1_max` 39.6% at one family, span `div_k1_span` 35.1% wide; `div_kN` 13.2% at eight
  families, span `div_kN_span` 0.0% wide; `legacy_unseen` 35.9% for the previous build), plus the
  same-speaker same-sentence protocol in one line.
- **Visual.** The diversity curve with its min-max band, moved here from slide 4. **This is the
  single most persuasive image in the deck and it is currently on the wrong slide**, because it is
  the novelty argument and novelty is scored here.
- **Stat strip.** Change one tile. Current tiles are 13.2%, 1.5 s, 185 ms, 7 codecs, 0 bytes.
  **Replace "13.2% EER" with "69.2% caught, 30.8% missed, on a cloner from this year"** and keep
  13.2% in the chart caption. The first tile should say what the system does, not what a tuned
  threshold could do.

---

**Slide 3. TECHNICAL APPROACH**
- **Argument.** Every arrow in this architecture has a number on it, and the hardest part is the
  threshold.
- **Evidence.** The stack table as it stands is good. **Add one row that is currently missing:**
  the per-channel commit band, `band_clean` [0.010, 0.014] on clean against `band_worst`
  [0.036, 0.500] on G.723.1 6.3 kbps, derived from bona fide speech alone at a `fpr_budget` 2%
  false-positive budget, never hand-set. Keep the frozen-versus-fine-tuned justification with the
  Pascu et al., Interspeech 2024 citation. Keep the "deck generated from results.json" line.
- **Visual.** The architecture diagram, with data shapes on the arrows and the four rungs drawn as
  a ladder rather than a list, so prevention is visible as structure. `docs/RUBRIC_MAP.md` row 4
  names "a block diagram with no numbers on the arrows" as the trap.

---

**Slide 4. FEASIBILITY AND VIABILITY**
- **Argument.** We measured our own failures and priced the repair.
- **Evidence.** Keep "built with almost nothing" (1 laptop, no GPU, zero budget, `audio_minutes`
  229 minutes, 8 generator families built locally). Keep the three risks with measured answers.
  **Add two things.** First, the confidence interval on the headline: `unseen_eer_ci` 13.2%
  (95% CI 4.7% to 21.9%) on 23 clones and 127 genuine recordings. **No other deck in the room will
  have an error bar.** Second, the black-box adversarial result in one line: `adv_n_filters` 9
  Malafide-class filters on `adv_n_spoof` 505 held-out spoof clips, EER `adv_eer_worst` 0.00%,
  catch rate `adv_catch_worst` 100.0%, white-box unmeasured and stated as such.
- **Visual.** The generator-by-codec heatmap, with the red cells left red. Caption it: "A grid with
  no red cells is a grid where nobody ran the hard test."
- **Remove from this slide:** the diversity curve, which moves to slide 2.

---

**Slide 5. IMPACT AND BENEFITS**
- **Argument.** The error points away from the customer, and it runs where the audio already is.
- **Evidence.** `op_fpr_allchan` 1.1% false alarms across `n_bona_allchan` 3,570 genuine recordings
  on all `n_channels_scored` 7 channels, `op_fpr_worst` 1.6% on the worst (G.726 32 kbps),
  `op_fpr_clean` 0.4% clean. Decision at `min_commit` 1.5 s. Zero bytes of audio leaving the
  premises. `cap_streams` 5.4 calls per core and `cap_cores` 37 cores for 200 seats. The business
  model as the decay curve: `ad_shotsN` 12 recordings, `ad_base` 18.8% to `ad_eerN` 0.0%.
- **Add, and this is the biggest single gain available on any slide:** the Podonos latency
  comparison table. Four rows, one column, one date. Pramaan 0.046 on a laptop CPU offline;
  Corsound 0.035; Pindrop 0.076; Resemble 0.40; Reality Defender 1.52, all cloud APIs, Podonos
  benchmark, 14 August 2026. Label the column "real-time factor" and nothing else. **Do not put an
  accuracy column next to it.**
- **Visual.** Split: console screenshot on the left, the latency comparison bar on the right with a
  vertical line at 1.0 marked "cannot keep up with a live call".

---

**Slide 6. RESEARCH AND REFERENCES**
- **Argument.** We can name what beats us, which is why you can believe what we claim.
- **Evidence.** Keep the research list and the full model and dataset table with licences. **Add
  three named reference points that are currently absent from the deck:** SATYAM at 3.27% EER on
  Indic-CodecFake with its own AASIST baseline at 12.47% (arXiv 2604.19949); Wav2DF-TSL at 6.83%
  EER on In-the-Wild (arXiv 2509.04161); and the RADAR 2026 SSL-AASIST baseline at 42.6% EER on a
  multilingual media-transformed eval set (arXiv 2605.09568). Label the block "reference points,
  not comparisons: different corpora, and we have not run these on our data". Keep the CNAP under
  TRAI line, since it is the India-relevant caller-trust primitive and complements rather than
  competes.
- **Visual.** Keep the two-column layout and the full-width roadmap band at the bottom.
- **Guardrail.** Naming SATYAM as ahead of us on absolute accuracy is a criterion-2 point, per
  `docs/SOTA_GAP_ANALYSIS.md` section 4. Do it in one sentence with the architecture reason.

---

## 7. Video beat sheet direction

**Constraint: under ten minutes, six speakers, all speaking.** Target 9:15 of content, which leaves
margin. The existing `docs/PRESENTATION_SCRIPT.md` is a live-stage script for a 10-minute slot plus
2 minutes of Q&A. A video has no Q&A, so **the two minutes that were Q&A become proof**, and the
demo gets longer rather than shorter. Video also allows cuts, so the demo must be continuous and
visibly uncut where it matters, with an on-screen clock or a visible Wi-Fi-off shot to prove it.

| Beat | Speaker | Time | What it proves |
|---|---|---|---|
| 1. The cold open | S1 | 0:00 to 0:25 | That the judge cannot tell. Two clips, same speaker, same sentence, one cloned. No narration over them. Then the reveal. |
| 2. The thesis and the miss rate | S1 | 0:25 to 1:10 | That this team leads with its own weakness. The five PS commitments, then "the voice is never the last factor", then 69.2% caught and 30.8% missed on an unseen 2025 cloner, stated in the first minute. |
| 3. The four layers | S2 | 1:10 to 2:20 | That the system is a router, not a classifier. Listener (2,049 trained parameters on a frozen 300M frontend, and why), Gate (1.5 s, commit-or-defer, per-channel band), ladder, ledger. One decision named per layer. |
| 4. What is new | S2 | 2:20 to 3:00 | Novelty. The diversity scaling law as variance collapse: 4.5% to 39.6% at one family, 13.2% at eight, previous build 35.9%. Plus same-speaker same-sentence. Plus one sentence naming the prior art we did not invent. |
| 5. Demo, genuine caller | S3 | 3:00 to 3:30 | That it streams and that it refuses to guess. Wi-Fi visibly off first. Gate silent for 1.5 s by construction, then commits genuine, and the transfer is still held. |
| 6. Demo, known clone | S3 | 3:30 to 4:05 | That it is fast and decisive on what it knows. Commits synthetic at 1.5 s, 185 ms per update on CPU, blocked before the first sentence ends. |
| 7. Demo, the 2025 clone it may miss | S3 | 4:05 to 5:25 | **The centrepiece.** The unseen cloner, same speaker and sentence as the genuine pair. Say the true origin out loud. Whatever the score does, narrate it honestly, then run the challenge and the device push, and show the transfer blocked by a factor that is not the voice. |
| 8. Demo, the ledger tamper | S3 | 5:25 to 5:50 | Theme fit, done honestly. Edit block 2, verify, every later hash breaks. One sentence on why there is no token. |
| 9. The evidence | S4 | 5:50 to 7:20 | That the numbers are measured, not vibed. The diversity chart, the codec grid with its red cells, the confidence interval 4.7% to 21.9% and how it was computed, the repair cost 12 clips from 18.8% to 0.0%, and the worst false-alarm cell 0.79% on G.723.1 named with its channel. |
| 10. The weakness register | S4 | 7:20 to 7:45 | Candour paired with measurement. Three in thirty seconds: the replay-microphone surface at 18.2% held out with 14.0% false alarms, EnCodec at 24.4%, and the black-box-only adversarial result with the white-box gap named. |
| 11. Scale and the fair comparison | S5 | 7:45 to 8:40 | That it deploys. 5.4 calls per core, 37 cores for 200 seats, no GPU, zero bytes leaving the premises, 1.1% false alarms across 3,570 genuine recordings on all 7 channels. Then the Podonos real-time-factor table with the date, latency against latency only. |
| 12. Sustainability | S5 | 8:40 to 9:00 | That it keeps working. The decay curve as the business model, plus the licence path stated before anyone asks. |
| 13. Research base and roadmap | S6 | 9:00 to 9:40 | That the team knows the field. Name what beats us (SATYAM 3.27% on Indic-CodecFake, with the architecture reason), name what we borrowed, then the four roadmap items: more generators, more languages with held-out cloners each, a published head-to-head on our own data, one live contact centre. |
| 14. Close | S6 | 9:40 to 9:50 | "Pramaan: proof before approval. Every number you just saw is generated from one results file by one script." |

**Direction notes.**

- **Beats 5 to 8 are 2:50 of continuous demo**, which is the largest single block in the video and
  should be. The prototype criterion and the impact criterion are both bought here.
- **Do not cut inside a demo beat.** If a score moves, let it move on camera. A cut during a live
  score is the one thing that makes a judge suspect the whole video.
- **Show the true origin of every sample on screen**, which the console already prints under the
  source selector. Say it out loud as well.
- **Beat 7 has two valid endings and both are strong.** If the gate commits synthetic: "caught, on
  a cloner it has never seen, and that is what eight families bought us." If it does not: "the
  passive layer reads this clone as close to genuine, which is what the literature says happens to
  every detector including the commercial ones, and it is why the next two rungs exist." Script
  both, deliver whichever is true. Never re-record to get the friendly one.
- **No music under the demo.** Music under a live technical demonstration reads as production
  covering for substance.
- **One on-screen lower third per speaker**, name and the one thing they own. Nothing else animated.

---

## Appendix: cross-artifact sweep, to run before upload

The standing method requires numbers to agree across pitch, README, dashboard and demo. Three
discrepancies were found while writing this file, and they must be resolved before submission.

1. **`docs/SOTA_GAP_ANALYSIS.md` is partly stale against `NUMBERS.json`.** Section 1 says "a 29.9%
   clean EER cell for EnCodec resynthesis"; `NUMBERS.json` `gm_encodec` says **24.4%**. Section 1
   also says "the training set is 6 generator families and 2,069 spoof clips"; `NUMBERS.json` says
   `n_seen` **8** families and `n_spoof` **2,919**. Section 2b says adversarial robustness is
   "None measured", which section 3 (G8) then contradicts with the completed Malafide sweep.
   **`NUMBERS.json` wins in every case.** SOTA_GAP_ANALYSIS is an internal research file and is not
   quoted outward, but nobody should read a number off it.
2. **`scripts/build_deck.py` and `docs/PRESENTATION_SCRIPT.md` are behind `docs/SPEAKER_S1.md`
   through `SPEAKER_S6.md`.** Confidence intervals, the Malafide result, the Podonos latency
   comparison and the SATYAM reference point all appear in the speaker files and in none of the
   generated deck or the master script. The speaker files are the current state of the argument.
3. **Team ID is absent from slide 1.** The template asks for it explicitly.
