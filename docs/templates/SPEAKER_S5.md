# S5 · Impact, scale and the business model

**You speak fifth. 7:40 to 9:00. Slide 5.**

Your job: turn the technology into money and deployment. Criterion 7 (scalability), criterion 8 (impact) and criterion 9 (business model) are 30 of the 100 marks, and almost all of them are yours.

The rule for your slot: **never answer with an adjective.** "It is scalable" scores nothing. "{{cap_streams}} calls per processor core, measured, so a 200-seat centre is {{cap_cores}} cores" scores the mark.

---

## 1 · What you say, word for word

**80 seconds, the shortest slot in the presentation.** Nothing here is optional. Walk the slide: who benefits, the three tiles, the record, the business.

> "Three people benefit here, and not all of them are inside a bank.
>
> The **officer about to approve a transfer** on a voice they trust. The **customer**, who gets asked a question rather than accused, because when the system is unsure it defers. And the **family** who gets that call in a voice they know.
>
> ### *(point at the three tiles)*
>
> Three numbers. A verdict in **{{min_commit}} seconds**, inside the caller's first sentence, so the warning arrives before the money moves.
>
> **{{op_fpr_allchan}} false alarms** on {{n_bona}} real callers across all {{n_channels_scored}} telephone channels, worst channel {{op_fpr_worst}}. That is a commercial number as much as a technical one: a fraud system that insults real customers gets switched off within a month.
>
> And **zero bytes of audio leave the building.**
>
> Every decision is **hash-chained**, so a regulator or a court can see what the system knew and when. That is the blockchain half of this theme, as evidence rather than a token.
>
> ### *(point at the business block)*
>
> The business is two parts. A **per-seat licence** for software on the bank's own hardware, and a **subscription** for continuous re-testing against every new cloning tool that ships.
>
> Most teams will offer you a detector. **A detector is a depreciating asset.** It gets worse every month whether you touch it or not. We sell the thing that keeps it working, and we can tell you what one refresh cycle costs, **because we ran one.**
>
> Banks and NBFCs first, they carry the loss. Enterprise finance next. Telecom last."

**If you have ten spare seconds**, add at the end: *"One limitation before anyone asks: two of our training sources are research-licence only, so a commercial version retrains on licensed data. A known step, not a hidden flaw."*

**Hand over:** "S6 will close with the research behind this, and where it goes next."

---

## 2 · The scale number, and why ours is lower than the obvious one

A judge with a calculator may challenge you here. Be ready, because getting this right is worth more than the number itself.

**The naive calculation:** one update takes {{lat_cpu4}} ms to process 4 seconds of audio, so one core could handle about 21 calls at once.

**Why that is wrong:** the system re-scores a sliding window every hop. With a 4-second window advancing every 1 second, each second of call audio is processed 4 times over. At a half-second hop, 8 times over.

**The honest calculation:** processor-seconds consumed per second of call = time per update divided by how often you update. That gives **{{cap_streams}} calls per core** at a one-second cadence.

If someone quotes 21 at you, the answer is:
> "One over the real-time factor assumes each second of audio is processed exactly once. A sliding window re-reads overlapping audio, so we report the number that accounts for the overlap. Ours is about four times lower than the naive one, and it is the one we would put in a contract."

**Two things we have not measured, and you say so before being asked:** memory per concurrent stream, and thermal throttling under sustained load. Also, the 200-seat figure assumes 100% of seats are on calls simultaneously, which no real contact centre reaches, so our sizing is pessimistic on purpose.

---

## 3 · All your numbers

| number | value | what it means |
|---|---|---|
| time per update, ordinary processor | **{{lat_cpu4}} ms** | 4-second window, no graphics card |
| real-time factor, processor | {{rtf_cpu4}} | it uses {{rtf_cpu4}} seconds of compute per second of audio |
| time per update, Mac graphics chip | {{lat_mps4}} ms | we quote the processor number because that is the honest deployment case |
| concurrent calls per core | **{{cap_streams}}** | at a one-second update cadence |
| cores for a 200-seat centre | **{{cap_cores}}** | at 100% simultaneous occupancy, which is pessimistic |
| earliest decision | {{min_commit}} s | before the caller finishes a sentence |
| median decision time | {{ttd_seen}} s | on families it has learned |
| false alarms on real callers | {{op_fpr_allchan}} | pooled across {{n_bona_allchan}} genuine recordings, 3 languages, all {{n_channels_scored}} codecs |
| worst single channel | {{op_fpr_worst}} | {{op_fpr_worst_chan}}; the clean line is {{op_fpr_clean}} |
| audio sent to the internet | **zero bytes** | |
| third-party API cost per call | **zero** | nothing leaves the machine |

