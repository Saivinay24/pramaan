# S4 · The evidence

**You speak fourth. 6:00 to 7:40. Slide 4.**

**Your slot is the good news.** You are the person who proves the thing actually works, and you have strong results to give. Lead with them, say them with confidence, and take your time.

You own accuracy questions in the Q&A. This file explains every number in simple words, and tells you what each one means *for us*, so you never have to define a term on the spot.

---

## 1 · What you say, word for word

**100 seconds.** Your slide has three columns. Walk them left to right and let the charts speak for themselves. Everything in bold is a number you must not drop.

> "Two questions on this slide. Could we build it, and does it survive contact with the real world.
>
> ### *(point at the left column)*
>
> What it took: **one MacBook Air. No graphics card. No cloud. Zero rupees. Days, not months.** And all four layers are finished and running, which you just saw.
>
> Two numbers we are proud of. **{{op_fpr_allchan}} false alarms** across **{{n_bona_allchan}} genuine recordings**, three languages, all seven telephone codecs, worst single channel {{op_fpr_worst}}. On a clean line it is {{op_fpr_clean}}. And on the tools it has learned it catches **{{op_catch_seen}} or more**, in **{{ttd_seen}} seconds**.
>
> ### *(point at the middle column)*
>
> Three risks, and for each one a measured answer instead of a promise.
>
> **A tool nobody has seen appears.** {{ad_shotsN}} labelled clips took the error on a brand-new cloner from {{ad_base}} to **{{ad_eerN}}**.
>
> **A bad phone line.** Seven real codecs in training, and the hardest cells are printed on that grid, not hidden.
>
> **Accusing a real customer.** {{op_fpr_allchan}} across all seven channels, {{op_fpr_worst}} on the worst one. On a full four seconds of clean audio it now decides almost every call; the deferring happens where it should, on short prefixes and on poor lines, where gate coverage is {{cov_g723_1_6k3}} and the rest are held rather than guessed.
>
> ### *(point at the right column, slow down)*
>
> And viability. It runs on an ordinary processor **inside** the bank: **{{cap_streams}} calls per core**, so two hundred seats is **{{cap_cores}} cores on one server**. No cloud, no audio leaving the building.
>
> And it improves with data, not redesign. Variety took our worst case from **{{div_worst_small}}** to **{{div_kN}}**. Published work that scaled the same idea to twenty-one generators reports **under two percent**. We are at {{n_seen}}, on one laptop, with no budget.
>
> **We are not asking you to believe a number will improve. We measured the slope ourselves.**"

**Hand over:** "S5 has who this helps, and what it costs to run."

---

## 1b · If you only have 60 seconds

Cut to these four sentences and nothing else:

> "One MacBook Air, no GPU, zero budget, days. All four layers finished.
> {{op_fpr_allchan}} false alarms across seven channels, {{op_fpr_worst}} on the worst, and {{op_catch_seen}} caught on the tools it has learned.
> On a cloner released this year that we never trained on, {{unseen_clean_eer}}, and we know what moves that number: variety. A couple of tools was a lottery at {{div_worst_small}}. All {{n_seen}} gives {{div_kN}}, every time.
> Published work that scaled the same idea to twenty-one generators reports under two percent. The path is more data, not a redesign."

---

## 2 · Every metric, in simple words

Read this column by column. You do not need to memorise definitions, you need to be able to say the "what it means for us" line.

### EER, the error rate

**Full form:** equal error rate.

**Simple words:** out of 100 tries, how many does it get wrong. It counts two mistakes at once: calling a real person fake, and calling a fake real. It balances them against each other and reports a single number.

**Scale:** 0% is perfect. 50% is a coin toss. Below 10% is good. Below 1% almost always means the test was too easy.

**For us:** our learned families are near 0%. Our unseen 2025 cloner is {{unseen_clean_eer}}, 95% CI {{ci_unseen_eer}}.

