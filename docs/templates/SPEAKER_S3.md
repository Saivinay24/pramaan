# S3 · The live demo

**You speak third. 3:00 to 6:00. You drive the laptop. Nobody else touches it.**

Your job: make five things happen on screen, on time, and narrate them calmly. This is the single highest-scoring three minutes in the presentation, because it is the only part the judges cannot argue with.

Practise the whole run at least three times before the morning.

---

## 1 · Before you walk in

```bash
cd ~/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
scripts/demo.sh
```

Wait about 15 seconds for it to load the speech model, then open Chrome at **http://127.0.0.1:8770**.

- [ ] **Wi-Fi off** before you start the server. Proving it runs offline is part of the pitch, and you will say so.
- [ ] Laptop on mains power, notifications off, Do Not Disturb on.
- [ ] Volume at about 70%. You need to hear the clips.
- [ ] Browser zoom at 110% so the projector is readable. Full screen, no bookmarks bar.
- [ ] Run all five beats once in the actual room if you can get in.
- [ ] Have `docs/RUNSHEET.md` open on your phone as a fallback.

If the server refuses to start, the message will say why. The most common cause is that the model file is missing; the fix is `../.venv/bin/python eval/experiments.py --only ship`.

---

## 2 · What is on the screen

```
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ Pramaan   Live call | Audit ledger | Evidence      [on-device] [model] [ms]     │
 ├────────────────────────────────────────────────────────────────────────────────┤
 │ SOURCE [which audio ▼]   CHANNEL [which phone line ▼]   [Start call] [End call] │
 ├──────────────┬───────────────────────────────────────┬─────────────────────────┤
 │ INCOMING     │ RUNNING RISK SCORE                    │ VERIFICATION LADDER     │
 │ CALL         │   ● state       big probability       │  1 passive analysis     │
 │              │   [human ░░ undecided ░░ synthetic]   │  2 live challenge       │
 │ who is       │   score-over-time graph               │  3 device approval      │
 │ calling,     │   live waveform                       │  4 decision on record   │
 │ what they    │   update / earliest / decided / ms    │                         │
 │ want,        │                                       │  [Issue challenge]      │
 │ the HOLD box │                                       │  [Send push] [Block]    │
 ├──────────────┴───────────────────────────────────────┴─────────────────────────┤
 │ AUDIT CHAIN  #0 call opened  #1 score  #2 gate committed  #3 ...                │
 └────────────────────────────────────────────────────────────────────────────────┘
```

| control | what it does |
|---|---|
| **SOURCE** | picks the laptop microphone, or one of the bundled clips. Under it the screen prints the clip's **true origin**. Read that line out loud every single time. |
| **CHANNEL** | simulates a phone line. "Opus 24 kbps" is a normal internet call. "G.723.1" is the worst narrowband line. |
| **state chip** | goes Listening, then Verifying, then Genuine voice or Synthetic voice |
| **the meter** | the striped middle section is the undecided band. Inside it, the system refuses to guess. |
| **hold box** | the money: held, blocked, or cleared |
| **audit chain** | each new decision appears as a block along the bottom |

---

## 3 · The five beats

Total 3 minutes. Keep moving; do not wait for a clip to finish playing if you have made the point.

### Beat 1 · a real caller (about 30 seconds)

Source: **Genuine caller · Hindi**. Channel: **VoIP · Opus 24 kbps**. Click Start call.

> "This is a real recording of a Hindi speaker, pushed through a normal internet-call codec, streamed into the system piece by piece exactly as a live call would arrive.
>
> Watch the score. For the first {{min_commit}} seconds it refuses to decide, and that is by design, not by accident.
>
> *(it commits)* Genuine voice.
>
> Now look at the box on the left. The transfer is **still held**. Acoustic check passed, device approval still required. That is the whole philosophy: the voice is never the last factor."

### Beat 2 · a clone it has learned (about 40 seconds)

End call. Source: **Clone · XTTS-v2**. Same channel. Start.

> "Same pipeline, now a cloned voice from a family the system has been trained on. Watch.
>
> Score jumps to 0.99. Synthetic at {{min_commit}} seconds. Transaction blocked, before the caller has finished their first sentence.
>
> And look at the number in the corner: **{{lat_cpu4}} milliseconds** per update. That is on this laptop's ordinary processor. No graphics card, no cloud, and the Wi-Fi is off."

### Beat 3 · a cloner it has never heard, and it still catches it (about 30 seconds)

Source: **Clone · ElevenLabs professional voice clone**. Channel: **VoIP · Opus 24 kbps**. Start.

> "This one is different. This is a commercial voice clone, made with ElevenLabs, the tool an actual attacker would pay for. It was created the night before this presentation and it appears nowhere in our training data.
>
> *(it commits)* Synthetic, at 2 to 3 seconds, 0.99. On a cloning tool the system has never heard.
>
> One clip, so that is a demonstration and not a measured rate, and we say so. But it is the case that matters, because that is the tool the fraud is actually committed with."

**Known result, tested:** synthetic on a clean line, over VoIP and over the worst narrowband line. We also checked it is not an artefact of the file format: a real human recording through the same conversion stays at 0.01.

### Beat 4 · the hard case, and the point of the whole system (about 60 seconds)

Source: **Pair B · 2025 clone of the same person**. Channel: **clean**. Start.

