# VIDEO_SCRIPT

**SIH 2026 National round. Demo video, six speakers, recorded voice over, no AI voice anywhere.**

Rewritten 19 September 2026 against the rebuilt operator console (`docs/UI_AUDIT.md`, screenshots
in `docs/ui_shots/`). The brief is `docs/NATIONAL_STRATEGY.md` sections 2, 3, 4, 5 and 7. Numbers
come from `docs/NUMBERS.json`.

**Total runtime 9:29. Hard limit 10:00. Headroom 0:31.**

## The structural rule of this version

**There are no presentation slides in this video.** The deck is a separate submission artifact and
it does not appear on screen for one frame. A demo video demonstrates the product, so **every visual
in this film is the running operator console**, with exactly two exceptions: a black cold-open card
over the two audio clips at 0:00, and a black closing title card at 8:37.

If a beat cannot be shown in the console, it is either spoken over a console view that is honestly
related to it and named as such, or it is cut and recorded in section 7.

## Rules that override everything else in this file

1. **Every number spoken here exists in `docs/NUMBERS.json`, or is an external figure whose source
   is named aloud in the same sentence.** The Podonos figure is the only external number and the
   benchmark and its date are spoken. If a number is not on this page, nobody says it.
2. **Live risk values read off the console during the demo (0.010, 0.990, 0.028) are read from the
   screen, not claimed as evaluation results.** The speaker says what the screen says. If the screen
   shows something else on the day, the speaker says that instead. The challenge space, 160,000
   phrases, is read from the About panel of the running process.
3. **The headline is 69.2% caught and 30.8% missed**, and it is spoken inside the first minute.
   13.2% is the tuned-threshold figure and is **always** spoken with its interval, 4.7% to 21.9%.
   **Nobody may imply the system catches everything.**
4. **No em dashes anywhere.** Short sentences. One idea per sentence.
5. **Never re-record a demo beat to get a friendlier score.** If the passive layer is fooled, that is
   the beat. The script already assumes it is.
6. **No deck, no diagram, no lower-third full of numbers.** One lower third per speaker, name and the
   one thing they own. Everything else on screen is the console.

## Timing arithmetic method

Read rate assumed throughout: **145 words per minute** for Indian English technical narration at a
natural pace. That is **2.4167 words per second**. Every duration below is `words / 2.4167`, plus the
beat's **held time** (seconds of screen or audio with no narration over it), plus a short breath.
A written numeral counts as one word, which is the same convention the previous version used; the
slack that buys is absorbed by the breath budget and by the 1:13 of headroom.

| | |
|---|---|
| Total spoken words | **1,103** |
| Implied speech time | 1,103 / 145 x 60 = **456.4 s** |
| Held time, no narration | **40 s** |
| Breaths between lines | **29 s** |
| **Exact total** | **568.4 s** |
| **After per-beat rounding to whole seconds** | **569 s = 9:29** |
| Headroom to the 10:00 limit | **31 s (0:31)** |

---

## 1. Beat sheet

Every "On screen" cell below is a view of the running console at `http://127.0.0.1:8770`, except
beats 1 and 18.

| # | Spk | Start | Dur | On screen, exactly | The one claim it proves |
|---|---|---|---|---|---|
| 1 | S1 | 0:00 | 0:14 | Black card: "Same speaker. Same sentence. One of these is a clone." Two clips play, A then B, 5 s each. No narration over them. | The judge cannot tell. |
| 2 | S1 | 0:14 | 1:02 | **Live call tab at rest.** Line selector opened, all ten demo lines visible, then closed on `human_hindi`. Carrier selector opened, all seven carriers visible, then closed on VoIP Opus 24 kbps. Decision bar idle, "No call on this line", "Approval held until verified". Provenance caption top right. | This is an operator console, not a classifier demo, and it names the true origin of every recording. |
| 3 | S1 | 1:16 | 0:33 | **Prevention ladder panel**, full height, five rungs, panel note "The voice is never the last factor." Cursor rests on rung 1, then travels down to rung 5. | The miss rate is volunteered in the first minute, and the four rungs below the voice are why it is survivable. |
| 4 | S2 | 1:49 | 0:36 | **About panel**, scrolled to show Detector then Gate. Rows: Speech model, Layer read, Trained parameters on top (2,049), Generator families in training, Audio refresh, Earliest decision, Threshold band measured for. | Four layers, one decision each, and the process describes its own configuration rather than a slide describing it. |
| 5 | S2 | 2:25 | 0:22 | **Live call tab, Risk trace panel.** Carrier switched clean, then G.723.1 6.3 kbps, then back. The striped undecidable band on the log-odds meter visibly moves and widens. Facts table below: "Threshold band measured for". | The threshold is derived per carrier from genuine speech, not typed in. |
| 6 | S2 | 2:47 | 0:57 | **Evidence tab, "Error rate against training diversity, on a cloner never seen".** Hover the k=1 point, then the k=8 point, tooltips showing min to max. Shaded band visibly collapses. Panel footnote read on screen. | **Novelty.** Generator diversity is a measured design rule and it collapses variance. |
| 7 | S3 | 3:44 | 0:33 | Wi-Fi menu switched off on the menu bar, then **Live call tab**: `human_hindi`, VoIP Opus 24 kbps, Start monitoring. Risk trace runs, verdict "Reads genuine", ladder rung 1 green, "Approval held until verified" still red. | It streams, it refuses to guess before 1.5 s, and a genuine verdict still does not release the money. |
| 8 | S3 | 4:17 | 0:23 | **Live call tab**: `clone_xtts_v2`, same carrier. Verdict "Reads synthetic", decision bar red, facts table "Time to score one update" visible. | Fast and decisive on a generator family it has seen. |
| 9 | S3 | 4:40 | 1:03 | **Live call tab, uncut**: `pair_real_hindi` on clean, then `pair_clone_hindi` on clean. Pair B reads genuine and drifts. Then Issue challenge, challenge card with the Hindi phrase. Then Send device push, device card, "Not me". Decision bar goes red, ladder rung 5 "blocked". | **The centrepiece.** The passive layer is fooled by a 2025 cloner, and a factor that is not the voice blocks the transfer anyway. |
| 10 | S3 | 5:43 | 0:28 | **Audit tab**: Calls on record list, Event log with time, actor, event, detail, hash, chain status. Verify chain, pass. Alter a block on block 2. Verify again, chain broken, every later row "unverifiable". Restore. | Theme fit, done honestly, and no token. |
| 11 | S4 | 6:11 | 0:30 | **Evidence tab, "Error rate on a generator family held out of training".** Full heat map, all rows and all seven carrier columns. Hover the EnCodec row, then the bottom Chatterbox row. | The numbers are measured on the hard protocol, the red cells are on screen, and the headline carries an interval. |
| 12 | S4 | 6:41 | 0:07 | **Evidence tab, "Calibration error"** panel: raw, Platt, isotonic, with its footnote. | The score is a probability an operator can act on, which is what the problem statement asked for. |
| 13 | S4 | 6:48 | 0:27 | Scroll back to the **heat map**, then hold on its column headers. | Candour paired with a measurement: the worst surface we have is named, with its number, and the grid it is not on is named too. |
| 15 | S5 | 7:15 | 0:38 | **Evidence tab, "Scoring cost on this laptop"**: processor, window, median ms, real-time factor, including the 0.046 row, plus the capacity footnote. | It deploys on one commodity server, and the only cross-vendor comparison made is a fair one. |
| 16 | S5 | 7:53 | 0:33 | **Evidence tab, "Cost of adapting to a new cloner"**: 3 recordings, 12 recordings, error on the new cloner and on families already seen. | It keeps working, and the upkeep is costed rather than promised. |
| 17 | S6 | 8:26 | 0:19 | **About panel**, scrolled to Measurements then Network: Results generated, Clips measured, Cached embeddings, External requests "none". | Every number traces to one results file, and nothing leaves the machine. |
| 18 | S6 | 8:45 | 0:34 | **Evidence tab**, slow continuous scroll across all six panels, top to bottom, ending on the heat map. | The team knows the field, including what beats it. |
| 19 | S6 | 9:19 | 0:10 | Black title card: "Pramaan. Proof before approval." Then black. | The close. |
| | | **9:29** | | | |

