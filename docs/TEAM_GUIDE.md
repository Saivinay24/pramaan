# Pramaan, explained for the whole team

Read this once, start to finish. Everything is in plain words. After this you should be able to explain the project to anyone, present your slide, run the demo, and survive any question.

Every number here is generated from our results file. These are the only numbers we say on stage.

---

# PART 1 · THE STORY

## 1.1 The problem, the way we will tell it

AI voices have stopped sounding like robots. Today, anyone can take a few seconds of someone's voice from an Instagram reel, a WhatsApp voice note or a YouTube video, and make that voice say anything.

So imagine your phone rings. It is your father's voice, or your brother's, or your manager's. They sound stressed. They need money right now, or they need an OTP, or they need you to confirm something. **You have no way to tell whether that is really them.** Not by listening. The voice is perfect.

That is the whole problem in one sentence: **the human ear has stopped being proof of identity, and everything we do on the phone still assumes it is.**

It is happening at both ends of the scale:

```
   AT HOME                                  AT WORK
   "Papa's voice" asking for money          "The CFO's voice" asking finance
   or an OTP, from a new number             to approve a large transfer

   loses a family a few lakh                loses a company a few crore
```

Same attack, same tool, different victim. Our system is built for the second case first, because banks and companies have the money, the fraud losses and the compliance rules to pay for it. But it is the same technology that protects the first case, and that is the honest way to say it.

**What exists today does not help.** Caller ID can be faked. Calling back does not help if the attacker controls the number. And "I know his voice" is precisely the thing being attacked.

## 1.2 What the problem statement asks for

SIH problem 26104 asks for five things. Most teams will build only the first one.

| what is asked | what it means |
|---|---|
| detect **during the call** | not on a recording afterwards, while the person is still talking |
| an **actionable risk score** | a number you can act on, not just the word "fake" |
| **prevention**, not only detection | actually stop the fraud, do not just write a report |
| **on the device** | the audio must never leave the bank's building |
| **Indian languages, real phone lines** | Hindi, Tamil, Telugu, over normal noisy phone connections |

## 1.3 Our answer, in one sentence

**Pramaan (प्रमाण = proof): the voice is never the last factor.**

Pramaan listens to the live call, gives a fresh risk score every half second, and keeps the money on hold until something that is **not** the voice confirms it is really that person.

That sentence is the whole project. If you remember nothing else, remember that.

---

# PART 2 · HOW IT WORKS

## 2.1 The four layers

```
   LIVE CALL AUDIO
        │   (phone or VoIP, any quality, cut into half-second pieces)
        ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  LAYER 1 · THE LISTENER          "does this voice sound machine-made?"       │
 │  A big frozen speech model turns each piece of audio into numbers.           │
 │  A tiny classifier reads those numbers and gives a probability.              │
 │  Output: a number between 0 (human) and 1 (synthetic), refreshed every 0.5 s │
 └───────────────────────────────────┬──────────────────────────────────────────┘
                                     ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  LAYER 2 · THE GATE              "am I sure enough to say it out loud?"      │
 │  Commits to an answer ONLY if all three are true:                            │
 │     • it has heard at least 1.5 seconds of real audio                       │
 │     • the probability is outside this channel's uncertain band, e.g. [0.010, 0.014] clean │
 │     • it has stayed there for three updates in a row                         │
 │  Otherwise it says "not yet" and passes the call to Layer 3.                 │
 └───────────────────────────────────┬──────────────────────────────────────────┘
                                     ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  LAYER 3 · THE PREVENTION LADDER          this is the "prevention" half      │
 │   step 2  LIVE CHALLENGE: "please say these digits: 8 7 7 8, then बर्तन"       │
 │           one of 160,000 possible phrases, so no recording can answer it     │
 │   step 3  DEVICE APPROVAL: a push notification to the REAL person's          │
 │           registered phone. No tap there, no money. Compulsory for large      │
 │           transfers no matter what the voice score said.                     │
 │   step 4  callback on the number on record, or a human operator decides      │
 └───────────────────────────────────┬──────────────────────────────────────────┘
                                     ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │  LAYER 4 · THE AUDIT LEDGER               this is the "blockchain" half      │
 │  Every score, decision, challenge and approval becomes a block. Each block   │
 │  carries a fingerprint of itself plus the previous block's fingerprint.      │
 │  Change anything afterwards and every later fingerprint breaks. Provable.    │
 └──────────────────────────────────────────────────────────────────────────────┘
```