If you are asked an accuracy question, hand it to S4: **"S4 has that, and covered it just now."**

---

## 3b · Latency against the named commercial systems, and the rule for using it

This is the one axis where a laptop with no graphics card beats products that run in data
centres, so it is worth saying on stage. It is also the one comparison that is easy to ruin.

**Source:** the Podonos audio deepfake detection benchmark, published 14 August 2026, a
vendor-independent third-party evaluation. Ours: `eval/results/latency.json`, {{lat_cpu4}} ms
median per 4-second window on the M4 laptop processor with no graphics card, real-time factor **{{rtf_cpu4}}**.

| system | real-time factor | where it runs |
|---|---|---|
| Corsound AI | 0.035 | cloud API |
| **Pramaan (ours)** | **{{rtf_cpu4}}** | **laptop processor, offline, no graphics card** |
| Pindrop | 0.076 | cloud API |
| Hive | 0.34 | cloud API |
| Resemble AI Detect | 0.40 | cloud API |
| Reality Defender | 1.52 | cloud API, and above 1.0 means it cannot keep up with a live call at all |

**What you are allowed to say.** Of the systems in that benchmark whose real-time factor is
published, Pramaan is faster than four and slower than one, and it is the only one of the six
that runs on the caller's own device with the network off. Reality Defender at 1.52 is the
line worth pointing at: a real-time factor above 1 means the detector falls further behind
the longer the call runs.

**The rule, and say it out loud when you use the table.** This is a **latency comparison
only**. Never put our error rate next to their accuracy column. Their accuracy numbers are
measured on English audio on a different corpus, and mixing corpora is exactly the mistake
this team already made once and published: 0.59% on a corpus-confounded benchmark became
32.03% under a matched-pairs control. Saying that on stage turns the table from a risk into a
credibility beat.

> "On speed we can compare directly, because speed is measured the same way everywhere.
> Real-time factor {{rtf_cpu4}} on a laptop processor, against 1.52 for Reality Defender,
> 0.40 for Resemble and 0.076 for Pindrop, all from the independent Podonos benchmark of
> August this year. What we will not do is put our error rate next to their accuracy column.
> Those are English, on a different corpus, and comparing across corpora is the exact mistake
> we published a document about."

**[UNVERIFIED, NEEDS A HUMAN TO CHECK]** the Podonos benchmark names seven commercial systems
in total; a published real-time factor could be found for only the six in the table above.
Do not say "we beat seven systems on speed". Say six, or say "every system in that benchmark
with a published real-time factor except one".

---

## 4 · The business model, in more depth

### What the customer buys

1. **A per-seat licence.** Software that installs inside the bank's own network. No audio leaves. Priced per agent seat, or per concurrent monitored call, sized against the {{cap_cores}}-cores-per-200-seats figure so the customer can compute their own hardware cost.
2. **A re-evaluation subscription.** Every quarter we test the deployed model against every new cloning tool released since the last cycle, retrain, recalibrate, and hand over a fresh model and a fresh evaluation report.

### Why the subscription is the real product, and not a gimmick

Because we measured that the model decays and measured what fixing it costs. S4's number: **{{ad_shotsN}} labelled recordings** of a brand-new cloner take the error on it from {{ad_base}} to {{ad_eerN}}.

Say this line, it is the strongest business sentence in the deck:
> "Most teams will tell you they built a detector. A detector is a depreciating asset: it gets worse every month whether you touch it or not. We are selling the thing that keeps it working, and we can show you what one refresh cycle costs, because we ran one."

The honest part attached to it: somebody has to obtain and label those recordings of the new cloner. That is real work, and it is what the subscription pays for.

### Why the cost structure works

| | |
|---|---|
| marginal cost per call | near zero: it is processor time on hardware the customer already owns |
| third-party API fees | none |
| cloud egress and storage | none |
| what we actually sell | the licence, plus the ongoing evaluation work |

### Adoption order, and the reason for each

1. **Banks and NBFCs.** They carry the fraud loss directly, they already have a compliance mandate for call handling, and they have budget. They are also the ones who cannot send customer audio to a cloud service, which is exactly our shape.
2. **Enterprise finance teams.** Same attack, smaller budget, faster procurement.
3. **Telecom operators.** Biggest reach, but needs regulatory movement, so it is last, not first. **The Indian regulatory primitive here is CNAP under TRAI, calling name presentation, not the American STIR/SHAKEN that most decks cite.** CNAP verifies the line a call arrives on; Pramaan verifies the voice on it. They are complementary layers rather than competitors, and an operator that has deployed CNAP still has no answer to a cloned voice on a correctly attributed line. **[UNVERIFIED, NEEDS A HUMAN TO CHECK]** the current CNAP rollout status in India. Do not say it is deployed. Say it is the India-relevant primitive and that we designed to sit above it, whatever stage it is at.

