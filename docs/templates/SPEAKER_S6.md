# S6 · The close

**You speak last. 9:00 to 10:00. Slide 6.**

Your job is simple. Say three things, then stop. The last ten seconds are what the judges hear while they write our score.

**You do not have to read the paper names on the slide.** They are printed there for the judges to read. You just point at them.

---

## 1 · What you say

**About 65 seconds.** Short sentences. Full stops, not commas. Take your time, and pause where it says to.

> "This slide is the research we built on. We did not invent these pieces. We name them before anyone asks.
>
> What is ours is putting them together. Indian languages. Real phone lines. One laptop. And we measured every claim, including the ones that go against us.
>
> *(pause. change tone. this is the part that matters)*
>
> Now, the honest size of this.
>
> One MacBook Air. A few days. No graphics card. No budget. About **{{n_ai_train}} fake voice clips, from {{n_seen}} free tools we ran ourselves.**
>
> So, what Pramaan looks like at the finals. *(point at the band along the bottom)*
>
> **Trained at scale.** Fifty generators or more, including the paid cloners attackers actually use. On real machines, hundreds of thousands of clips.
>
> **Every scheduled Indian language**, not three. Each with its own held-out cloner.
>
> **Benchmarked in public**, against the paid products, on Indian languages. Nobody has done that.
>
> **And shipped, not demonstrated.** An SDK a bank installs inside its own network, and a pilot on live calls.
>
> *(pause)*
>
> None of this changes what we built. The four layers stay. Only the data grows.
>
> *(stop moving. look at the judges. slow right down)*
>
> **Pramaan. Proof before approval.**
>
> **Thank you.**"

**If you have spare time**, add before the pause: *"And the ledger anchored on a chain."*

**If you are running late**, cut straight from "no budget" to "Pramaan. Proof before approval. Thank you." The close matters more than the roadmap.

---

## 2 · The hard words, and how to say them

Only four words in your whole slot are difficult. Practise these five times each.

| word | say it like | what it is |
|---|---|---|
| **Pramaan** | pruh-MAAN | our project name. Hindi for proof |
| **ElevenLabs** | eh-LEV-en labs | the best-known paid voice cloning company |
| **PlayHT** | play-H-T | another one. Just say the letters |
| **contact centre** | | the room where bank agents take customer calls |

**Words you do NOT have to say:** Interspeech, ICASSP, NeurIPS, AudioMarkBench, AUDETER, isotonic, self-supervised. All of those are printed on the slide. Point, do not pronounce.

---

## 3 · What is on the slide, in case you are asked

You do not read this out. But if a judge points at a line and asks, here is a one-line answer for each.

| what is on the slide | if asked, say |
|---|---|
| Pascu, 2024 | "It showed that freezing a big speech model and training a tiny classifier on top works better than retraining the whole thing." |
| Müller, 2022 | "It showed that detectors which look perfect in the lab fall apart on real-world audio. That is why we do not quote a lab number." |
| AUDETER, 2025 | "It showed that using many different fake-voice tools in training is what makes a detector generalise. On Indian languages we measured what variety actually buys, and what it buys is **consistency, not a lower average.** With one tool the result depends on which tool you happened to pick: anywhere from {{div_k1_min}} to {{div_k1_max}}. With all {{n_seen}} it is {{div_k6}} every time. The average does not fall. The luck goes out of it." |
| the 2026 first-greeting paper | "It is about deciding from very short audio, and the tricks that make short-clip results look better than they are. We designed against that." |
| Semjonovs, 2026 | "Deciding during a call instead of after it. That is prior work and we say so." |
| Zadrozny, 2002 | "The maths that turns a raw score into an honest probability." |
| PITCH, 2025 | "A study where asking the caller a surprise question raised detection from 56 to 88 percent. **Their number, on their data.** Never ours." |
| AudioMarkBench, 2024, and the 2026 follow-ups | "It showed audio watermarks can be stripped off, and the 2026 work is worse for watermarks, not better: one paper shows a watermark can be **stamped onto a genuine recording**, so forgery is as real as removal. Our rule covers both directions. A watermark in our system can only ever **lower** risk, never raise it. Strip one off and the caller loses a discount, which is the safe direction. Forge one on and the best it buys an attacker is a lower score on a call that still cannot move money without the registered device. The rule is an `assert` in `src/pramaan/warrant.py`, not a sentence on a slide." |
| CNAP under TRAI | "That is India's own caller-trust rule, not the American one. CNAP verifies **the line**. Pramaan verifies **the voice on it**. Two different layers, and they work together: a verified caller name does not tell you the voice is not a clone." |

---

## 4 · What is actually ours, if someone pushes

**The diversity curve, all {{n_seen}} numbers, in case a judge asks to see it.** Mean equal error
rate on the held-out 2025 cloner, over {{n_div_subsets}} random subsets of generator families
at each k (`eval/results.json`, `diversity_curve`):

| families in training (k) | mean EER | best subset | worst subset | spread |
|---|---|---|---|---|
{{div_table_rows}}

