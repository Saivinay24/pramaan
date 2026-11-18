# SIH 2026 portal submission copy

Paste-ready text for `sih.gov.in/participate` Idea Submission, PS **26104**, AICTE Cyber Security
Cell, theme Blockchain and Cybersecurity.

Every number below is a value in `docs/NUMBERS.json`. No em dashes. The portal warns that no
changes are entertained after submission, so nothing here is approximate or aspirational.

---

## 1. Idea Title

*Limit 100 characters.*

```
Pramaan: on-device real-time detection and prevention of AI voice clone impersonation calls
```

---

## 2. Abstract / Summary

*Limit 10000 characters.*

```
A voice you recognise is no longer proof of who is calling. In India 47 percent of adults have
experienced an AI voice scam or know someone who has, double the seven-country average, and 66
percent would respond to a distress message appearing to come from a parent, partner or child
(McAfee, 2023). Three seconds of audio is enough to clone a voice. Europol found that raising
awareness does not reliably improve anyone's ability to detect a clone in the moment, so the check
has to happen on the call rather than in the listener's ear.

Pramaan is an on-device system that verifies voice integrity during a live call and prevents the
transaction when the voice cannot be trusted. It scores the stream every half second, returns a
first verdict at 1.5 seconds, and never allows the voice alone to release a high-value action.
The same detector serves a family emergency call and a corporate approval call; only the response
rung differs.

The system has four layers. The Listener decides whether the voice is synthetic, using a frozen
300 million parameter multilingual speech model covering 128 languages with 2,049 trained
parameters on top, and no GPU in the critical path. The Gate decides whether there is enough
evidence to speak, committing or deferring on a calibrated probability, never before 1.5 seconds
of real audio and never inside an uncertain band derived per carrier from genuine speech at a
2 percent false positive budget. The Prevention ladder decides what is allowed to release the
money: a live challenge in the caller's own language from 160,000 combinations, out of band
approval pushed to the registered device of the person being claimed, a callback on the number of
record, then an operator block or clear. The Ledger writes every score, verdict, challenge and
approval into a SHA-256 hash chain, so altering any past entry breaks every hash after it.

The innovation is treating generator diversity as a measured design rule. Trained on one synthesis
family, error against an unseen cloner swings between 4.5 percent and 39.6 percent depending on
which family is available. Trained on all eight, it settles at 13.2 percent regardless of subset,
collapsing a 35.1 point spread to zero. This converts an unpredictable model into a specifiable
one and yields a maintenance rule: 12 labelled recordings absorb a brand new cloner to 0.0 percent
error with no regression on families already seen.

Against a 2025 zero-shot cloner held entirely out of training, which clones the exact genuine
recordings it is scored against so speaker, sentence and content cannot be the tell, the shipped
system catches 69.2 percent of clones and misses 30.8 percent, 95 percent interval 53.6 percent to
81.4 percent. At a tuned threshold the equal error rate is 13.2 percent, 95 percent interval 4.7
percent to 21.9 percent. Those misses are why the prevention ladder is mandatory: the two rungs
that block a transfer do not depend on the audio at all.

Performance is measured across seven real telephony carriers applied at training and test time:
clean, Opus 24 kbps, Opus 8 kbps, G.722, G.726, G.723.1 6.3 kbps and Speex wideband. The corpus is
3,429 clips, 510 bona fide FLEURS recordings in Hindi, Tamil and Telugu and 2,919 synthetic clips
across nine generator families.

One scoring update costs 185 ms on CPU at a 4 second window, a real-time factor of 0.046, which is
37 CPU cores for a 200 seat contact centre at full concurrency with no GPU. No audio leaves the
device, there is no cloud API and no network request in the scoring path, so the privacy
requirement is met structurally. It deploys as an on-device library behind an API for banking,
enterprise telephony and operator infrastructure, and the ledger exports for on-chain anchoring.
```

---

## 3. Idea Description

*Limit 50000 characters.*