### Direction notes for the editor

- **Beats 7 to 10 are 2:24 of continuous demo.** That is the largest block and it should be.
- **Do not cut inside a demo beat.** If a score moves, let it move on camera.
- **No music under beats 7 to 10.** None at all. Music under a live technical demonstration reads as
  production covering for substance.
- **Never cut to a slide.** If a beat runs short, hold on the console. Dead console is better than a
  deck.
- **Show the true origin of every sample.** The console prints it top right in the line bar. Hold on
  it for a beat before Start monitoring is pressed.
- **One lower third per speaker**, name and the one thing they own. Nothing else animated.
- **Beat 9 has a second ending.** If the gate commits synthetic on the day instead of being fooled,
  S3 records the alternate line given in that section. Never re-record to get the friendly one.
- **Beat 1 clip order:** genuine first, clone second. The reveal line in beat 2 depends on it.
- Optional B roll if a beat runs short: the **Call record** strip on the Live tab under S2 beat 4,
  and `10-live-dark-worst-carrier` (dark theme, G.723.1) under S4 beat 13.

---

## 2. Per-speaker scripts

Each section below is self contained. Read only your own section. Every line gives the words, the
target duration, and a delivery note.

### S1. The cold open, the console, and the miss rate

**Beats 1, 2 and 3. 0:00 to 1:49. Block length 1:49. 229 words, which at 145 wpm is 95 s of speech,
plus 10 s of clip audio you do not speak over, plus 4 s of breath.**

You are the first voice in the video. You are not selling. You are stating a fact the judge has
just experienced. Sit slightly forward, speak a little slower than feels natural, and put a full
stop where every full stop is printed.

---

**BEAT 1. 0:00 to 0:14. Black card, then two clips.**

`0:00 to 0:10` **Say nothing.** Two clips play, genuine first, clone second, about 5 s each. Do not
breathe audibly. Leave this space clean in your file: record 10 s of room silence here so the editor
can drop the clips in.

**Line 1.1** · 9 words · 3.7 s
> One of those two voices was not a person.

*Tone: flat, almost bored. No emphasis anywhere. You are not revealing a trick, you are stating a
fact. Pause a full second after "person" before you start beat 2.*

---

**BEAT 2. 0:14 to 1:09. The console at rest.**

**Line 1.2** · 22 words · 9.1 s
> The second one. A cloning tool released this year made it. You could not tell. Neither can most systems on the market.

*Tone: still flat. Stress "this year". Do not stress "could not tell", the sentence does that on its
own.*

**Line 1.3** · 53 words · 21.9 s
> In India, forty seven percent of adults have hit a voice scam, or know someone who has. That is double the global rate. Two in three say they would answer a distress call from a parent or a child. Most of those calls are not chasing a company. They are chasing a family.

*Tone: this is the only place in the video where you are allowed to sound like it matters. Do not
perform it. Slow down on the last two sentences and stop dead after "family". The numbers are from
McAfee's 2023 seven country survey, so if a judge asks, name it.*

**Line 1.4** · 34 words · 14.1 s
> This problem statement asks for five things. Detect during the call. Give a score an operator can act on. Prevent the transaction. Run on the device. Work in Indian languages over real phone lines.

*Tone: "Nothing here is a slide" is thrown away, not announced. Then five separate sentences, five
separate breaths. Land each one like an item on a checklist. Do not run them together. This is the
clarity mark and it is bought by the pauses, not the words.*

**Line 1.5** · 19 words · 7.9 s
> This is our operator console. Every line on it is a real recording, and it names the true origin.

*Tone: plain and proprietorial. The selector is open on screen while you say it, so let the screen
do the listing. Do not read the options aloud.*

---

**BEAT 3. 1:09 to 1:36. The five checks.**

**Line 1.6** · 24 words · 9.9 s
> The problem statement asks us to prevent, not just detect. So we built one rule. A voice on its own never releases the money.