### Licence limitation, stated by us

Two of our training sources, IndicSynth and Meta MMS output, are **non-commercial research licences**. The architecture and pipeline are production-shaped, but a commercial model retrains on licensed or self-generated data. That is a costed step on the roadmap. Saying it yourself scores; being caught on it costs.

---

## 5 · Impact, stated without inventing figures

**Do not invent a market size in crores.** Judges have heard fabricated TAM slides all day. Use mechanisms instead.

- **The direct saving** is one prevented transfer. Against a near-zero per-call inference cost, a single averted fraud pays for a long deployment. Let them do that arithmetic themselves; it is more convincing than us doing it.
- **The user experience win:** when the system is unsure it defers and asks a question rather than accusing. Measured false alarms on genuine callers: {{op_fpr_allchan}} pooled across all {{n_channels_scored}} channels, {{op_fpr_worst}} on the worst one ({{op_fpr_worst_chan}}). A fraud system that insults real customers gets switched off within a month, and every bank in the room knows it.
- **The systemic contribution:** the failure grid on slide 4. Today a bank buying a voice-fraud detector has no published table telling them which languages and which phone lines it fails on. Every vendor shows one number on English studio audio. Publishing the grid is worth something to the whole market, beyond our own product.

---

## 6 · Full forms and terms

| term | full form | meaning |
|---|---|---|
| **NBFC** | non-banking financial company | lenders like Bajaj Finance or Muthoot; heavy phone-based operations |
| **contact centre** | | the room of agents who take customer calls |
| **treasury desk** | | the team inside a company that moves large sums |
| **on-premise** | | software running on the customer's own hardware, not in a cloud |
| **SDK** | software development kit | the package a customer's engineers plug into their own system |
| **API** | application programming interface | the defined way one piece of software talks to another |
| **latency** | | how long one answer takes |
| **real-time factor** | | compute time divided by audio duration; below 1 means faster than real time |
| **concurrency** | | how many calls are being watched at the same moment |
| **core** | | one processing unit inside a processor; a normal server has 32 to 128 |
| **marginal cost** | | the cost of handling one more call |
| **per-seat licence** | | priced per agent, the normal way contact-centre software is sold |
| **compliance mandate** | | a rule from the regulator that the bank must follow |
| **egress** | | data leaving a network, which cloud providers charge for. Ours is zero |

---

## 7 · Questions you will get

**"How much will you charge?"**
> "We would price per seat or per concurrent monitored call, and we can size it because we know the hardware cost: about {{cap_cores}} cores for 200 seats. We are not going to invent a rupee figure we cannot defend in front of a procurement team. The unit and the cost basis are what we have."

**"Why would a bank buy this instead of Pindrop?"**
> "Three reasons. It runs inside their network, so customer audio never leaves, which for several of them is a hard requirement rather than a preference. It is built and evaluated on Indian languages over Indian phone conditions. And we publish the failure grid, so they can check the claim before buying instead of trusting a marketing number."

**"How do you compare to Pindrop on the numbers?"**
> "On speed, directly, and it is in our favour: real-time factor {{rtf_cpu4}} on a laptop processor against their 0.076 in the independent Podonos benchmark from August. On accuracy I will not give you a comparison, because theirs is measured on English audio on a different corpus and ours is Indian-language speech on ours. Comparing across corpora is how you get a number that falls apart, and we published a document about doing exactly that to ourselves once. Running a public baseline on our own data is on the roadmap, and until that exists the comparison does not."

**"What is your moat? Anyone can download the same model."**
> "The model is the commodity part, deliberately. What is not easy to copy is the evaluation: the generator variety, the Indian-language grid across seven codecs, and the discipline of re-testing every quarter against tools that did not exist last quarter. That is an operating capability, not a download."

**"Can it handle a whole telecom operator's traffic?"**
> "Not as it stands, and we scope that out explicitly. Our measured figure is contact-centre scale: {{cap_streams}} calls per core. Operator scale needs different engineering and regulatory work, and it is last on our roadmap for that reason."

**"What about memory, and heat, under sustained load?"**
> "Not measured. We will not guess at it. Everything on this slide is measured on this machine."

---

## 8 · What not to say

- **No adjectives without numbers.** "Highly scalable", "very fast", "extremely cheap" all score zero.
- **No invented market size, no invented pricing.**
- **Do not quote 21 calls per core.** That is the naive figure and it is wrong; use {{cap_streams}}.
- **Do not claim production readiness.** Say the licence step out loud instead. It reads as scope control, not weakness.
- Do not go past 9:00. S6 needs a full minute to close.