**Say it in one breath:** "Layer 1 listens. Layer 2 decides when it is sure enough to speak. Layer 3 asks the caller to prove it, then asks the real person's phone. Layer 4 writes everything down so nobody can quietly edit it later."

## 2.2 The two brains

This is the question a technical judge will ask. Learn this section properly.

### Brain 1: the big model that listens (borrowed, never changes)

We use **XLS-R**, an open-source speech model released by Meta. Three facts about it:

- It has **about 315 million numbers inside it** (the model is named XLS-R-300M) and takes 2.4 GB on disk.
- It was trained on **436,000 hours of speech in 128 languages**, including Hindi, Tamil and Telugu. Not by us, and we could never afford to.
- **We freeze it.** It never learns anything from us. We only use it as a very good pair of ears.

Its job: take a piece of audio and turn it into **2048 numbers** that describe *how the sound was physically made*, not what was said. Think of it as a detailed fingerprint of the voice's texture, breathing and micro-timing.

Two choices we made inside it, and both have a reason a judge may probe:

1. **We read layer 5 out of 24.** The model processes audio in stages. The early stages still hold the raw physical details of how the sound was produced. The last stages have thrown that away and only kept the meaning of the words, which is useless for catching a fake. So we tap it in the early-middle.
2. **We take the average and the spread** of those numbers across the clip. Average captures the typical texture; spread captures how much it varies. Real human speech varies more than machine speech in specific ways.

### Brain 2: the classifier that decides (ours, tiny)

On top of those 2048 numbers sits our own classifier. It is deliberately, almost absurdly small:

```
   audio  ──►  XLS-R (frozen, 300,000,000 numbers)  ──►  2048 numbers
                                                              │
                                                              ▼
                                        our classifier: 2,049 numbers
                                                              │
                                                              ▼
                                          one score:  negative = human
                                                      positive = synthetic
```

**2,049 numbers is the entire thing our project learned.** The file it lives in is 61 KB. The frozen model beside it is 2.4 GB.

Why so small, and why we are proud of that rather than embarrassed:

- We only have about 2,500 training clips. A big model with that little data simply memorises the specific cloning tools we showed it, and then fails completely on the next tool that comes out. A tiny classifier is forced to learn the general difference instead.
- This is a published finding, not our opinion (Interspeech 2024). Freezing the big model and training a small head beats fine-tuning the big model on new, unseen fakes.
- Side effect: it trains in **seconds on a laptop CPU**, no GPU. That is what makes our whole business model, retraining against every new cloner, actually practical.

### Brain 3 (the one people forget): the calibrator

The classifier gives a raw score like "+3.4" or "-6.9". That means nothing to an operator. The **calibrator** converts it into an honest probability, so that when the screen says 0.8, roughly 80 out of 100 clips scoring that were genuinely synthetic.

We have **eight calibrators**, one for each audio length from 0.5 s to 4 s, because a score from 1.5 seconds of audio and a score from 4 seconds do not mean the same thing. Without this, the problem statement's phrase "actionable risk score" would be a lie.

### See it for yourself, with real numbers

Run this and it prints every number at every stage for any clip:

```bash
scripts/explain.sh data/samples/clone_xtts_v2.wav --compare data/samples/human_hindi.wav
```

A saved copy of that output is in `docs/WALKTHROUGH_EXAMPLE.txt`. The short version, for a real 4-second clone next to a real human recording:

```
                        64,000 audio samples (4 s at 16 kHz)
                                     │
     frozen model, 315 million numbers, unchanged
                                     ▼
                        199 frames x 1024 learned features = 203,776 numbers
                                     │
     average of each column, and spread of each column
                                     ▼
                        2048 numbers describing the whole clip
                                     │
     our classifier: multiply each by its weight, add up
                                     ▼
              clone: +12.19                    human: -8.62
                                     │
     calibrator lookup table
                                     ▼
              clone: 0.99                      human: 0.01
                                     │
     gate: outside this channel's band, steady, after 1.5 s
                                     ▼
              SYNTHETIC                        HUMAN
```

Two things in there are worth being able to say out loud:

- **The features are learned, not designed.** Nobody can point at column 37 and say "that is pitch". The frozen model invented those 1024 measurements for itself while learning 128 languages. We never chose them, and that is why the approach carries over to languages and cloners we did not plan for.
- **The score is a tug of war.** For that clone, features pushing towards "synthetic" totalled +30.4 and features pushing towards "human" totalled -22.3. The net, +12.2, is the verdict. No single feature decides anything; about 55% of the deciding weight sits on the average half and 45% on the spread half.

### The live path, end to end

```
 microphone or phone line
       │  every 0.5 s: take the last 8 seconds of audio
       ▼
 THE LISTENER    XLS-R  ────────────►  2048 numbers
       ▼
 THE CLASSIFIER  ────────────────────►  raw score, e.g. +3.4
       ▼
 THE CALIBRATOR  ────────────────────►  probability, e.g. 0.99
       ▼
 THE GATE        ────────────────────►  DEFER / HUMAN / SYNTHETIC
       ▼
 THE LADDER + LEDGER  ───────────────►  hold, challenge, push, record
```

The whole thing takes **185 milliseconds** per update on a laptop CPU.

## 2.3 What we trained it on, and the idea that makes it work

A detector can only recognise the **kinds** of fake it has already heard. Show it one cloning tool and a different tool walks straight past it. This is the single biggest failure in this field.

So instead of downloading one dataset, we **built six different families of fake speech ourselves**, on this laptop, all speaking the same Hindi, Tamil and Telugu sentences as our real recordings:

```
  REAL SPEECH
     google/fleurs, 510 recordings, Hindi + Tamil + Telugu, free licence

  FAKE SPEECH, six different technologies (this is the important part)
     1. XTTS-v2      a popular voice-cloning text-to-speech tool
     2. FreeVC       voice conversion: reshapes one person's voice into another's
     3. EnCodec      a neural codec that rebuilds audio sample by sample
     4. Apple TTS    the Hindi and Telugu voices built into every Mac
     5. Meta MMS     Meta's text-to-speech, all three languages
     6. Kokoro       a popular open 2025 text-to-speech model

  KEPT HIDDEN, never used in training, this is our exam paper
     7. Chatterbox   a 2025 cloner: give it 4 seconds of a real person and it
                     speaks any sentence in that voice.
                     We used it to clone OUR OWN real recordings.
                     Same speaker, same sentence, same microphone.
                     The only difference between the two files is: one is real.
```

Number 7 is the hardest test we could design. Nothing else about the two clips differs, so the detector cannot cheat by noticing the recording quality or the words.

### The idea in one line

**Diversity does not buy you a lucky number, it removes the unlucky one.**

We measured this. Train on only one or two of those families and the result is a lottery depending on which ones you happened to have: on the hidden cloner the error went as high as **39.6%**. Train on all 8 and it is **13.2%**, every time, no luck involved. The earlier version of this same project, trained on only two families, sat at **35.9%**.

That is our contribution: not a new algorithm, but showing that generator variety is the thing that actually decides whether these systems work, and building the variety ourselves on a laptop.

## 2.4 The one score you need to understand