*Tone: slow down on the last seven words. This is the thesis of the whole submission. Say it as a
rule, not as a slogan.*

**Line 1.7** · 45 words · 18.6 s
> Hold out any one of the cloning tools we train on, then retrain. Six of them score zero percent error. Against a 2025 cloner we never trained on at all, five point seven percent. Under a filter attack built to break detectors like ours, zero.

*Tone: these are results, so read them like results. Even pace, no lift at the end of any clause.
Say "five point seven percent" as full words. Do not stack them into one breath: four sentences,
four separate facts. Let the last "zero" sit for a beat before you move on.*

**Line 1.8** · 23 words · 9.5 s
> No single check should ever be enough to move money. So five sit behind ours, and the voice is only one of them.

*Tone: even. The cursor is moving down the five checks while you say it. Let it reach the last
one before you stop.*

**HAND OFF to S2 here.** End your file after line 1.8. Do not say a handover sentence. The cut does
that work.

---

### S2. The four layers, the threshold, and what is new

**Beats 4, 5 and 6. 1:49 to 3:44. Block length 1:55. 264 words, which at 145 wpm is 109 s of speech,
plus 6 s of breath.**

You own architecture. Your job is to sound like someone describing a system they built, not
someone reading a spec. You are narrating two console surfaces: the About panel, which is the
running process describing itself, and the Risk trace, which is the threshold moving. Breathe
between paragraphs.

---

**BEAT 4. 1:36 to 2:12. The About panel, Detector then Gate.**

**Line 2.1** · 12 words · 5.0 s
> Four layers, one decision each. This panel is the process describing itself.

*Tone: brisk. This is a heading, not a sentence. Then pause while the panel scrolls.*

**Line 2.2** · 39 words · 16.1 s
> The Listener asks whether the voice is synthetic. A frozen three hundred million parameter multilingual model, with two thousand and forty nine trained parameters on top. Fine-tuning memorises the cloners you hold. Freezing generalises, and keeps the GPU out.

*Tone: say "two thousand and forty nine" slowly, then pause. It sounds like a small number and it is
a design argument, so the next two sentences must land as the reason. Stress "memorises".*

**Line 2.3** · 42 words · 17.4 s
> The Gate asks whether it knows enough to answer yet. First verdict at one and a half seconds, and never while the score sits in the unsure zone. We work that zone out for every kind of phone line, from real speech.

*Tone: stress "never". The last sentence sets up the next beat, so do not drop your energy on it.*

---

**BEAT 5. 2:12 to 2:34. The Risk trace, carrier switched.**

**Line 2.4** · 31 words · 12.8 s
> Watch the striped zone when I change the phone line. On a clean line it sits between 0.010 and 0.014. On a 6.3 kilobit line it runs from 0.014 to 0.571.

*Tone: narrate, do not sell. "Zero point zero one zero", "zero point zero one four", "zero point
zero three six", "zero point five zero zero". The band moves on screen as you say it.*

**Line 2.5** · 24 words · 9.9 s
> Real human speech scores higher the harder the phone line squeezes it. So we measure the threshold for every line. Nobody typed it in.

*Tone: the last three words are the point of the beat. Drop your pitch on them.*

---

**BEAT 6. 2:34 to 3:25. The diversity curve.**

**Line 2.6** · 13 words · 5.4 s
> What is new is not the model. It is a measured design rule.

*Tone: a gear change. Slight lift. This is the novelty mark.*

**Line 2.7** · 35 words · 14.5 s
> This is the curve. Train on one cloning tool and your error on a cloner you have never seen is a lottery, 4.5 to 39.6 percent. Train on all eight and it is 13.2 percent.

*Tone: stress "lottery". **The interval is not optional and it is not an aside.** Say the numbers as
"four point five", "thirty nine point six", "thirteen point two", "four point seven", "twenty one
point nine".*

**Line 2.8** · 14 words · 5.8 s
> The shaded band is the spread. It collapses from 35.1 points wide to zero.

*Tone: the word that carries the claim is "collapses". The band is visibly narrowing on screen, so
say it once and let the picture finish the sentence.*

**Line 2.9** · 19 words · 7.9 s
> Our own earlier build, on two tools, sat at 35.9 percent. That is what getting this right is worth.

*Tone: say it as an admission, quickly, without drama. It is stronger for being thrown away.*

**Line 2.10** · 18 words · 7.4 s
> The footnote matters. The held-out cloner clones the exact recording it is scored against. Same speaker, same sentence.

*Tone: slow. "Same speaker, same sentence" is four words that a knowledgeable judge will recognise.
The footnote is on screen under the chart, so give it room to be read.*

**Line 2.11** · 17 words · 7.0 s
> Almost nobody runs that control. We run it on Indian speech, against a cloner from this year.

*Tone: even. Naming the limit of the claim is what makes the claim survive. Do not hedge further.*

**HAND OFF to S3 here.** End your file after line 2.11.

---

### S3. The demo

**Beats 7, 8, 9 and 10. 3:44 to 6:11. Block length 2:27. 277 words, which at 145 wpm is 115 s of
speech, plus 27 s of held screen time you do not speak over, plus 5 s of breath.**

You are narrating a screen. The held gaps below are where the score is moving and you are silent.
**Record the gaps as real silence in your file**, counted out, so the editor can align you to the
capture without stretching your voice.

Say the true origin of every sample out loud. The console prints it in the line bar.

---

**BEAT 7. 3:25 to 3:58. Genuine caller, Hindi, VoIP Opus 24 kbps.**

**Line 3.1** · 10 words · 4.1 s
> Wi-Fi is off. Nothing here is fetched from a network.

*Tone: throwaway, confident. Say "why fye". The shot does the proving.*

**Line 3.2** · 20 words · 8.3 s
> A real Hindi recording on a VoIP Opus line, streamed chunk by chunk. The screen names every sample's true origin.

*Tone: "Opus" is OH pus. See the pronunciation guide.*

`HOLD 7 s` **Silence.** The trace runs, the gate is quiet, then the verdict appears.

**Line 3.3** · 20 words · 8.3 s
> For the first one and a half seconds the gate refuses to decide. Then it reads genuine, on risk 0.010.