**Read that column, not the mean column.** The mean does not fall. It goes
{{div_mean_seq}}. What collapses is the spread,
from {{div_k1_span}} at k=1 to {{div_kN_span}} at k={{n_seen}}. So the claim is **variance
reduction, and we do not claim more than that**: with few generators the outcome is a
lottery, with all {{n_seen}} it is the same answer whichever way you slice the training set.
**And say the caveat before a judge finds it.** At k={{n_seen}} the spread is
{{div_kN_span}} for a trivial reason: there is only one way to choose all {{n_seen}} of
{{n_seen}}, so all {{n_div_subsets}} subsets at that k are the same subset. The row that
carries the real evidence is k=2, where the spread is {{div_k2_span}}, against
{{div_k4_span}} at k=4 and {{div_k5_span}} at k=5. The trend is real and the last row
overstates it. Say so.

Getting the mean to move would need more than {{n_seen}} families, or more than
{{n_div_subsets}} subsets per k, and that is a named roadmap item and not a result we have.
Saying this precisely is stronger than saying we reproduced someone's scaling law, because
this version is exactly what our own JSON shows and a judge can check it.



Say it calmly, in four short points:

1. "We built {{n_seen}} different fake-voice generators ourselves, and measured exactly what that variety buys. It is not a lower average error. It is a smaller spread: with one generator the result swings between {{div_k1_min}} and {{div_k1_max}} depending on which one you happened to have, and with all {{n_seen}} it lands on {{div_k6}} every time. We say variance reduction, not improvement, because that is what our own curve shows."
2. "Our hardest test clones the exact recording it is compared against. Same speaker, same sentence."
3. "We publish a table of where we fail, across languages, tools and phone lines. Nobody else has published one."
4. "And we put all of it into one system that runs offline on a laptop."

---

## 4b · If a judge asks what the Warrant actually is

Answer in three sentences and do not oversell it.

> "A legitimate bank IVR is synthetic on purpose. So for a high-value action the question is not 'is this a machine', it is 'is this an **authorised** machine', and that is a different question our detector cannot answer. Our Warrant answers it from a signed token on the channel, and it is built so that it can only ever lower risk, never raise it, which is an `assert` in the code."

**What it is not, and say this if pushed:** it does **not** embed or detect an audio watermark. Recovering a watermark from the signal needs a separate neural model and a new dependency in a pinned environment, and we did not add one days before a demo. The token path is what runs. **Do not say we detect watermarks.**

**Why the rule has that sign, if they push further:** every audio provenance signal published so far is forgeable in both directions. If a forged warrant could **raise** risk, an attacker could stamp a fake one onto a genuine customer and get them blocked, which hands the attacker a weapon. Because it can only lower risk, forging one costs nothing and gains nothing, and the device factor is untouched either way.

---

## 5 · The licence question

Someone may ask if this can be sold tomorrow. Short answer:

> "Not with this training data. Two of our sources are free for research only. A commercial version would retrain on licensed data. That is a known step on our roadmap, and we would rather tell you than hide it."

Full forms if you need them: **CC-BY** means free to use if you give credit. **NC** means non-commercial, so research only.

---

## 6 · Questions you may get

**"What is new here?"**
> "Three things. We built {{n_seen}} fake-voice generators ourselves and measured what that variety buys, which is consistency rather than a lower average: {{div_k1_min}} to {{div_k1_max}} with one generator depending on which, {{div_k6}} every time with all {{n_seen}}. Our hardest test clones the exact recording it is compared against. And we publish where we fail, which nobody else does. The streaming part and the authorisation idea are other people's work, and they are on this slide."

**"What would you do in three months?"**
> "Clips from the paid cloning tools, a hard test in Tamil and Telugu, the two phone codecs we could not build, and one bank contact centre running live."

**"Why should we pick you?"**
> "Because you can check everything we said. One command re-runs every number. The slides are made from that file. And our table shows the places we fail. If we are wrong, you will find it."

**"So it is not finished?"**
> "The system is finished. It runs end to end, offline, and you saw it. What is small is the training data, and we measured exactly how much more data is worth. That is a system that needs feeding, not redesigning."

---

## 7 · How to close

The last ten seconds matter more than the last minute.

- **Stop walking. Put your hands down.**
- **Look at the judges, not the screen.**
- Say it slowly, with a real pause in the middle:

> "Pramaan. *(pause)* Proof before approval. *(pause)* Thank you."

- Then **stand still and say nothing.** Let them speak first.

**Do not say:** "that's all from our side", "any questions?", "sorry we went over", "yeah so". End on the name.

---

## 8 · What not to say

- **Do not read the paper names aloud.** Point at the slide.
- **Never say another team's number is ours.** The 56 to 88 percent is PITCH's result on PITCH's data.
- **Do not say "we ran out of time".** Say what we built, and what we would build next.
- **Do not promise we will beat the best products.** Say we will publish the comparison. That is a promise we can keep.
- If you are at 9:40, skip straight to the roadmap and the close.