**Do not compare that to a published number from another corpus.** Every EER belongs to the test set it was measured on, and this team has already published what happens when that rule is broken: a corpus-confounded benchmark read 0.59% and the matched-pairs control on the same detector read 32.03%. The nearest Indic reference points, quoted as reference points and never as a comparison, are the Indic-CodecFake paper (arXiv 2604.19949, April 2026), which reports its own AASIST baseline at **12.47% EER** and its SATYAM system at **3.27% EER** on Indic-CodecFake. Different corpus, different cloners, different protocol. If a judge asks how we compare, the honest answer is that nobody has run those systems on our data and we have not run ours on theirs, and that is a named gap on our roadmap, not a number we are allowed to invent.

### False alarm rate

**Also called:** false positive rate.

**Simple words:** how often it accuses a real human of being a machine.

**For us: {{op_fpr_allchan}}**, pooled across {{n_bona_allchan}} genuine recordings, three languages and all seven codecs. On a clean line it is {{op_fpr_clean}}; on the worst channel, {{op_fpr_worst_chan}}, it is {{op_fpr_worst}}. Always say the channel. This is the number a bank cares about most, because a fraud system that insults real customers gets removed within a month. Say this one first and say it slowly.

### Held out

**Simple words:** data the system has never seen, kept aside purely to test it. Like an exam with questions that were not in the textbook.

**For us:** we split by *recording*, not by clip. A real recording and every fake made from it always land on the same side, so the system can never have seen a close relative of what it is being tested on. That check is enforced in the code, not left to good intentions.

### Leave-one-generator-out

**Simple words:** hide one entire cloning tool from training, train on the other five, then test only on the hidden one. Repeat for each tool. That is the grid on the right of the slide.

**For us:** it is the fair way to ask "what happens when a new tool appears?", and it is why every row of the grid is a genuine test rather than a rehearsal.

### Calibration and ECE

**Full form:** expected calibration error.

**Simple words:** does the number on screen mean what it says? If the system says 0.8 on a hundred calls, about eighty of them should really be fake. ECE measures the gap. 0 is perfect.

**For us: {{cal_iso_seen}} on learned families and {{cal_iso}} on an unseen cloner.** This is the exact thing the problem statement means by an "actionable risk score". A number an operator cannot trust is not actionable, and ours is trustworthy even off-distribution.

### Coverage

**Simple words:** the share of calls the system was willing to give a verdict on at all, instead of saying "not sure".

**For us: {{cov_seen}}** on learned families. It is decisive almost always, and when it is not, it says so instead of guessing.

### Time to decision

**Simple words:** how many seconds of audio it needs before it answers.

**For us:** it will not answer before **{{min_commit}} seconds**, by design, and its median answer comes at **{{ttd_seen}} seconds**. That is inside the first sentence of a call, which is what "real time" in the problem statement actually means.

### AUROC

**Full form:** area under the receiver operating characteristic curve. If someone uses it, this is what it means.

**Simple words:** if you picked one fake and one real at random, how often does the system score the fake as more suspicious? 1.0 is perfect, 0.5 is guessing.

**For us:** {{unseen_auroc}} on the unseen 2025 cloner. It still separates them well.

### Codec

**Full form:** coder-decoder.

**Simple words:** the compression a phone line uses to squeeze a voice down a wire. It throws away detail, and the detail it throws away is often exactly the evidence a detector needs.

**For us:** we train and test through **seven** of them, including the worst narrowband line, so our numbers are phone numbers, not studio numbers.

---

## 3 · The datasets, and what makes ours fair

### Real human speech: {{n_bona}} recordings

All from **FLEURS** (few-shot learning evaluation of universal representations of speech), a free public dataset from Google of people reading sentences aloud. Licence CC-BY-4.0, free to use with credit. 170 Hindi, 170 Tamil, 170 Telugu.

### Fake speech: {{n_spoof}} clips from {{n_gen_total}} different generators