```
1. THE PROBLEM

A voice you recognise is still treated as proof of who is calling. It no longer is.

In India, 47 percent of adults have personally experienced an AI voice scam or know someone who
has, against a seven-country average of 25 percent, and 66 percent say they would respond to a
distress message appearing to come from a partner, parent or child, against 45 percent globally
(McAfee, The Artificial Imposter, 2023). Three seconds of audio is enough to clone a voice at up
to 95 percent accuracy in the same testing, and 53 percent of adults post their own voice online
at least weekly, which supplies the raw material for free.

The harm falls hardest where there is least institutional protection. In 2025, documented consumer
deepfake fraud reached 1.34 billion dollars across 289 incidents, roughly eighteen times the 74.9
million dollars documented across 41 corporate incidents, and private individuals were recorded as
victims 58 percent more often than their own identity was used as the vector (Resemble AI, 2025
Deepfake Threat Report). An elderly Delhi resident lost 50,000 rupees to a cloned voice in a fake
kidnapping call (NDTV, 2024). A mother in Arizona heard what she was certain was her 15 year old
daughter sobbing, followed by a ransom demand, and later testified before the US Senate Judiciary
Committee. A mother in California wired money after hearing her daughter's voice say "I'm so
sorry, Mom. I love you." Her daughter was never in danger.

The same technique scales upward without modification. A finance employee at the engineering firm
Arup transferred 25.6 million dollars after a video call on which every other participant was
synthetic. A cloned voice has defeated the voice-biometric authentication that UK banks sell as
being more secure than a PIN (BBC, 2024). One attack pattern, from a grandparent to a
multinational: a familiar voice, an urgent context, and a request to move money.

Awareness is not the control that works. Europol's Innovation Lab found that increasing people's
awareness that deepfakes exist does not reliably improve their ability to detect one in the
moment, because the technology is built to exploit the default human assumption that what we hear
is authentic. If the listener cannot be trained to catch it, the call itself has to be checked,
and the decision has to be taken out of the listener's ears.

2. THE SOLUTION

Pramaan is a real-time voice integrity and prevention system that runs on the device handling the
call, with no cloud dependency. It scores the live stream every half second and routes the
decision rather than merely announcing it. The detection layer is identical whether the call is a
daughter in apparent distress or a director requesting a transfer; what differs is the response
rung that follows. Four layers, each answering one question.

Layer 1, the Listener: is this voice synthetic. A frozen wav2vec2 XLS-R 300 million parameter
multilingual model covering 128 languages, read at layer 5, mean and standard deviation pooled,
with a head of 2,049 trained parameters. Scores are calibrated with isotonic regression per prefix
length, so 0.8 means eight calls in ten. An operator can act on a probability; a ranking score
cannot be acted on.

Layer 2, the Gate: is there enough evidence to speak. Streaming commit or defer. It commits only
after 1.5 seconds of real audio, never tile padded, only outside an uncertain band, and only after
three consecutive stable updates. The band is derived per carrier from bona fide speech alone at a
2 percent false positive budget, because genuine speech scores higher the harder a codec squeezes
it. On a clean line the band is narrow; on a G.723.1 6.3 kbps line it is much wider and the Gate
defers more often. A committed verdict does not reopen.

Layer 3, the Prevention ladder: what is allowed to release the money. Five rungs, each depending
less on the detector than the one before. Rung 1 is the voice check. Rung 2 is a live challenge, a
random phrase in the caller's own language drawn from 160,000 combinations, which the caller must
repeat. Rung 3 is out of band approval pushed to the registered device of the person being
claimed, which does not depend on the audio at all. Rung 4 is a callback on the number of record.
Rung 5 is an operator block or clear. A high-value action is never cleared by the voice alone, and
this is enforced in code rather than in policy.

Layer 4, the Ledger: what happened, provably. Every score, verdict, challenge, device response and
operator decision becomes a block in a SHA-256 hash chain, each carrying the hash of its
predecessor. Editing any past block breaks every hash after it. A verify endpoint and an export
make the chain auditable and anchorable on-chain where an external root of trust is required.

3. INNOVATION AND UNIQUENESS

Self-supervised frontends with light classification heads are established practice. The novel
contribution is treating the diversity of synthesis families in training as a measured design
rule, and quantifying what it buys.

Hold out a 2025 zero-shot cloner entirely. Train on k synthesis families over random subsets and
measure error against that unseen cloner. At k equal to one the result depends heavily on which
family happens to be available, ranging from 4.5 percent to 39.6 percent. As k grows the spread
narrows, and at all eight families the result is 13.2 percent regardless of which subsets are
drawn. A 35.1 point spread collapses to zero.

The engineering consequence is that diversity buys variance reduction, not merely a better mean.
A detector whose performance depends on which cloners the builder happened to collect cannot be
specified or contracted. One whose performance is stable across subsets can be. An earlier build
of this project, trained on two families, scored 35.9 percent on the same cloner against 13.2
percent now.

The second contribution is architectural: prevention is a first-class layer, not an alert. Most
systems in this space terminate at a score. The problem statement asks for detection and
prevention, and the two rungs that actually stop a fraudulent transfer, the device push and the
callback, are independent of the audio and therefore unaffected by any detector error.

4. TECHNICAL APPROACH AND COMPLEXITY

The hard problems here are not model capacity, they are threshold policy, calibration and
streaming behaviour under real channels.

Thresholds are derived, not chosen. For each of seven carriers the uncertain band is computed from
bona fide speech alone at a fixed false positive budget, which means the operating point is
specified by a policy target rather than tuned against test data.

Calibration is per prefix length, because a verdict at 1.5 seconds and one at 4 seconds carry
different confidence. Isotonic regression maps raw scores to probabilities so the displayed number
has an operational meaning.

Streaming requires a commit-or-defer policy rather than a per-frame classification. The Gate
enforces a minimum audio duration, an uncertainty band and a stability requirement before it will
speak, and deferring is treated as a correct outcome rather than a failure.

The trained surface is deliberately 2,049 parameters over a frozen frontend. This trains on a
laptop, ships as a small artifact, runs without a GPU and makes the system auditable, since the
decision boundary is small enough to inspect.

5. MEASURED PERFORMANCE

Against a 2025 zero-shot cloner held entirely out of training, cloning the exact genuine
recordings it is scored against so speaker, sentence and content cannot be the tell: the shipped
system catches 69.2 percent and misses 30.8 percent, 95 percent interval 53.6 percent to 81.4
percent. At a tuned threshold the equal error rate is 13.2 percent, 95 percent interval 4.7
percent to 21.9 percent, from a cluster bootstrap resampling parent recordings rather than clips,
since a genuine recording and its clone are one unit under this protocol. Scored across all 39
clips of that cloner, which the shipped head never trains on, the equal error rate is 5.7 percent,
95 percent interval 3.0 percent to 8.8 percent.

Hold out each generator family in turn, train on the rest, and test cold on the one withheld: six
of the eight return 0.0 percent equal error rate, and Meta MMS returns 0.8 percent.

Streaming behaviour on seen families, clean channel: commits on 100.0 percent of calls, wrong on
0.0 percent of committed calls, false alarm on 0.0 percent of genuine speech, median decision at
1.5 seconds.

Seven carrier conditions are applied at training and test time: clean, Opus 24 kbps, Opus 8 kbps,
G.722 64 kbps, G.726 32 kbps, G.723.1 6.3 kbps and Speex wideband. The corpus is 3,429 clips: 510
bona fide FLEURS recordings in Hindi, Tamil and Telugu under CC-BY 4.0, and 2,919 synthetic clips
across nine generator families, eight in training and one held out, with 70,424 cached embeddings.

6. FEASIBILITY AND PRACTICABILITY

The system exists and runs. One scoring update costs 185 ms on CPU at a 4 second window, a
real-time factor of 0.046. At a one second refresh that is 5.4 concurrent calls per CPU core, so
37 cores serve a 200 seat contact centre at full concurrency with no GPU.

An operator console is working software, not a mockup: live call scoring with a running risk
trace, the prevention ladder with challenge and device push, and an audit view where a recorded
block can be altered and the chain shown to break.

Deployment is an on-device library behind an API, integrating with banking applications,
enterprise telephony and operator infrastructure without moving audio off the machine.

7. PRIVACY AND SECURITY

No audio leaves the device. There is no cloud API, no upload and no network request in the scoring
path, so the privacy requirement is met structurally rather than by policy: audio that never
leaves cannot be intercepted, retained elsewhere or subpoenaed from a third party.

Robustness was tested against a black-box Malafide style convolutive attack: 9 random non-causal
FIR filters of 129 to 513 taps at 16 kHz, applied to 505 held-out spoof clips from 6 seen families
against 127 held-out genuine recordings, against the shipped model with no retraining. Equal error
rate remained 0.00 percent and catch rate 100.0 percent on all 9 filters, down to a distortion
floor of 9.3 dB.

8. SCALE OF IMPACT

Two surfaces, one detector. The consumer surface is the larger one by documented loss: family
emergency and impersonation scams, where India already reports roughly double the global exposure
rate, and where the on-device design matters most because a handset has no security operations
team behind it. The institutional surface is the approval call in banking, enterprise finance and
government, where a single successful impersonation moves a large sum in minutes, and where the
full prevention ladder including device approval is instrumented today. Coverage is multilingual by construction:
the frontend spans 128 languages and Hindi, Tamil and Telugu bona fide speech appears in every
test, which matters for Indian deployment where the attack will not arrive in English.

Because it runs on commodity CPU with no GPU and no cloud dependency, unit economics scale to
contact centres and to telecom operator infrastructure without per-call inference cost, and it
remains deployable in air-gapped or bandwidth-constrained environments.

9. SUSTAINABILITY AND MAINTENANCE

New cloners ship continuously, so the maintenance question is the real one. It is measured: 12
labelled recordings of a brand new cloner bring error on it to 0.0 percent with no regression on
families already seen, and 3 recordings already reach 6.3 percent. One re-evaluation cycle is
therefore small and costed rather than open-ended.

Every published number is generated by the evaluation pipeline into a single results file, and the
documents, deck and console are generated from that file, so a re-run propagates changes
everywhere without manual transcription.

10. USER EXPERIENCE

The console is built for a fraud operator, not for a model developer. The first screen states who
is calling, who they claim to be, the action requested, its value, the voice verdict and the single
next step to take. The prevention actions sit directly beneath that line. Model details, evaluation
grids and calibration are one click away in a separate view rather than occupying the decision
surface. Operators are never shown a bare score without the action it implies.

11. DESIGN DECISIONS WE MADE DELIBERATELY

Two capabilities were available to us and left out on purpose.

Cross-session voice matching against enrolled historical samples would raise accuracy, and it
requires storing a voiceprint for every protected person. That is a permanent biometric database
and a standing breach liability, and it is exactly the asset an attacker wants. Pramaan needs no
enrolment, stores no voiceprint, and protects a first-time caller as well as a known one.

Cloud inference would remove the CPU budget entirely. It would also mean shipping every customer
conversation to a third-party server. Every commercial detector on the Podonos benchmark works
this way. Pramaan runs with the network switched off, which is the only architecture that can be
deployed inside a bank's own perimeter without a data transfer agreement.

We also ship a threshold tuned for roughly one percent false alarms rather than the setting that
would flatter our headline accuracy, because a fraud desk that accuses real customers gets
switched off within a week, and the four non-voice checks are what carry the rest.

12. FUTURE SCOPE

Language coverage to all 22 scheduled languages of India. The frontend already spans 128
languages, so this is an evaluation and calibration exercise rather than new research, and it
makes Pramaan deployable by any state government and any national bank.

A handset application. The detector is CPU-only and fully offline, which means it can run on a
mid-range Android phone. This is the step that reaches the people absorbing the largest share of
documented loss, the families receiving the fake emergency call, who have no fraud desk behind
them.

Telecom-layer deployment. At 5.4 concurrent calls per CPU core with no GPU, operator-side
screening is economically viable at national scale. Combined with CNAP style caller name
authentication, the line and the voice get verified together rather than separately.

Regulatory integration. The hash-chained ledger already exports for external anchoring, which
gives a regulator a verifiable record of what the system knew and when, without having to trust
the operator holding it.

A national reference corpus. The generator-diversity result says that breadth of synthesis
families is what makes a detector generalise. An Indian-language, Indian-telephony corpus built
on that principle would raise the floor for every team working on this problem, not just ours.

13. ALIGNMENT WITH THE PROBLEM STATEMENT

Multi-layer voice authenticity analysis: a frozen self-supervised frontend capturing acoustic and
spectral structure, evaluated across seven telephony carriers.

Real-time risk scoring: a calibrated probability every half second, first verdict at 1.5 seconds,
thresholds derived per carrier at a stated false positive budget, configurable per scenario.

Contextual enrichment and alerting: caller, claimed identity, requested action and its value shown
with the recommended next step.

Prevention: the five-rung ladder, addressing the half of the problem statement that detection alone
does not.

Scalability and privacy: 37 CPU cores for a 200 seat centre, fully on device.

Blockchain and cybersecurity theme: a SHA-256 hash chain over every decision, verifiable and
exportable for external anchoring.
```

---

## 4. Idea Template (PDF upload)

Upload `ppt/Pramaan_SIH2026_Idea.pdf`.

- 6 pages, matches the mandated SIH format.
- **1.4 MB**, well inside the portal's 10 MB cap.
- Slide 1 carries **Team ID 149829**, Team Name Davinciable, PS ID SIH26104. Verified in the
  exported PDF text, no placeholder remains. Ready to upload.

## 5. Technology Bucket

A dropdown. The problem statement's own theme is **Blockchain and Cybersecurity**, so pick that if
it is offered. Confirm against the actual options in the list before selecting.

## 6. YouTube Link (optional, but do it)

The portal takes a **link**, not a file, so the demo video has to be uploaded to YouTube first.

- File: `video/out/pramaan_demo_delivery.mp4`, 8:47, 1920x1080, 21 MB.
- Upload as **Unlisted**, not Private. Private is unviewable by judges.
- Suggested title: `Pramaan | SIH 2026 PS 26104 | Real-time voice clone detection and prevention`
- The video is silent apart from the cold open until the six narration tracks are recorded and
  `python3 video/build.py` is run. **Do not upload the silent cut.**