We report an **error rate** (papers call it EER). Read it simply as: **out of 100 attempts, how many does it get wrong**, counting misses and false alarms together. Lower is better. 50% is a coin toss.

| test | error rate | what it means in words |
|---|---|---|
| clones from families it has learned | 0.0% to 24.4% depending on family | known tools: caught nearly every time |
| **Chatterbox, our self-built hardest test** | **13.2%** (95% CI 4.7% to 21.9%) | a ranking number only; see the box below for what it actually decides |
| the earlier version of this project, same test | 35.9% | we cut the error by about two thirds |
| **false alarms on real human callers, clean line** | **0.00%** | it does not accuse genuine people |
| the same thing on the worst of our seven channels | 0.79% (G.723.1 6.3 kbps), 95% CI 0.14% to 4.33% | say the channel every time you say this number |

### The second number, and you must know this one too

An error rate tells you whether the system can *rank* a clone below a human. It does not tell you what it actually **says** at the threshold we ship. Those two can disagree badly, and against a brand-new cloner they do. Measured on the shipped system:

| what it hears | says "synthetic" | refuses to decide | says "human" |
|---|---|---|---|
| clones from families it learned | 100.0% or more | almost none | none |
| **the hidden 2025 cloner** | **69.2%** (95% CI 53.6% to 81.4%) | **0.0%** | **30.8%** (95% CI 18.6% to 46.4%) |
| real human callers, clean line | 0.4% | none | almost all of them |
| real human callers, pooled over all 7 channels | 1.1% | none | almost all of them |

Read that middle row honestly: **against Chatterbox, Layer 1 alone still waves 30.8% of them through.** Roughly one Chatterbox clip in three is called genuine on the laptop. Never claim otherwise, and expect a judge to try one.

**But here is the case that matters, and we do catch it.** A commercial ElevenLabs professional voice clone, made the night before the presentation and appearing nowhere in our training data, is called synthetic at 2 to 3 seconds with probability 0.99, on a clean line, over VoIP, and over the worst narrowband line. We checked it is real detection and not a file-format artefact: a genuine human recording through the same conversion stays at 0.01. It is one clip, so say "a demonstration, not a measured rate".

Why the difference: the Chatterbox clips clone our own recordings using those very recordings as the prompt, so they inherit a lot of the original and sit right on top of the genuine voices. That is what makes it the hardest test we could build, and it is deliberately harder than the real attack.

This is not a bug and it is not unique to us. It is the known, published behaviour of every passive deepfake detector against a generator released after it was trained, commercial ones included. The scores still rank correctly; it is the fixed threshold that stops transferring.

**And it is the entire reason the system is built the way it is.** If Layer 1 could be trusted on its own, we would not need Layers 2, 3 and 4. Say it in this order and it becomes the strongest part of the pitch:

> "Against a cloner released after we trained, the listener alone catches about one in eight and waves most of them through. Every detector in the world has this problem. That is precisely why our system never lets the voice release the money: it asks a question a recording cannot answer, and then it asks the real person's own phone."

**Never hide these rows. Lead with them.** And always follow with the repair:

1. *"We did not just report the failure, we measured the fix."*
2. *"Give it 12 labelled recordings of the new cloner and the error on it drops from 18.8% to 0.0%, tested on speakers it never saw. So the product is not a frozen model, it is a subscription that keeps re-testing against every new cloning tool that ships."*

## 2.5 Speed and scale

| | |
|---|---|
| new score every | 0.5 seconds |
| earliest possible decision | 1.5 seconds of audio |
| time per update, laptop CPU, no GPU | 185 ms |
| calls one CPU core can watch at once | about 5.4 |
| a 200-seat call centre needs | about 37 cores, one ordinary server |
| audio that leaves the building | none |

The line to say: **"privacy and scalability are the same fact here"**. Because it runs on the bank's own machine there is no cloud bill, no internet dependency, and no customer audio leaving the premises.

