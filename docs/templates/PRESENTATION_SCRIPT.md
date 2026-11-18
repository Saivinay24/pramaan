# Pramaan: presentation script

**SIH 2026 internal round. Slot 11:18 to 11:30. Ten minutes to present, two minutes of questions. Six speakers, everyone speaks.**

Every number in this script is generated from `eval/results.json` and `eval/results/latency.json`. If a number is not in this file, nobody says it on stage. "I would have to check that" is always an acceptable answer.

## Speaker slots

| Slot | Speaker | Owns | Minutes | Slide |
|---|---|---|---|---|
| S1 | ________ | The problem and the one-line idea | 0:00 to 1:20 | 1, 2 |
| S2 | ________ | What we built and what is new | 1:20 to 3:00 | 2, 3 |
| S3 | ________ | Live demo, drives the laptop | 3:00 to 6:00 | console |
| S4 | ________ | The evidence: numbers, the scaling law, the failure we planned for | 6:00 to 7:40 | 4 |
| S5 | ________ | Impact, scale, business model | 7:40 to 9:00 | 5 |
| S6 | ________ | Research base, roadmap, close | 9:00 to 10:00 | 6 |

Rules that decide our score:

- **No adjective answers.** Every claim gets a number, a mechanism or a named artifact. "It is scalable" scores nothing. "{{cap_streams}} calls per CPU core, measured, so a 200-seat centre is {{cap_cores}} cores" scores the mark.
- **Nobody speaks out of turn.** If a judge interrupts, the person whose slot it is answers. In Q&A, S4 answers anything about accuracy, S2 anything about architecture, S5 anything about business, S3 anything about the demo. S1 handles "what problem" questions, S6 handles "what next".
- **Never apologise for a limit. State it, then state the design that handles it.** The unseen-cloner number is not a weakness we confess, it is the reason the prevention ladder exists.
- **No numbers that are not on this page.**

---

## S1, 0:00 to 1:20. The problem. (Slides 1 and 2, top line)

Stand still, look at the panel, no slide reading.

> "Good morning. We are team Davinciable, problem statement 26104: real-time detection and prevention of voice cloning impersonation attacks.
>
> AI voices have stopped sounding like robots. A few seconds of anyone's voice, from a reel or a voice note, is now enough to make that voice say anything.
>
> So imagine your phone rings and it is your father's voice. He sounds stressed, he needs money right now, or an OTP. **You have no way to tell whether that is really him.** Not by listening. The voice is perfect.
>
> That is the problem in one sentence: the human ear has stopped being proof of identity, and everything we do on the phone still assumes that it is. The same call reaches a bank's finance desk in the CFO's voice, and there the number on the transfer has six more zeros.
>
> Caller ID can be faked. Calling back does not help if the attacker controls the number. And 'I know his voice' is exactly the thing being attacked.
>
> The problem statement asks for five things, and most teams will build only the first. Detect **during the call**, not on a recording afterwards. Give a **risk score you can act on**, not a label. **Prevent** the transaction, not just report it. Run **on the device**, so no audio leaves the building. And work in **Indian languages** over **real phone lines**.
>
> Our answer is called Pramaan, which means proof. The idea in one line: **the voice is never the last factor.** Pramaan listens to the live call, scores it every half second, and holds the money until something that is not the voice says yes."

Hand over: "S2 will show you what we built."

---

## S2, 1:20 to 3:00. What we built, what is new. (Slides 2 and 3)

> "Four parts, and I will name the one decision in each that matters.
>
> **The Listener.** A frozen multilingual speech model, XLS-R, pre-trained on 128 languages including Hindi, Tamil and Telugu. On top of it we train about two thousand parameters. Two thousand, not three hundred million. That is deliberate: fine-tuning a big model on a few cloners teaches it those cloners' fingerprints. Freezing it and training a small head is what generalises, and it is why the whole system runs on a laptop CPU with no GPU anywhere.
>
> **The Gate.** Every half second the score updates. The gate commits to a verdict only when three things hold: at least one and a half seconds of real audio, no padding tricks; the calibrated probability is outside the uncertain band; and the score has been stable for three updates. If those do not hold it says 'not yet', and 'not yet' triggers the next layer instead of a guess.
>
> **The Prevention ladder.** This is the half of the title most teams drop. When the gate defers, or when the action is high value, the caller is asked to repeat a random phrase in their own language, drawn from a hundred and sixty thousand possibilities, so a pre-recorded clone cannot answer. The response is scored as fresh evidence. And for a large transfer the final step is never the voice: a push goes to the real person's registered device. Approve there, or the money does not move.
>
> **The Ledger.** Every score, verdict, challenge and approval is a block in a SHA-256 hash chain. Edit one past decision and every later hash breaks. That is the blockchain half of this theme done honestly: an append-only, verifiable record a bank can anchor to its own chain.
>
> What is new. First, we treated **generator diversity** as the design principle, not the training data as a given. We built {{n_seen}} different synthesis families on this laptop, from Apple's on-device voices to a 2025 open model, and measured what each one buys against a cloner none of them resemble. Second, our hardest test is **same speaker, same sentence**: the unseen cloner clones the exact recording it is scored against, so nothing but the synthesis can be the tell. Third, **detection is a router, not a judge.** S3 will show you what that means."