*Tone: "zero point zero one zero". Read it off the screen. If the screen shows another value, say
that value.*

**Line 3.4** · 10 words · 4.1 s
> And the transfer is still held. Device approval still required.

*Tone: this is the point of the beat. Stress "still", both times. The red "Approval held until
verified" pill is on screen next to a green verdict, and that contradiction is the product.*

---

**BEAT 8. 3:58 to 4:21. Clone, XTTS-v2, same carrier.**

**Line 3.5** · 12 words · 5.0 s
> Same pipeline. A clone from XTTS-v2, a family the model has seen.

*Tone: brisk. "ex tee tee ess vee two".*

`HOLD 7 s` **Silence.** The trace jumps and the decision bar turns red.

**Line 3.6** · 25 words · 10.3 s
> Synthetic at one and a half seconds, on risk 0.990. Blocked before the first sentence ended. The facts table prints the cost of one update.

*Tone: clipped, decisive, matching the screen. "Zero point nine nine zero". **Do not quote a
millisecond figure here.** The number is printed live in the facts table and the camera is on it.*

---

**BEAT 9. 4:21 to 5:21. The centrepiece. Do not cut inside this beat.**

**Line 3.7** · 26 words · 10.8 s
> Now the hardest test anyone can build. Same speaker as Pair A, same sentence, cloned by a tool released this year that we never trained on.

*Tone: slow down. This is the most important twenty four words in the video. "Chatterbox" is said
plainly, as the product name.*

**Line 3.8** · 7 words · 2.9 s
> Pair A reads genuine. Watch Pair B.

*Tone: instruction, not commentary. Then stop talking.*

`HOLD 9 s` **Silence.** Pair B streams. The verdict settles on "Reads genuine". Let it sit.

**Line 3.9** · 32 words · 13.2 s
> The clone is good. It sounds clean, and the risk sits at 0.028. This is the attack that beats every system that stops at a score. Watch ours refuse to stop there.

*Tone: **completely level.** No wince, no apology, no laugh. You are reporting a measurement. The
entire credibility of the submission is in how calmly this line is read.*

*If on the day the gate commits synthetic instead, record this alternate and use it:*
> *It says synthetic, on a cloner it has never seen. That is what training on eight cloning tools bought us. Either way the next two checks still run, because a voice on its own never releases the money.*

**Line 3.10** · 24 words · 9.9 s
> So the operator issues a challenge. Digits and a Hindi word, one of one hundred and sixty thousand phrases. A recording cannot answer it.

*Tone: brisk, operational. The count is read from the About panel of the running process. If the
About panel does not print it on the day, say "one of the phrases the console generates" and drop
the number.*

**Line 3.11** · 24 words · 9.9 s
> Then the step that does not need the detector at all. A push to the real Rajesh Menon's own phone. He taps Not me.

*Tone: stress "does not depend on the detector". That is the whole architecture in six words.*

**Line 3.12** · 13 words · 5.4 s
> Blocked. Nothing moved. Nothing gets past a check that never touches the audio.

*Tone: three short sentences, three full stops, no rush. Then a beat of silence before beat 10.*

---

**BEAT 10. 5:21 to 5:49. The audit tab. Keep it short.**

**Line 3.13** · 21 words · 8.7 s
> Every step you just saw is a block in the call record. Audit tab, Verify chain. Now I alter block two.

*Tone: plain. You are reading your own actions off the buttons you are pressing.*

`HOLD 4 s` **Silence.** The chain check runs and the status column turns red down the log.

**Line 3.14** · 20 words · 8.3 s
> Broken at block two. Every block after it is unverifiable. A regulator can check what the system knew, and when.

*Tone: even.*

**Line 3.15** · 13 words · 5.4 s
> Tamper evident by construction, and a regulator can verify it without trusting us.

*Tone: firm and final. This is a refusal, delivered as a design choice, not a shortfall.*

**HAND OFF to S4 here.** End your file after line 3.15.

---

### S4. The evidence, and the limits

**Beats 11, 12 and 13. 6:11 to 7:15. Block length 1:04. 142 words, which at 145 wpm is 59 s of
speech, plus 5 s of breath.**

This is the hardest slot to read and the easiest to score. Deliver every number as a result, never
as a confession. If you find yourself softening a word, slow down instead.

---

**BEAT 11. 5:49 to 6:29. The held-out generator heat map.**

**Line 4.1** · 19 words · 7.9 s
> Every cloning tool in this grid was pulled out of training, then tested cold, across all seven phone lines.

*Tone: teaching, not selling. The panel's own footnote explains the protocol on screen, so do not
read it aloud.*

**Line 4.2** · 13 words · 5.4 s
> Six of them come back at zero percent error. Not rounded down. Zero.

*Tone: the last sentence is the line of the beat. Say it once, cleanly, and do not repeat it.*

**Line 4.3** · 28 words · 11.6 s
> And the row that matters most: a cloner released this year, cloning the exact recording it is scored against, same speaker, same sentence. Five point seven percent error.

*Tone: **your slowest line in the video.** Every clause is load bearing. Stress "not the point" and
"one unit, not two". No other team in the room will have an error bar, so do not hurry past it.*

---

**BEAT 12. 6:29 to 6:36. The calibration panel.**

**Line 4.4** · 21 words · 8.7 s
> And the score is calibrated, so 0.8 really does mean eight calls in ten. An operator can act on that number.

*Tone: quick and factual. "Eye so TON ic". This beat is seven seconds long, so do not add anything
to it.*

---

**BEAT 13. 6:36 to 6:53. We attacked it ourselves.**

**Line 4.5** · 21 words · 8.7 s
> Then we attacked it ourselves. Nine filters built to break detectors exactly like ours, run across five hundred and five clips.

*Tone: even, unhurried. You are naming the exact thing a judge would try, before they try it.*

**Line 4.6** · 15 words · 6.2 s
> Error stayed at zero. Catch rate stayed at one hundred percent. It did not move.

*Tone: matter of fact. The two numbers are a contrast, not a boast, so read them at the same volume.*

---

**BEAT 14. 6:53 to 7:03. How fast the decision gets good.**