---

# PART 3 · THE ROADMAP (say this with confidence, it is our strongest closing)

Be completely straight about where we are:

> "What you have seen was built on one MacBook Air, in days, with no GPU and no budget. We trained on about **2919 synthetic clips from 8 generators, and most of those are open-source models we ran ourselves.** That is a deliberately small, honest starting point, and everything we claim is measured on it."

Then the ask:

> "Here is what changes if we go forward from this round.
>
> **One, data at scale.** We buy and generate samples from the cloners attackers actually use today: ElevenLabs, PlayHT, Resemble, the newest open models, and every new one that ships. Not 8 generators, but fifty or more, across many more Indian languages and dialects. We already proved the effect variety has; right now we are just short of it.
>
> **Two, compute.** Everything here was trained on a laptop CPU in seconds. With real GPUs we train on hundreds of thousands of clips instead of two thousand, and we can afford larger models where they genuinely help.
>
> **Three, benchmark ourselves publicly.** We put our numbers next to the published state of the art on the same public benchmarks, and against the commercial products, on Indian languages, which is exactly where nobody has published a comparison. Right now every vendor quotes one number on English studio audio. A bank buying one of these has no way to check.
>
> **Four, real deployment.** One bank's contact centre, real calls, then telecom-level integration.
>
> The architecture does not change for any of that. The Listener, the Gate, the ladder and the ledger are already the shape of the final product. What scales is the training data and the compute behind it, and we have shown exactly how much each one is worth."

Two supporting points to have ready:

- **Why the small start is a feature, not an excuse:** because it retrains in seconds, adding a new cloner is cheap. That is what makes a quarterly refresh a real business rather than a promise.
- **What we will not claim:** we will not say our numbers beat commercial vendors today. We will say nobody has published a fair comparison on Indian languages and phone lines, and building that comparison is itself worth doing.

---

# PART 4 · THE PRESENTATION

Six slides, six speakers, 10 minutes, 2 minutes of questions.

```
 0:00 ── S1 ── 1:20 ── S2 ── 3:00 ── S3 (live demo) ── 6:00 ── S4 ── 7:40 ── S5 ── 9:00 ── S6 ── 10:00
       slides 1-2      slides 2-3        the console            slide 4       slide 5      slide 6
```

**S1 · the problem** (1 min 20). The phone-call story from 1.1: a voice you know, asking for money, and no way to tell. Then the same attack against a company's finance desk. Then the five things the problem statement demands. End on: "Our answer is Pramaan, which means proof. The voice is never the last factor."

**S2 · what we built** (1 min 40). The four layers from 2.1, one sentence each. Then the two brains from 2.2 in three sentences: borrowed frozen ears, our own tiny 2,049-number decision-maker, honest probabilities. Then what is new: six fake families built by us, the same-speaker-same-sentence exam, and "detection is a router, not a judge". Hand to S3.

**S3 · the live demo** (3 min). Part 5 of this guide.

**S4 · the evidence** (1 min 40). The diversity finding from 2.3, the grid of every family against every phone codec including the red cells ("a grid with no red cells is a grid where nobody ran the hard test"), and the repair number from 2.4.

**S5 · impact, scale, money** (1 min 20). Who it protects, the numbers from 2.5, then the business model: a per-seat licence for software that runs inside the bank, plus a subscription for continuous re-testing against new cloners. Say the licence limitation yourself before anyone asks: two of our training sources are research-only, so a commercial version retrains on licensed data.

**S6 · research and roadmap** (1 min). Name the work we built on (we did not invent the pieces and we say so), then the roadmap from Part 3, then close: "Pramaan: proof before approval. Thank you."

**Question ownership.** Accuracy and evaluation → S4. Architecture and models → S2. The demo → S3. Business and scale → S5. The problem and users → S1. Roadmap and research → S6. One person answers. Nobody joins in.

---

# PART 5 · RUNNING THE DEMO

