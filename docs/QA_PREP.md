# Q&A preparation

Two minutes of questions. Every answer below is checkable against `eval/results.json`. If a question asks for a number that is not here, the answer is "we have not measured that" and then the nearest thing we have measured. Never invent.

Who answers: accuracy and evaluation S4; architecture and model S2; demo S3; business and scale S5; problem and users S1; roadmap and research S6. One person answers, nobody joins in.

---

### "What is your accuracy?"
Depends on the test, and picking the test is the whole field's problem. On generator families the model has seen, held-out clips, equal error rate runs from 0.0% (XTTS-v2) to 24.4% (EnCodec resynthesis). On a cloner released this year that appears nowhere in training, cloning the exact recording it is compared against, it is 13.2%, with a 95% confidence interval of 4.7% to 21.9% because that cell is only 23 held-out clones against 127 held-out genuine recordings. And a second number that matters more: at the threshold we actually ship, that unseen cloner is called synthetic only 69.2% of the time, deferred 0.0% and waved through 30.8%. Ranking transfers to a new generator; the absolute threshold does not. That is published behaviour for every passive detector, commercial ones included, and it is exactly why a high-value action always needs the device factor. Vendors quote only the first kind of number.

### "Why should we believe a small team's numbers?"
Because they are produced by one script anyone can run, `eval/experiments.py`, into one file, and every slide is generated from it. Held-out means held-out at the level of the recording: a bona fide clip and every clone made from it are always on the same side of the split. And the grid on slide 4 has red cells in it. A grid with no red cells is a grid where nobody ran the hard test.

### "What is the error bar on that number? You only have a few dozen clips."
Correct, and it is printed. The headline 13.2% is measured on 23 held-out clones against 127 held-out genuine recordings, and its 95% confidence interval is 4.7% to 21.9%. The interval comes from a cluster bootstrap that resamples parent recordings rather than clips, because under our protocol a genuine recording and the clone made from it are one unit, not two independent draws, and resampling the unit gives the wider and more honest interval. The corpus has 39 Chatterbox clips in total; the shipped head never trains on any of them, so on all 39 its EER is 5.7% (95% CI 3.0% to 8.8%). Two counts, two protocols, both published. And the worst-channel false-alarm cell, 0.79%, is one false alarm in 127 genuine recordings, 95% CI 0.14% to 4.33%, so we do not read it as a two-decimal rate either.

### "Isn't this just another deepfake detector?"
Detection is one rung of four. The passive score decides whether to challenge; the challenge decides whether to escalate; the registered device decides whether the money moves. A high-value transfer is never cleared by the voice, and that policy is in the code, not on a slide.

### "Why didn't you fine-tune the speech model?"
Because fine-tuning on the cloners you have teaches the model those cloners' fingerprints and it fails on the next one. A frozen self-supervised frontend with a small head generalises better out of domain: Pascu and colleagues, Interspeech 2024. We train about 2,049 parameters. The side effect is that nothing in the critical path needs a GPU.

### "What is actually new here? These pieces exist."
They do, and we name them on slide 6. Three things are ours. One, treating generator diversity as the design lever and measuring it on Indian-language speech: as bad as 39.6% with a few families depending on which, 13.2% with all 8 regardless; the previous build on two families sat at 35.9%. Two, the same-speaker, same-sentence held-out protocol so a cloner is scored against the recording it cloned. Three, the integration: streaming gate, challenge, device approval and a hash-chained ledger in one on-device system that runs with the Wi-Fi off.

### "How do you handle a bad phone line?"
Every clip is pushed through seven real codecs at training and test time: Opus at 24 and 8 kbps, G.722, G.726, G.723.1, Speex. Narrowband G.723.1 at 6.3 kbps is the hardest cell in the grid and it is on the slide. AMR-WB and EVS cannot be encoded with our toolchain, so they are listed as absent, not faked.

### "How fast is it, really?"
185 ms per update on the laptop CPU for a four-second window, real-time factor 0.046; 104 ms on the laptop GPU. The first legal decision is at 1.5 s of audio, median decision on seen families at 1.5 s.

### "How many calls can one server handle?"
The honest way to count is CPU seconds per call second, because a streaming window re-scores overlapping audio. At a one-second update that is 5.4 concurrent calls per core, so a 200-seat centre at full concurrency is 37 cores, one commodity server, no GPU. Memory per stream and thermal throttling under sustained load are not yet measured.

### "What happens when a new cloning tool ships next month?"
It degrades the passive layer, and we measured the repair rather than hoping. 12 labelled recordings of the new cloner take held-out error on it from 18.8% to 0.0%, scored on speakers the adapted model never saw. That quarterly re-evaluation is the subscription. A vendor who says their detector is permanent has not tested it on a cloner released after they shipped.

### "Your unseen-cloner number is high. Why is the system worth anything?"
Two answers. The direction of the error: on genuine speech it raises the alarm 1.1% of the time pooled across all 7 telephone channels, 0.4% on a clean line and 1.6% on the worst channel we measured (G.726 32 kbps), so it misses clones rather than accusing customers. And the design assumes exactly this: a call the passive layer cannot settle gets a challenge, and a high-value action always gets device approval. The demo showed the clone the detector missed being blocked by the registered device.

### "What is the blockchain part?"
A per-call SHA-256 hash chain: every score, verdict, challenge and approval is a block whose hash covers the previous block. Edit one past decision and every later hash breaks; we showed that live. It is append-only and verifiable, and the head hash can be anchored to a bank's private ledger or a public chain. We did not build a token, because a token would not make a decision more auditable.