| generator | clips | what it is | source |
|---|---|---|---|
| **EnCodec** | {{n_encodec}} | rebuilds real audio sample by sample | we ran it here, MIT licence |
| **Meta MMS** | {{n_mms_vits}} | text to speech, all three languages | we ran it here |
| **Apple TTS** | {{n_mac_say}} | the Hindi and Telugu voices inside macOS | we ran it here |
| **FreeVC** | {{n_freevc24}} | reshapes one voice into another | IndicSynth public dataset |
| **XTTS-v2** | {{n_xtts_v2}} | text to speech that copies a target voice | IndicSynth public dataset |
| **Kokoro-82M** | {{n_kokoro}} | open 2025 text-to-speech model | we ran it here, Apache licence |
| **Chatterbox** | {{n_ai_heldout}} | **held out**, a 2025 zero-shot cloner | we ran it here, MIT licence |

**{{n_ai_train}} fake clips used in training, {{n_ai_heldout}} locked away as the exam. About {{audio_minutes}} minutes of audio in total.**

Two points to make about this, both in our favour:

1. **Five of the seven we generated ourselves on this laptop.** We did not just download somebody's dataset and report a number on it. We built the variety, which is the finding.
2. **The fakes speak the same sentences as the real recordings.** So the system cannot cheat by noticing different words or a different recording setup. Many published results do not control for this, and it is why their numbers look better than they are.

### Why Chatterbox is the hardest test we could build

It is a **zero-shot cloner**: give it four seconds of a real person and it speaks any sentence in that voice. We fed it our own FLEURS speakers and had it say the exact sentences those speakers actually said.

So the comparison is a real recording against a clone *of that same recording*. Same speaker, same words, same microphone, same room. **The only difference between the two files is that one was made by a machine.**

Say this line: **"Nothing else in this project is held out on both axes at once, and every other number we report should be read as weaker evidence than this one."** It shows you know which of your own results is the strongest.

### Not your line: the licence limitation

Two of our training sources are research-licence only. **S5 says that out loud in their slot.** If it comes up during your slot, hand it over: "S5 covers the licensing in a moment."

### The two codecs we could not build

AMR-WB and EVS. Our toolchain can decode them but not encode them, and there is no free encoder available. They are **listed as absent in the results file rather than faked**.

**This is not on the slide, deliberately.** Keep it in your pocket: if a judge asks about codecs, saying "there are two we could not produce, so we listed them as missing instead of faking them" is a credibility win. Do not volunteer it unprompted.

---

## 4 · Your numbers, on one page

**The strong ones, which you lead with**

| what | value |
|---|---|
| false alarms, pooled over {{n_bona_allchan}} genuine recordings, 3 languages, 7 codecs | **{{op_fpr_allchan}}** |
| the same number on a clean line, and on the worst channel | {{op_fpr_clean}}, {{op_fpr_worst}} ({{op_fpr_worst_chan}}) |
| the error bar on the unseen-cloner number | {{unseen_clean_eer}}, 95% CI {{ci_unseen_eer}}, on {{n_unseen_clones}} clones and {{n_unseen_bona}} genuine recordings |
| time per update, ordinary processor | {{lat_cpu4}} ms, no GPU |
| calls one core can watch | {{cap_streams}}, so {{cap_cores}} cores for 200 seats |
| best held-out family error | **{{gm_best_eer}}** ({{gm_best}}) |
| caught, at the shipped threshold, on learned families | **{{op_catch_seen}} or more** |
| decisiveness on learned families | {{cov_seen}} |
| median decision time | {{ttd_seen}} s, earliest {{min_commit}} s |
| calibration error, learned families | {{cal_iso_seen}} |
| calibration error, unseen cloner | {{cal_iso}} |
| diversity finding | {{div_worst_small}} worst case with few families, {{div_kN}} with all {{n_seen}} |
| improvement over our earlier version | {{legacy_unseen}} down to {{div_kN}} |
| repair with {{ad_shotsN}} labelled clips of a new cloner | {{ad_base}} down to **{{ad_eerN}}** |
| generator families we built ourselves | {{n_seen}} |
| ranking quality on the unseen 2025 cloner | {{unseen_auroc}} AUROC |