## Setup

```bash
cd ~/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
scripts/demo.sh
```

Then open Chrome at **http://127.0.0.1:8770**. Turn **Wi-Fi off first**: proving it works with no internet is part of the pitch.

## The screen

```
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ Pramaan   Live call | Audit ledger | Evidence      [on-device] [model] [ms]     │
 ├────────────────────────────────────────────────────────────────────────────────┤
 │ SOURCE [what audio ▼]   CHANNEL [which phone line ▼]   [Start call] [End call]  │
 ├──────────────┬───────────────────────────────────────┬─────────────────────────┤
 │ INCOMING     │ RUNNING RISK SCORE                    │ VERIFICATION LADDER     │
 │ CALL         │  ● state       the big probability    │  1 passive analysis     │
 │ who is       │  [human ░░ undecided ░░ synthetic]    │  2 live challenge       │
 │ calling,     │  score-over-time graph                │  3 device approval      │
 │ what they    │  live waveform                        │  4 decision on record   │
 │ want, and    │  update / earliest / decided / ms     │  [Issue challenge]      │
 │ the HOLD box │                                       │  [Send push] [Block]    │
 ├──────────────┴───────────────────────────────────────┴─────────────────────────┤
 │ AUDIT CHAIN  #0 call opened  #1 score  #2 gate committed  #3 ...                │
 └────────────────────────────────────────────────────────────────────────────────┘
```

- **SOURCE** is either the laptop microphone or a bundled clip. Under it the screen always prints the clip's **true origin**. Read that line out loud every single time. We never let anyone think a file is live.
- **CHANNEL** simulates the phone line. Opus 24k is normal VoIP; G.723.1 is the worst narrowband line.
- The **state** goes Listening → Verifying → Genuine voice, or Synthetic voice.
- The striped middle of the meter is the **undecided band**. Inside it, the Gate refuses to guess.
- The **hold box** shows the money: held, blocked, or cleared.

## The four beats

**Beat 1, a real caller.** Source "Genuine caller · Hindi", channel Opus 24 kbps, Start call.
Say: a real recording, through a VoIP codec, streamed in live. For the first 1.5 seconds it refuses to decide, by design. Then: Genuine. **Point at the hold box:** "acoustic check passed, device approval still required". The voice is never the last factor.

**Beat 2, a clone it knows.** Source "Clone · XTTS-v2", Start.
Say: a cloned voice from a family the system has learned. The score jumps to 0.99, Synthetic at 1.5 s, transaction blocked before the sentence finishes. Point at the milliseconds: that is on the laptop CPU.

**Beat 3, the hard one.** Run "Pair A · the real person" (Genuine), then "Pair B · 2025 clone of the same person".
Say: same person, same sentence, cloned by a tool released this year that we never trained on. Then whatever happens on screen:
- if it commits Synthetic: "caught, on a cloner it has never heard."
- if it stays low or hovers: "the listener reads this as close to genuine. That happens to every detector against a brand-new cloner, including the commercial ones, and it is precisely why the next steps exist."
Then **Issue challenge** ("random digits and a Hindi word, no recording can answer this"), **Send push** ("this goes to the real person's own phone"), **Not me**. Hold box turns red: blocked. "The money never moved."

**Beat 4, the ledger.** Audit ledger tab → **Tamper with block 2** → **Verify chain**. Red: broken at block 2, every later fingerprint invalid. "A regulator can check exactly what the system knew and when."

## The microphone, tested on this laptop

The speaker-to-microphone path is its own kind of phone line, so we recorded 200 training clips through this laptop's own speaker and mic and retrained on them. Measured afterwards:

| played into the mic | result |
|---|---|
| an ElevenLabs commercial voice clone (never trained on) | synthetic at 1.5 s, blocked |
| a real Hindi, Tamil or Telugu recording | human |
| a person speaking live | human |