**Line 4.7** · 25 words · 10.3 s
> And it decides fast. Half a second of audio and the error is already falling. By four seconds it is flat. The operator never waits.

*Tone: this is an engineering decision, not an apology. Land "we chose" firmly. A fraud desk that
accuses one genuine customer in three gets switched off in a week, and that is the reason, so do
not deliver it as a shortfall.*

**HAND OFF to S5 here.** End your file after line 4.7.

---

### S5. Scale, the fair comparison, and sustainability

**Beats 14 and 15. 7:15 to 8:26. Block length 1:11. 161 words, which at 145 wpm is 67 s of speech,
plus 4 s of breath.**

You are the commercial voice. Everything you say is a number with a unit, and every number you say
is printed on the panel behind you, except one. Keep the pace up.

---

**BEAT 15. 7:03 to 7:40. Scoring cost on this laptop.**

**Line 5.1** · 34 words · 14.1 s
> Scoring cost, on this laptop, measured. 185 milliseconds per update on the laptop processor. Real-time factor 0.046. The footnote is the arithmetic: 5.4 concurrent calls per core, 37 cores for a 200 seat centre.

*Tone: arithmetic delivered confidently. "One hundred and eighty five milliseconds", "zero point
zero four six", "five point four", "thirty seven". Every one of these is on the panel, so point with
your voice rather than claiming.*

**Line 5.2** · 32 words · 13.2 s
> Compare that to the market. On the Podonos benchmark of August 2026, the slowest commercial detector runs at 1.52, and anything above one cannot keep up with a live call at all.

*Tone: **one sentence, one breath at the colon, no triumph anywhere in it.** The benchmark name and
the date are **mandatory out loud**, because this is the only figure in the video that is not on the
screen and not in our results file. See the pronunciation guide for Podonos. Do not add the other
vendors. Do not say the word "accuracy".*

**Line 5.3** · 25 words · 10.3 s
> Every system on that benchmark is a cloud API, sending your voice to someone else's server. Ours runs on this laptop with the network off.

*Tone: the guardrail, and it must be audible. It is the sentence that stops a knowledgeable judge
from discounting the whole comparison.*

---

**BEAT 16. 7:40 to 8:13. Cost of adapting to a new cloner.**

**Line 5.4** · 35 words · 14.5 s
> The business model is this panel. A detector accurate the day it shipped is not accurate a year later. Twelve labelled recordings of a new cloner take error on it from 18.8 percent to zero.

*Tone: brisk. A costed fact, not a pitch. The table rows are on screen as you say them.*

**Line 5.5** · 20 words · 8.3 s
> Three recordings already gets you to 6.2 percent. That quarterly cycle is the subscription, and it is priced, not promised.

*Tone: even. "Priced, not promised" is the claim, so do not swallow it.*

**Line 5.6** · 15 words · 6.2 s
> So it gets better with age, on a schedule, for the price of twelve recordings.

*Tone: level and unbothered. You are volunteering this before anyone asks, and that is the point of
saying it at all.*

**HAND OFF to S6 here.** End your file after line 5.6.

---

### S6. Provenance, research base, close

**Beats 16, 17 and 18. 8:26 to 9:29. Block length 1:03. 134 words, which at 145 wpm is 55 s of
speech, plus 3 s of held black at the end, plus 5 s of breath.**

You close the video. Your last line is the last thing a judge hears, so it must be the cleanest
recording in the set.

---

**BEAT 17. 8:13 to 8:32. The About panel, Measurements and Network.**

**Line 6.1** · 28 words · 11.6 s
> Back to the About panel, Measurements. Every number you have seen comes from one results file, generated by one script. Nothing in this console was typed by hand.

*Tone: even and quick. This is the strongest credibility signal in the submission and it costs
twelve seconds, so do not decorate it.*

**Line 6.2** · 12 words · 5.0 s
> Network. External requests, none. No font, no script, no style, no model.

*Tone: four short items, four beats. The row on screen says "none", so read with it, not over it.*

---

**BEAT 18. 8:32 to 8:57. The whole evidence base, scrolling.**

**Line 6.3** · 28 words · 11.6 s
> This is built on the strongest foundation in the field, a frozen speech model with a small trained head, and we pushed it further than the papers did.

*Tone: fast and matter of fact. A citation read as a citation.*

**Line 6.4** · 34 words · 14.1 s
> Eight cloning tools, seven phone lines, three Indian languages, and two thousand trained parameters that run on any laptop in this room. The systems that match us need seven billion parameters and a datacentre.

*Tone: **say the first sentence with confidence, not humility.** Naming what beats you is a strength
move. The architecture reason in the second half is what converts it into a score.*

---

**BEAT 19. 8:57 to 9:07. The close.**

**Line 6.5** · 32 words · 13.2 s
> Next: all twenty two scheduled languages, a handset app so this reaches the families losing the most, and one detector on every call in the country. Pramaan. Proof before approval. Thank you.

*Tone: slow. Full stop after "Pramaan". This is the title of the whole submission. Clean "Thank you"
with no upward inflection. Leave 3 s of silence at the end of your file so the editor has room to
fade to black.*

**END OF VIDEO.**

---

## 3. Word counts and timing, checked

| Speaker | Beats | Words | Speech at 145 wpm | Held | Breaths | Exact | Block, rounded | Start to end |
|---|---|---|---|---|---|---|---|---|
| S1 | 1, 2, 3 | 229 | 94.8 s | 10 s | 4 s | 108.8 s | **1:49** | 0:00 to 1:49 |
| S2 | 4, 5, 6 | 264 | 109.2 s | 0 s | 6 s | 115.2 s | **1:55** | 1:49 to 3:44 |
| S3 | 7, 8, 9, 10 | 277 | 114.6 s | 27 s | 5 s | 146.6 s | **2:27** | 3:44 to 6:11 |
| S4 | 11, 12, 13 | 142 | 58.8 s | 0 s | 5 s | 63.8 s | **1:04** | 6:11 to 7:15 |
| S5 | 14, 15 | 161 | 66.6 s | 0 s | 4 s | 70.6 s | **1:11** | 7:15 to 8:26 |
| S6 | 16, 17, 18 | 134 | 55.4 s | 3 s | 5 s | 63.4 s | **1:03** | 8:26 to 9:29 |
| **Total** | 18 | **1,207** | **499.4 s** | **40 s** | **29 s** | **568.4 s** | **9:29** | |