> "Now the hardest case we could build for ourselves. This is Chatterbox, a cloner released this year, and we had it clone the exact recording it is being compared against. Same speaker, same sentence, same microphone. The only difference is that one was made by a machine."

**Expect it to say Genuine, or to sit in the middle band. That is the normal result and it is the point of the beat.** Say:

> "Look at the score. The listener reads this one as close to genuine. It has never heard this cloning tool, and against a brand-new cloner that happens to every detector in the world, including the commercial products. We publish that rather than hide it.
>
> **And this is exactly why we do not stop at the listener.**"

Click **Issue challenge**.
> "It asks the caller to say four random digits and a random Hindi word. One of a hundred and sixty thousand possible phrases. A recording cannot answer this."

Click **Send push**.
> "And then the step that actually stops the fraud. A notification goes to the real person's own registered phone."

Click **Not me**.
> "He says it is not him. Blocked. Logged. The money never moved."

### Beat 5 · the ledger (about 30 seconds)

Click the **Audit ledger** tab. Click **Tamper with block 2**. Then click **Verify chain**.

> "Every step you just saw is a block in a chain, each one fingerprinted together with the one before it. I am now editing one score after the fact.
>
> Verify. **Broken at block two**, and every fingerprint after it is invalid. A regulator or a court can check exactly what the system knew, and when."

**Hand over:** "S4 has the numbers behind everything you just saw."

### If you are short of time

Beats 1, 3 and 4 are the ones that must happen: a real caller held, an unseen commercial cloner caught, and the hard case where the ladder does the work. Beat 2 and beat 5 are the first to cut.

---

## 4 · If a judge asks for the microphone

Source: **Laptop microphone (live)**. Start, then either speak yourself, or hold a phone near the laptop and play a cloned clip.

We tested this exact path on this laptop, after recording 200 training clips through its own speaker and mic:

| played into the mic | result |
|---|---|
| an ElevenLabs commercial voice clone | synthetic at {{min_commit}} s, blocked |
| a real Hindi, Tamil or Telugu recording | human |
| a person speaking live | human |

Keep the phone within about 30 cm, medium volume, quiet room. Say clearly that it is live.

**The honest number behind this beat, in case a judge asks what it costs.** The speaker-to-microphone path is now scored and published in `eval/results.json` under `replay_mic`. On {{rm_replay_mic_n}} clips recorded through this laptop's own speaker and microphone ({{rm_replay_mic_n_bona}} genuine, {{rm_replay_mic_n_spoof}} clones), with that channel removed from training, the error rate is **{{rm_replay_mic_channel_heldout_eer}}**, clones are called synthetic {{rm_replay_mic_channel_heldout_catch}} of the time, and **{{rm_replay_mic_channel_heldout_fpr}} of genuine speech through the speaker is called synthetic**, which is far above the {{op_fpr_allchan}} we report on telephone lines. The model the demo runs does better than that, {{rm_replay_mic_shipped_eer}}, because it trains on this path, and we say that it is an in-sample number rather than quoting it as generalisation.

> "A room is a channel too, and it is the worst one we have measured. We scored it and published it rather than only demonstrating it. That is also why this beat ends with the device push and not with the detector."



**If the score sits in the middle band, do not panic and do not apologise.** Say:
> "That is the Gate refusing to guess, which is the designed behaviour. Watch what it does about it." Then issue the challenge and send the push.

---

## 5 · Terms you will say out loud

| term | full form | what to say if asked |
|---|---|---|
| **codec** | coder-decoder | the compression a phone line uses to squeeze the voice |
| **VoIP** | voice over internet protocol | a call over the internet, like WhatsApp |
| **Opus, G.722, G.726, G.723.1, Speex** | | five real telephone compression standards. G.723.1 at 6.3 kbps is the worst one, and we test on it |
| **narrowband** | | a phone line that throws away everything above 4 kHz, which is where a lot of the evidence lives |
| **prefix** | | the audio heard so far; the system scores a growing prefix, not a finished file |
| **hash chain** | | each record carries a fingerprint of itself plus the previous one |
| **SHA-256** | secure hash algorithm, 256-bit | the specific fingerprinting function |
| **defer** | | the system saying "not enough evidence yet", instead of guessing |

---

## 6 · Rules you must not break

- **Always read the true origin line aloud.** We never let anyone believe a bundled file is a live capture. If a judge asks "is this live?", the honest answer is exactly what it is doing.
- **Never claim a verdict before the screen shows it.** Narrate what happens, do not predict it.
- **If something breaks:** say what broke in one sentence, click End call, move to the next beat, keep talking. Do not debug. Do not let a second person come to the laptop. A team that recovers calmly reads as a team that has shipped before.
- **Do not explain the model.** That is S2's slot and they have already done it. You narrate behaviour.
- **Watch the clock.** If you are at 5:30 and have not done the ledger, skip beat 5 and hand over on time. S4 losing their slot costs more than the ledger gains.

---

## 7 · Your checklist

- [ ] Server started with Wi-Fi off, at least 15 minutes before we are called.
- [ ] All five beats rehearsed end to end, three times, with the words.
- [ ] You know that beat 4 is *expected* to read genuine, and what to say when it does.
- [ ] You know the microphone fallback and its honest caveat.
- [ ] `docs/RUNSHEET.md` open on your phone.