---

## S3, 3:00 to 6:00. Live demo. (The console)

Before walking in: Wi-Fi off, `scripts/demo.sh` running, browser on `http://127.0.0.1:8770`, screen mirrored, notifications off, volume up.

Say the true origin of every sample out loud. The console prints it under the source selector.

**Beat 1, 30 s. A genuine caller.** Source: "Genuine caller, Hindi". Channel: Opus 24k (VoIP).

> "This is a real recording of a Hindi speaker, pushed through a VoIP codec, streamed into the system chunk by chunk exactly as a live call would be. Watch the score. For the first one and a half seconds the gate refuses to decide, by construction. Then it commits: genuine. Note what did not happen: the transfer is still held. Acoustic check passed, device approval still required. Voice is never the last factor."

**Beat 2, 45 s. A clone from a known family.** Source: "Clone, XTTS-v2". Same channel.

> "Same pipeline, a cloned voice from a synthesis family the model has seen. Score climbs, the gate commits synthetic at {{demo_decide_s}} seconds, and the transaction is blocked before the caller has finished their first sentence. Inference is {{lat_cpu4}} milliseconds per update on this laptop's CPU."

**Beat 3, 75 s. The pair.** Source: "Pair A, the real person", then "Pair B, 2025 clone of the same person".

> "Now the hard one. Pair A is a real FLEURS recording. Pair B is the same person, the same sentence, cloned by Chatterbox, a zero-shot cloner released this year that appears nowhere in our training data.
>
> [Run A: genuine.] [Run B, watch the score, then say whichever is true:]
>
> If the score climbs and the gate commits synthetic: 'Caught, on a cloner it has never seen. That is what training on {{n_seen}} families bought us.'
>
> If the score stays low or hovers in the band: 'Look at the score. The passive layer reads this clone as close to genuine. It is a cloner it has never met, and this is exactly what the published literature says happens to every detector, including the commercial ones.'
>
> This is the point of the design. A passive detector against a cloner it has never met is a coin you should not bet forty-two lakh on. So the system does not. Watch: issue the challenge." [Click Issue challenge.] "Random digits and a word, in Hindi. A recording cannot answer this. Now the step that actually stops the fraud." [Click Send push.] "The real Rajesh Menon gets this on his own phone. He taps 'Not me'." [Click Not me.] "Blocked. Logged. The money never moved."

**Beat 4, 30 s. The ledger.** Tab: Audit ledger. Click "Tamper with block 2", then "Verify chain".

> "Every step you just saw is a block. I edit one score after the fact. Verify: broken at block two, every later hash invalid. A regulator can check what the system knew and when."

Hand over: "S4 has the numbers behind what you just saw."

**Optional live beat, if time allows or a judge asks:** source "Laptop microphone", play the ElevenLabs clone from a phone held near the laptop. Tested on this laptop: synthetic at 1.5 s. Say: "this is a commercial voice clone made this morning, played into the laptop mic, live."

If anything breaks: say what broke in one sentence, switch to the next sample, keep talking. Nobody else touches the laptop.

---

## S4, 6:00 to 7:40. The evidence. (Slide 4)

This is the hardest slot. Deliver it as a result, not a confession. Left chart first, then the grid.

> "Every number here comes from one script, `eval/experiments.py`, into one file, and the slides are generated from that file. Held out means held out: a recording and every clone made from it always land on the same side of the split.
>
> **The scaling law, left.** We hold out the 2025 cloner entirely and ask: how many synthesis families does the detector need to see before it generalises to one it has never met? Train on a small set of families and the result depends on which ones you happened to have: across random choices it ranges from {{div_k1_min}} to as bad as {{div_worst_small}}. Train on all {{n_seen}} and it is {{div_kN}} regardless of choice. Diversity does not buy a lucky number, it removes the unlucky one. The previous build of this project, on two families, sat at {{legacy_unseen}} on this same cloner.
>
> **The grid, right.** Leave one generator out, train on the rest, across seven telephony codecs. Held-out family error runs from {{gm_best_eer}} for {{gm_best}} to {{gm_worst_eer}} for {{gm_worst}}. The red cells are on the slide because a grid with no red cells is a grid where nobody ran the hard test.
>
> **The failure we planned for.** A cloner released after you ship will degrade any passive detector. Ours is no exception, and we measured the repair instead of hoping: {{ad_shots0}} labelled recordings of the new cloner gives {{ad_eer0}}; {{ad_shotsN}} recordings gives {{ad_eerN}}, scored on speakers the adapted model never saw. That re-evaluation cadence is the product.
>
> **Calibration.** A score is only actionable if 0.8 means eighty percent. Expected calibration error is {{cal_iso_seen}} on seen families and {{cal_iso}} on the unseen cloner, so the probability the operator sees means what it says even off-distribution. First decision at {{min_commit}} seconds, {{fpr_clean}} false alarms on genuine speech on a clean line and {{fpr_worst}} on the worst of the seven channels ({{fpr_worst_chan}}), median decision at {{ttd_seen}} seconds. Every false-alarm number we say names its channel, because the commit band is derived per channel."