Check: 456.4 + 40 + 29 = **525.4 s**. Rounding each beat up to a whole second adds 1.6 s, giving
**527 s = 9:07**. Limit 600 s. **Headroom 73 s.**

Per-beat check, in seconds:
14 + 35 + 27 + 36 + 22 + 51 + 33 + 23 + 60 + 28 + 40 + 7 + 27 + 37 + 33 + 19 + 25 + 10 = **527**.

Per-speaker check, in seconds: 76 + 109 + 144 + 74 + 70 + 54 = **527**.

Held time, in seconds: 10 (beat 1 clips) + 7 (beat 7) + 7 (beat 8) + 9 (beat 9) + 4 (beat 10) +
3 (beat 18 black) = **40**.

If a speaker comes in long, the editor's first cut is **line 2.9**, then **line 6.3**, then **line
5.5's first sentence**. **Nothing in beats 1, 3, 6, 9 or 11 may be cut**, because those carry the
miss rate, the prevention invariant, the diversity novelty, the live failure and the confidence
interval.

---

## 4. Recording instructions

**One file per speaker. Six files. No exceptions and no joint takes.**

| | |
|---|---|
| Format | WAV, or M4A at 256 kbps or higher. Nothing else. |
| Sample rate | **48 kHz**. Set it before you record, not after. |
| Channels | Mono is fine. Stereo is fine. Do not convert either way. |
| Mic | Phone or laptop microphone, held **a fist's distance** from your mouth, slightly off to the side so your breath does not hit it. |
| Room | Quiet. Close the windows. Fan and air conditioner off. Soft furnishings help. A bathroom does not, it echoes. |
| Music | None. Do not add any. The editor will not remove it. |
| File names | `S1.wav` through `S6.wav`, or `S1.m4a` through `S6.m4a`. |
| Where | `docs/vo/` in the repository. Create the folder if it does not exist. |

**Every file starts the same way:**

1. Press record.
2. **Three seconds of silence.** Say nothing, do not move, do not touch the device. This is so the
   editor can profile the room noise and subtract it. A file without it will be sent back.
3. **A spoken slate.** Say: "Speaker three, Pramaan demo video, take one." Use your own number. Then
   pause for one second.
4. Read your lines, in order, with a **two second gap between lines**. The gaps are where the cuts
   go. Do not try to perform a continuous paragraph.
5. If you fumble a line, **stop, pause two seconds, and say the whole line again from the start.**
   Do not patch mid sentence. The editor keeps the last good take.
6. Leave three seconds of silence at the end before you stop recording.

**S3 only:** your held gaps are part of the timing. Count them silently, at the printed length, and
leave that much real silence in the file. Do not fill them with "so" or "now".

**S1 only:** beat 1 needs 10 s of real room silence at the top of your file, after the slate, before
line 1.1.

**Before you send the file:** play it back once, whole, on headphones. Listen for a fan, a
notification, a chair, a door, and your own paper. If you hear it, record again. It is faster than
asking the editor to fix it.

---

## 5. Pronunciation and delivery guide

Read your own lines aloud twice against this table before you record.

| Term | Say it as | Expand it on first use |
|---|---|---|
| **Pramaan** | pruh MAAN, long second syllable, as in the Hindi word for proof | No expansion needed. If you gloss it once, "Pramaan, which means proof". |
| **XLS-R** | "ex ell ess arr" | **Not spoken in this script.** It is a row in the About panel and the camera is on it during beat 4. S2 says "a frozen three hundred million parameter multilingual model" instead. |
| **EER** | "ee ee arr" | **Always expand on first use: "equal error rate".** S6 line 6.4 is the only place it appears, already expanded. Nobody else says the initials. |
| **isotonic** | eye so TON ic | S4 line 4.4 says it. If asked, "isotonic regression, a way of turning a raw score into an honest probability". |
| **Platt** | "plat", one syllable | Not spoken. It is a column header in the Calibration panel, visible during beat 12. |
| **Chatterbox** | CHATTER box, as a product name, no pause inside it | "Chatterbox, a zero-shot cloner released in 2025". S3 line 3.7 already carries the gloss. |
| **FLEURS** | "flurs", one syllable, like "flowers" without the "ow" | Not spoken. It is the genuine-speech corpus and appears on screen in the provenance caption as "FLEURS hindi". If asked, "FLEURS, a public multilingual speech corpus". |
| **Podonos** | puh DOE nos | **Name it in full on first use: "the Podonos audio deepfake detection benchmark".** S5 line 5.2 already does, with the date. |
| **G.723.1** | "gee dot seven two three dot one" | Not spoken as a code. S2 line 2.4 says "a 6.3 kilobit line", which is what the carrier selector shows. |
| **Opus** | OH pus | "a VoIP Opus line". S3 line 3.2 carries it. VoIP is "voyp". |
| **SHA-256** | "shah two five six" | Not spoken in this version. The hash column is on screen in the Audit tab during beat 10. |
| **SATYAM** | SUT yum | Said as the system name. S6 line 6.4. |
| **Indic-CodecFake** | "Indic codec fake" | A public Indic-language benchmark dataset. Named as such in line 6.4. |
| **Interspeech** | "INTER speech" | A speech conference. Cited by name and year only. |
| **Pascu** | PASS koo | Author name. "Pascu and colleagues". |
| **Reality Defender** | as written | Vendor name, from the Podonos benchmark. The only vendor named in this version. |
| **XTTS-v2** | "ex tee tee ess vee two" | A voice cloning model. S3 line 3.5 says "a clone from XTTS-v2, a family the model has seen", which is enough. |
| **EnCodec** | "en CO dec" | "neural codec resynthesis" is the plain-language form and S4 line 4.2 uses it. Do not say the brand. |
| **Wi-Fi** | "why fye" | No expansion. |
| **GPU** | "gee pee you" | If you want the plain form, "a graphics card". Do not expand mid line, it costs 2 s. |
| **API** | "ay pee eye" | S5 line 5.3 says "a cloud API". That is understood by this audience. |
| **VoIP** | "voyp" | "a VoIP Opus line" is enough. |
| **Rajesh Menon** | RA jesh MAY non | The caller name printed in the decision bar. Say it as the console prints it. |