### "Can this go to production as is?"
Not with this training set. IndicSynth and Meta MMS output are non-commercial research licences. The architecture and the pipeline are production-shaped; the production model is retrained on licensed or self-generated data, which is a costed step on the roadmap.

### "What about Tamil and Telugu?"
Bona fide speech in all three languages is in every test. The unseen-cloner test is Hindi only, because Chatterbox does not speak Tamil or Telugu; MMS and Apple TTS cover them on the seen side. A Tamil and Telugu held-out cloner (IndicF5) is first on the roadmap.

### "How is this different from Pindrop or Resemble?"
They run in the cloud, are English-first, and publish no per-language, per-codec failure grid. We run on the device, are Indian-language first, and publish the grid, including the cells we fail, so a bank can check the claim before buying.

### "Does the challenge really stop a live cloner?"
It stops a replayed or pre-rendered clone outright, because the phrase is one of 160,000. A live cloning pipeline must transcribe, synthesise and deliver inside human reaction time, and the response is scored as fresh evidence.

**Say the provenance, because it is not our measurement.** The scoring half was measured in the **parent repository this project was rebuilt out of**, `2026-sih-26104-kempelen`, in `eval/challenge_eval.py`, logged in its `HONEST_LOG.md` on 2026-09-03 under B1, at commit `1f2f032`. **Pramaan itself has no challenge evaluation**, and `eval/results.json` carries no challenge number. Anyone who says "we measured it" about this repo is wrong, and a judge who greps for it will find nothing.

**And the parent's result was negative, which is the answer worth giving.** Pooled over all seven channels, in the honest deployment regime (same-corpus, shipped detector), the challenge settled **60.5% of deferred calls, 95% CI 49.3% to 70.8%**, and got **47.8% of those wrong, 95% CI 34.1% to 61.9%**, while the passive layer was committing at 47.93% error. Where the detector did have signal it worked as designed: 78.9% settled at 10.5% error with an in-domain head, 68.7% settled at 7.1% error cross-corpus.

**The sentence that makes sense of all three rows:** the challenge **amplifies a detector that can already see the attack, and cannot rescue one that cannot**. Adding a second observation from a blind detector gives you two blind observations, not one sighted one. That is precisely why the third rung, out-of-band approval on the registered device, **does not depend on the detector at all**. It is the only rung whose correctness is independent of how good the passive score is, and it is the one that blocks the transfer in the demo.

We did not measure a live attacker in the loop, in either repository, and we say so. PITCH's 56.0% to 88.7% AUROC is their number on their data and appears in none of our results.

### "What if the attacker knows your detector?"
Half of that is measured and half of it is not, so take the measured half first. We ran the Malafide attack class (arXiv 2306.07655), a short linear filter convolved with the spoofed audio, in its black-box form: 9 random filters, 129 to 513 taps at 16 kHz, 0.05 to 0.35 of the filter energy off the centre tap, applied to 505 held-out spoof clips from the 6 seen families and scored against 127 held-out genuine recordings. The filter touches spoof audio only, because an attacker controls their own synthetic audio and not the victim's microphone, and the detector is the shipped bundle, not retrained, not refit and not recalibrated. **Held-out EER was 0.00% before the attack and 0.00% after it, on all 9 filters, and the share of clones called synthetic at the shipped band stayed at 100.0% against 100.0% before, on all 9.** Reproduce it with `python eval/malafide.py`; the rows are in `eval/results.json` under `adversarial_malafide`.

**Two details that make that a result rather than a shrug.** It held across the whole distortion range, from 29.7 dB signal-to-distortion down to 9.3 dB on `fir257_s0.35`, and at 9.3 dB the colouration is plainly audible, so inside this attack class the attacker runs out of perceptual budget before the detector runs out of margin. And the direction is the opposite of the one the attacker wants: on `fir257_s0.35` the median spoof score moves +0.508 in log-odds and on `fir513_s0.35` it moves +1.257, towards synthetic and not away from it. A convolutive filter is adding artefact for the head to see, not removing it.

**Now the half that is not measured, which is the half a sharp judge is really asking about.** This is the black-box variant. The published Malafide optimises the filter coefficients against the countermeasure, which needs gradients, so every number above is a lower bound on the damage the published attack would do and not an all-clear. **A white-box gradient attack against the frozen XLS-R frontend remains unmeasured, and adversarial training is out of scope on this hardware, because it needs gradients through a 300M-parameter frontend and we have no GPU for it.** The attack against the Gate's sequential decision, rather than against a single 4 s score, is unmeasured too. And the 2026 literature points straight at the gap: "Escaping the Linearity Trap" (arXiv 2605.30366) places the vulnerability in the transferable representation geometry of SSL models themselves, which means freezing XLS-R does not avoid it and may make transfer easier, since our frontend is public and identical for the attacker.

**Finish on the design, because that is the real answer.** The ladder was built for the case where the passive score is wrong, whatever made it wrong. A high-value transfer is never cleared by the voice, and a registered device does not care what filter the audio went through.

### "What did not work?"
Three things, all written down. A first head architecture let the easiest synthetic family dominate the loss, so a seen cloner scored as human until we weighted families equally. A first calibration band was degenerate and would have committed on any score; we widened it to a fixed uncertain zone. And the passive layer misses the 2025 cloner more often than we would like, which is exactly why step three of the ladder is mandatory.