---

## S5, 7:40 to 9:00. Impact, scale, business. (Slide 5)

> "Who this protects: the treasury desk approving transfers by voice, the contact-centre agent under pressure, and the customer on the other end, because the system defers and asks rather than accusing a real person.
>
> Scale. {{lat_cpu4}} milliseconds per update on a laptop CPU means {{cap_streams}} concurrent calls per core at a one-second update, so a two-hundred-seat contact centre fits in {{cap_cores}} cores on one commodity server inside the bank's own network. No GPU, no cloud, no audio leaving the premises. Privacy and scalability are the same fact.
>
> Business model. An on-premise SDK licensed per seat, plus a subscription for what actually keeps this working: a quarterly re-evaluation against every new cloner that ships, with the recalibration pass. Marginal cost per call is near zero because nothing is sent to a third-party API. Adoption path: banks and NBFCs first, because they carry the loss and the compliance mandate; enterprise finance teams second; telecom operators third.
>
> Licence hygiene, before anyone asks: two of our training sources are non-commercial research licences. The production model is retrained on licensed or self-generated data, and that is a costed step on the roadmap, not a hidden flaw."

---

## S6, 9:00 to 10:00. Research base, roadmap, close. (Slide 6)

> "We did not invent the pieces, and we say so. Frozen speech model plus a small head: Pascu and colleagues, Interspeech 2024. Diversity drives generalisation: AUDETER, 2025. Short-prefix decisions and their traps: ICASSP 2026. Challenge-response: PITCH, AsiaCCS 2025. What we did is put them into one system that runs on a laptop, in Indian languages, over real codecs, with prevention built in and a ledger under it, and we measured every claim.
>
> Now the honest scale of what you have seen. This was built on one MacBook Air, in days, with no GPU and no budget. We trained on about **{{n_spoof}} synthetic clips from {{n_seen}} generators, and most of those are open-source models we ran ourselves.** Everything we have claimed is measured on that.
>
> Here is what changes if we go forward from this round. **First, data.** We gather samples from the cloners attackers actually use today, ElevenLabs, PlayHT, Resemble and every new one that ships, across many more Indian languages and dialects. Not {{n_seen}} generators, but fifty. We have already measured what variety is worth, and right now variety is the one thing we are short of. **Second, compute.** Everything here trains in seconds on a CPU; with real GPUs we train on hundreds of thousands of clips instead of two thousand. **Third, we publish the comparison.** Our numbers against the published state of the art and against the commercial products, on Indian languages and real phone lines, which is exactly where nobody has published one. Today a bank buying a voice-fraud detector has no way to check the claim. **Fourth, one bank's contact centre, live.**
>
> None of that changes the architecture. The Listener, the Gate, the ladder and the ledger are already the shape of the final product. What scales is the data and the compute behind it.
>
> Pramaan: proof before approval. Thank you."

---

## Q&A, 2 minutes. Who answers what

See `docs/QA_PREP.md`. The five most likely questions, one sentence each:

1. **"What is your accuracy?"** S4: "Depends on which test you mean, and that is the point. Seen families: {{gm_best_eer}} to {{gm_worst_eer}} held-out. A cloner from this year we never trained on: {{div_kN}}. That last number is why the ladder exists."
2. **"Isn't this just a deepfake detector?"** S2: "Detection is one rung. The transfer is cleared by the registered device, never by the voice."
3. **"Why not fine-tune a bigger model?"** S2: "Fine-tuning memorises the cloners you have. Frozen plus small head generalises, published result, and it removes the GPU."
4. **"Does it work over a bad phone line?"** S4: "Seven codecs in the grid, narrowband G.723.1 is the hardest cell and it is on the slide."
5. **"How is this different from Pindrop?"** S5: "They are cloud, English-first, and closed. We are on-device, Indian-language, with a published grid a bank can check before buying."