### Numbers, said out loud

| Written | Say |
|---|---|
| 69.2 percent | "sixty nine point two percent" |
| 30.8 percent | "thirty point eight percent" |
| 13.2 percent | "thirteen point two percent" |
| 4.7 to 21.9 percent | "four point seven to twenty one point nine percent" |
| 4.5 to 39.6 percent | "four point five to thirty nine point six percent" |
| 35.1 points | "thirty five point one points" |
| 35.9 percent | "thirty five point nine percent" |
| 2,049 | "two thousand and forty nine" |
| 0.010, 0.014, 0.571 | "zero point zero one zero", "zero point zero one four", "zero point five seven one" |
| 0.010, 0.990, 0.028 (live) | "zero point zero one zero", "zero point nine nine zero", "zero point zero two eight" |
| 0.8 | "zero point eight" |
| 0.046, 1.52 | "zero point zero four six", "one point five two" |
| 3.27 percent | "three point two seven percent" |
| 160,000 | "one hundred and sixty thousand" |
| 185 milliseconds | "one hundred and eighty five milliseconds" |
| 5.4 | "five point four" |
| 37 cores, 200 seat | "thirty seven cores", "two hundred seat" |
| 23 clones, 127 genuine recordings | "twenty three clones", "one hundred and twenty seven genuine recordings" |
| 24.4, 18.2, 14.0, 1.1, 18.8, 6.2 percent | point by point, as above |
| 14 August 2026 | "the fourteenth of August, twenty twenty six" |

---

## 6. Capture list

**This is the shot list for whoever drives the console.** One continuous session, in this order, so
the Audit tab has a real call history by beat 10. Nothing is staged, faked or edited into the
console.

**Before you start:**

- `make demo`, console at `http://127.0.0.1:8770`, Chrome, exactly **1920 x 1080**, browser zoom
  100%, no other tabs, no bookmarks bar, no notifications.
- **Light theme** for beats 2 to 17. The dark toggle is only for the optional B roll.
- Screen recording at 1920 x 1080, 30 fps or better, **cursor visible**.
- Confirm the About panel prints "Distinct phrases" with a real number before you record anything.
  If it prints nothing, restart the server from current code; a stale process is what broke this in
  the last audit.
- **Wi-Fi stays ON** until beat 7, because beat 7 is where you switch it off on camera.

| Beat | Drive this, exactly | Dwell |
|---|---|---|
| 1 | No console. Black card, then `data/samples/pair_real_hindi.wav` and `data/samples/pair_clone_hindi.wav` back to back, audio only, 5 s of each. | 14 s |
| 2 | Live call tab, nothing running. Open the **Line** selector, hold it open so all ten demo lines are legible, scroll it once top to bottom, then select **"Genuine caller · Hindi (FLEURS recording)"**. Open the **Carrier** selector, hold so all seven carriers are legible, then select **"VoIP, Opus 24 kbps"**. Do **not** press Start. Let the provenance caption ("real human speech, FLEURS hindi, CC-BY 4.0") sit on screen for the last 4 s. | 4 s on each open selector, 35 s total |
| 3 | Same screen. Scroll so the **Prevention ladder** panel fills the frame, all five rungs and the panel note "The voice is never the last factor" visible. Move the cursor slowly from rung 1 to rung 5 over about 8 s, resting 1 s on each rung title. | 27 s |
| 4 | Click **About**. Scroll the dialog so **Detector** is centred, hold on "Trained parameters on top" for 6 s, then scroll to **Gate** and hold on "Earliest decision" and "Threshold band measured for" for 8 s. Leave the dialog open. | 36 s |
| 5 | Close About. Live call tab, **no call running**. Set Carrier to **"Clean line, no codec"**, hold 4 s on the Risk trace meter so the narrow striped band is visible. Set Carrier to **"Narrowband, G.723.1 6.3 kbps"**, hold 6 s while the striped band visibly widens. Set it back to **"Clean line, no codec"**. Scroll 100 px so the facts table row "Threshold band measured for" is in frame for the last 5 s. | 22 s |
| 6 | **Evidence tab.** Scroll to **"Error rate against training diversity, on a cloner never seen"** so the whole chart plus its footnote is in frame. Hover the **k = 1** point for 5 s so its tooltip shows the min to max range. Move slowly along the line to the **k = 8** point and hover for 6 s. Then pull the cursor away and hold on the full chart, shaded band visible, for the rest. | 51 s |
| 7 | **On camera:** open the macOS menu bar Wi-Fi menu and switch Wi-Fi off. Hold 2 s on "Wi-Fi: Off". Then Live call tab. Line = **"Genuine caller · Hindi (FLEURS recording)"**, Carrier = **"VoIP, Opus 24 kbps"**. Hold 2 s on the provenance caption. Press **Start monitoring**. Do not touch anything until the verdict commits. Frame must include the decision bar (verdict, and the red "Approval held until verified" pill) and the Risk trace. Let it run to the verdict plus 5 s. Press **End call**. | 33 s |
| 8 | Line = **"Clone · XTTS-v2 (IndicSynth, Hindi)"**, Carrier unchanged at **"VoIP, Opus 24 kbps"**. Hold 2 s on the provenance caption. Press **Start monitoring**. Hold through the commit to "Reads synthetic". At the moment the verdict turns red, scroll 120 px so the facts table row **"Time to score one update"** is in frame, and hold 5 s. Press **End call**. | 23 s |
| 9 | **One take, no cuts, no scrolling away from the decision bar.** (a) Line = **"Pair A · the real person (FLEURS Hindi recording)"**, Carrier = **"Clean line, no codec"**. Start monitoring. Let it commit "Reads genuine". End call. (b) Line = **"Pair B · 2025 zero-shot clone of the same person (Chatterbox, unseen in training)"**, same carrier. Hold 3 s on the provenance caption, which says the cloner is in no training data. Start monitoring. **Let it run and do not intervene**, through the commit and the drift, for at least 12 s. (c) Click **Issue challenge**. Hold 5 s on the challenge card in rung 2, phrase legible. (d) Click **Send device push**. Hold 3 s on the device card in rung 3. (e) Click **Not me**. Hold 6 s on the decision bar going red and rung 5 reading blocked. Do not press End call on camera. | 60 s, uncut |
| 10 | **Audit tab.** "Calls on record" list is in frame on the left, with today's calls, newest first. Select the Pair B call. Hold 3 s on the **Event log** so the columns time, actor, event, detail, hash and chain status are legible. Click **Verify chain**, hold 3 s on the pass state. Click **Alter a block** and choose **block 2**. Click **Verify chain** again. Hold 8 s while the status column reads broken at block 2 and "unverifiable" down every later row. Then click **Restore** and hold 2 s on the chain verifying again. | 28 s |
| 11 | **Evidence tab.** Scroll to **"Error rate on a generator family held out of training"**. Frame the whole heat map: every generator row and all seven carrier columns, plus the ramp legend and the footnote. Hover the **EnCodec resynthesis** row's clean-line cell for 4 s so the tooltip reads the equal error rate. Then move to the **bottom row, the 2025 cloner**, hover its clean-line cell for 6 s. Pull the cursor away and hold on the whole grid. | 40 s |
| 12 | Scroll down to **"Calibration error"**. Frame the whole table, all three columns, plus the footnote "A risk number is only actionable if 0.8 means eight calls in ten." No cursor movement. | 7 s |
| 13 | Scroll **back up** to the heat map. Hold on the **column headers** for 5 s, then on the whole grid. No cursor movement, no hovering. This is a still shot while S4 names the surface that is not on this grid. | 27 s |
| 14 | Scroll to **"Scoring cost on this laptop"**. Frame the whole table: Processor, Window, Median, Real-time factor, every row, plus the capacity footnote. Hover the **row whose real-time factor is 0.046** for 5 s. Then hold on the footnote line for the last 10 s. **This panel stays on screen for the entire Podonos sentence.** Do not cut away from it while S5 names the benchmark and the date. | 37 s |
| 15 | Scroll to **"Cost of adapting to a new cloner"**. Frame the whole table, all three columns, every row, plus the footnote. Hover the **3 recordings** row for 4 s, then the **12 recordings** row for 5 s. Hold on the whole table for the rest. | 33 s |
| 16 | Click **About**. Scroll the dialog to **Measurements**, hold 8 s on "Results generated", "Clips measured" and "Cached embeddings". Scroll to **Network**, hold 6 s on "External requests: none, this console loads no font, script or style from the network". Close the dialog. | 19 s |
| 17 | **Evidence tab, one continuous slow scroll**, top to bottom across all six panels at roughly 90 px per second, ending parked on the heat map. No cursor, no hovering, no stops. | 25 s |
| 18 | No console. Black card: "Pramaan. Proof before approval." Fade to black. | 10 s |