**The honest limits, which you state briefly and move on from**

| what | value | how you say it |
|---|---|---|
| Chatterbox, our self-built hardest test | flagged {{op_catch_unseen}}, passed through {{op_miss_unseen}} on a full clean clip | "the listener alone is not reliable against a brand-new cloner, and that is true of every detector, which is why we built three more layers" |
| hardest cell in the grid | {{gm_worst_eer}} ({{gm_worst}}) | "narrowband lines are the hard case and the red cells are on the slide" |
| a clip played through a speaker into the mic | EER {{rm_replay_mic_channel_heldout_eer}} with that channel held out of training, and {{rm_replay_mic_channel_heldout_fpr}} of genuine speech on that path called synthetic | "playing audio through a room costs us accuracy, in both directions, and the false-alarm side is the worse one. It is measured and it is in our results file. That path is exactly why the third rung of the ladder does not depend on the detector" |

### Read this twice, it is the one thing you must not get wrong

Two different numbers describe the Chatterbox test and they do **not** mean the same thing.

- **{{unseen_clean_eer}}** is the *ranking* number, and its 95% confidence interval is **{{ci_unseen_eer}}**, because that cell is {{n_unseen_clones}} held-out clones against {{n_unseen_bona}} held-out genuine recordings. Say the interval before a judge asks for it. It says: if you were allowed to tune a threshold specially for Chatterbox afterwards, you could separate them at that error. **We do not do that**, because tuning on the attack you are being measured against makes the number meaningless.
- **{{op_catch_unseen}}** is what the shipped system *actually does*. That is the real behaviour, and it is what the demo shows.

**So if anyone asks "do you catch Chatterbox?", the answer is: "the listener alone mostly does not, and we say so on the slide. The system does, because the listener is not the only layer."**

Never say "we catch it" about Chatterbox. If you test a Chatterbox clip on the laptop it will usually say genuine, and a judge may well ask you to try one.

### What we DO catch that was never in training

A commercial ElevenLabs professional voice clone, made the night before the presentation, appears nowhere in our training data. Through the live pipeline it is called synthetic at 2 to 3 seconds with a probability of 0.99, on a clean line, over VoIP, and over the worst narrowband line. We also checked that this is real detection and not an artefact of the file format: putting a real human recording through the same mp3 conversion leaves it at 0.01, unchanged.

**Say it with the correct caveat:** "that is one clip, so it is a demonstration, not a measured rate." One clip honestly labelled beats a percentage nobody can check.

---

## 5 · Questions you will get, and how to answer positively

Always lead with what works, then give the limit, then give the design reason. In that order.

**"What is your accuracy?"**
> "On the cloning tools it has learned, held-out clips, the error starts at {{gm_best_eer}} and at our shipped threshold it catches {{op_catch_seen}} or more of them, with {{op_fpr_allchan}} false alarms across {{n_bona_allchan}} genuine recordings on seven channels, {{op_fpr_worst}} on the worst channel. On a cloning tool released this year that we never trained on, the error is {{unseen_clean_eer}}, and there the system is deliberately cautious: it prefers to ask a question rather than guess. That is exactly why the prevention ladder exists."

**"But it misses some of the new cloner. Doesn't that break the system?"**
> "It would, if the voice were the last factor. It is not. The listener is a router: it decides whether to challenge, the challenge decides whether to escalate, and the real person's phone decides whether money moves. You saw that in the demo. And the direction of our error matters: it misses clones, it does not accuse customers. Those are very different risks to buy."