Keep the phone within about 30 cm of the laptop, medium volume, quiet room. If the score sits in the middle band, that is the Gate refusing to guess: issue the challenge and send the push, which is the designed path, not a failure.

## If something breaks

Say what broke in one sentence, End call, move to the next sample, keep talking. Only S3 touches the laptop. A team that recovers calmly reads as a team that has shipped something before.

---

# PART 6 · QUESTIONS YOU WILL BE ASKED

Short answers here; the fuller versions are in `docs/QA_PREP.md`.

**"What is your accuracy?"** Depends which test, and choosing the test is this field's whole problem. On cloning tools it has learned: 0.0% to 24.4% error. On a 2025 cloner it has never heard, cloning the exact recording it is compared against: 13.2%. That second one is the honest number and it is why the prevention ladder exists.

**"Isn't this just another deepfake detector?"** Detection is one rung of four. The score decides whether to challenge; the challenge decides whether to escalate; the real person's phone decides whether money moves. That policy is in the code, not on a slide.

**"Why not use a bigger model, or fine-tune it?"** Because with 2,500 clips a big model memorises the cloners we happened to show it and fails on the next one. Freezing the big model and training 2,049 numbers on top generalises better. That is a published result, and it also means no GPU is needed anywhere.

**"What happens when a new cloning tool comes out next month?"** It degrades, like every detector. We measured the repair: 12 labelled recordings takes the error on that new cloner from 18.8% to 0.0%, tested on speakers it never saw. That refresh cycle is the business.

**"Only 2,000 samples? That is nothing."** Correct, and we say it first. It is a laptop-scale honest baseline, and it is the whole point of the roadmap: the biggest single gain available to us is more variety of cloners, which is exactly what scale and funding buy. We have already measured how much variety is worth.

**"Where is the blockchain?"** A hash chain over every decision on every call. Edit one past entry and every later fingerprint breaks, which we demonstrate live. Append-only and verifiable, and the final fingerprint can be anchored to a bank's chain. We did not build a token because a token would not make a decision more auditable.

**"Can you deploy this tomorrow?"** Not with this training set: two of our sources are research-only licences. The architecture is deployment-shaped; a commercial version retrains on licensed or self-generated data. That is a known, costed step, not a hidden flaw.

**"How is this different from Pindrop or ElevenLabs' own detector?"** They are cloud services, English-first, and none of them publishes a per-language, per-phone-line failure table. We run on the device, Indian languages first, and we publish the grid including the cells we fail, so a buyer can check the claim instead of trusting it.

**"Does the challenge really stop a live attacker?"** It stops a recording outright, because the phrase is one of 160,000. A live cloning setup would have to hear the phrase, generate it and play it back inside human reaction time. The scoring half was measured **in the parent repository this project was rebuilt out of**, `2026-sih-26104-kempelen`, `eval/challenge_eval.py`, logged in its `HONEST_LOG.md` on 2026-09-03 at commit `1f2f032`. **Pramaan itself has no challenge measurement and `eval/results.json` carries no challenge number**, so never say "we measured it" about this repo. The parent's result was negative and worth saying: in the honest regime the challenge settled 60.5% of deferred calls and got 47.8% of those wrong. The reading is that the challenge amplifies a detector that can already see the attack and cannot rescue one that cannot, which is exactly why the device push, the rung that does not depend on the detector at all, is the one that blocks the transfer. We did not have a live attacker to test against, and we say so.

---

# PART 7 · HOW TO TALK

**Use:** the listener, the gate, the ladder, the ledger, "a cloner it has never heard", "the voice is never the last factor", "we measured the repair", "we publish the cells we fail".

**Avoid:** "unfortunately", "we did not have time", "our accuracy is 99%" (nobody's is, and a sharp judge knows it), and any number that is not in `docs/NUMBERS.json`.

**If you do not know:** "I would have to check that." It costs nothing. Two of us quoting different numbers for the same thing costs us the presentation mark and the credibility mark together.