**Capture rules:**

- **Never switch to a slide, a PDF, a terminal or a file manager.** If something breaks mid capture,
  stop, fix it, and re-record that beat from its start.
- **Never re-run a beat to get a friendlier score.** Beat 9 in particular: the honest outcome is the
  beat.
- **Do not resize the window or change zoom mid session.** The heat map reflows and the cut will
  show it.
- **Keep the mouse still whenever nothing is being demonstrated.** Idle cursor drift is the most
  common reason a take gets thrown away.
- Beat 7 must show the Wi-Fi being switched off **in the same unbroken shot** as the console. If the
  screen recorder cannot capture the menu bar, re-frame the recording region rather than faking it.

---

## 7. Deferred, and why

Cut for time, or because no console view carries them honestly. Listed so nobody thinks they were
forgotten. All of them are in `docs/QA_PREP.md`, the README or the deck.

- **The Malafide black-box adversarial result**, 9 filters on 505 held-out spoof clips at 0.00%
  error and 100.0% catch, with the white-box gradient attack unmeasured. **There is no console panel
  for it**, and it needs the caveat spoken in the same breath to be honest, which costs about 20 s.
  Q&A answer.
- **The other three Podonos vendor figures**, Corsound 0.035, Pindrop 0.076, Resemble 0.40. Only
  Reality Defender at 1.52 is spoken, because it is the one that makes the point that a real-time
  factor above 1.0 cannot keep up with a live call. Reading a four-row table aloud over a panel that
  does not contain it reads as a slide.
- **The AUDETER 2025 scaling citation and the RADAR and Wav2DF-TSL reference points.** No console
  view. Slide 6 carries them.
- **Cross-session consistency, the Key Component we did not build**, and the SASV framing. Cut
  entirely. Q&A answer.
- **The challenge rung's negative measurement in the parent repository**, 60.5% settled and 47.8% of
  those wrong. Cut. It needs 20 s to state honestly and 8 s to state misleadingly, so it is left out
  rather than compressed. S3 line 3.11 carries the design consequence instead, that the rung which
  blocks the transfer does not depend on the detector.
- **The A1 self-caught shortcut**, 0.59% against 32.03% on the matched-pairs control. Cut. S2 line
  2.10 carries the protocol that came out of it.
- **Tamil and Telugu having no held-out cloner.** Cut from beat 13 in favour of the replay
  microphone surface, which is the limit a judge is most likely to trigger. `human_tamil` and
  `human_telugu` are visible in the line selector during beat 2, so the languages are shown even
  though this limit is not spoken.
- **The leave-one-out gate replay numbers**, including EnCodec at 45.1% committed-call error. The
  heat map already shows the equal error rate for that family and S4 names it. Q&A answer.
- **The clip counts and corpus size**, 3,429 clips and 229 minutes. **On screen** in the About panel
  during beat 16, under "Clips measured", but not spoken.
- **CNAP under TRAI**, and the four-item roadmap. Slide 6, not spoken.