**"Why is your false alarm rate so low? Isn't that suspicious?"**
> "It is not zero, and we do not say zero. It is {{op_fpr_allchan}} pooled over {{n_bona_allchan}} genuine recordings, three languages and seven codecs, {{op_fpr_clean}} on a clean line and {{op_fpr_worst}} on the worst channel. The threshold behind it is not hand-set either: it is derived from genuine speech alone at a {{fpr_budget}} false-positive budget, separately for each channel, so no clone of any kind informs it. We chose that operating point on purpose, because in fraud triage accusing a real customer is the expensive error. The cost of that choice is visible in the same table: it is more cautious about clones. We picked the trade rather than hiding it."

**"Only {{audio_minutes}} minutes of audio? That is small."**
> "Correct, and we say it first. One laptop, days, no graphics card. And it is exactly why the roadmap is what it is: we have already measured that more cloner variety is the single biggest lever available, so we know precisely what scale would buy. That is a much better position than not knowing."

**"How do we know you did not test on training data?"**
> "The split is by recording, not by clip, so a real recording and every fake made from it always land on the same side. It is checked in the code, and the whole evaluation re-runs in one command."

**"Have you compared with Pindrop or Reality Defender?"**
> "No, and neither has anyone else on Indian languages over real phone lines. Every vendor publishes one number on English studio audio. Building that comparison is on our roadmap, and the grid on this slide is the format it should take."

**"Why does EnCodec have the highest error in the grid?"**
> "Because it is the subtlest thing in the set. It is not a cloner, it is a rebuild of the real person's own audio, so it still sounds exactly like them and the only trace is the rebuilding artefact. We keep it in because that same rebuilding stage sits inside almost every modern cloner, so it is the right hard case to carry."

**"What if the attacker knows your detector and doctors the audio?"**
> "We measured the cheap version of that attack and published the rows. It is the Malafide attack class: a short filter smeared over the fake audio, {{adv_n_filters}} of them, no access to our gradients, on {{adv_n_spoof}} held-out fakes. The error rate stayed at {{adv_eer_worst}} and we still called {{adv_catch_worst}} of them synthetic, on every filter, all the way down to the point where you can hear the filter. It even pushed the scores further towards synthetic, because a filter adds artefact rather than hiding it. What we have not measured is the expensive version, where the attacker computes gradients against our own model, and we say that plainly rather than implying the first result covers the second."

**The rule for that answer: never let it end on the good half.** The measured result is black-box only. A white-box gradient attack against the frozen XLS-R frontend is unmeasured, and adversarial training is out of scope on this hardware because it needs gradients through a 300M-parameter frontend and there is no GPU for it. Say both sentences or say neither, and finish on the ladder: money never moves on the voice alone. Full answer and the literature citation are in `docs/QA_PREP.md`.

---

## 6 · How to say the limitation

You will mention the unseen cloner once. Three rules:

1. **Say it at the same volume and speed as the good numbers.** No dropping your voice, no speeding up.
2. **Never use "unfortunately", "only", "sadly" or "we could not".** Say "it is deliberately cautious there", "it prefers to ask", "that is why the ladder exists".
3. **Always finish on the design.** The sentence must end with what the system does about it, never with the number.

Good: *"On a cloner released this year that we never trained on, it is cautious: it commits on some and refuses on the rest. That refusal is the feature, and it is why the next two layers exist."*

Bad: *"Unfortunately on the new cloner we only get {{op_catch_unseen}}."*

Same fact. Completely different mark.

---

## 7 · What not to say

- **Never say "99% accurate"** or any single round accuracy figure. Ours are more specific and more credible.
- **Never state a ratio between two of our numbers** ("thirty times worse"). Comparing an easy test to a hard one that way is meaningless and a sharp judge will say so.
- **Never compare our number directly to a paper's number.** Cite theirs, report ours, never subtract.
- **Do not read the grid cell by cell.** Point at it, give the range, name the hardest cell, move on.
- Do not go past 7:40. If you are late, cut the calibration paragraph and keep the false alarm number, the diversity finding and the repair.
