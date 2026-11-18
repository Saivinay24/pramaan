# S2 · What we built, and what is new

**You speak second. 1:20 to 3:00. Slides 2 and 3.**

Your job: explain the system clearly enough that a non-technical judge follows it, and precisely enough that a technical judge respects it. You own every architecture and model question in the Q&A.

This is the longest study file. Read it twice.

---

## 1 · What you say, word for word

> "Pramaan has four layers, and I will name the one decision in each that matters.
>
> **Layer one, the Listener.** A frozen multilingual speech model turns the audio into numbers, and a very small classifier we trained reads those numbers and says how machine-made this voice sounds. It gives a fresh answer every half second.
>
> **Layer two, the Gate.** This decides *when* to decide. It only commits to an answer if it has heard at least 1.5 seconds of real audio, the probability is clearly at one end, and it has stayed there for three updates in a row. Otherwise it says 'not yet', and 'not yet' is not a shrug, it triggers the next layer.
>
> **Layer three, the prevention ladder.** This is the half of the title most teams drop. The caller is asked to repeat a random phrase in their own language, drawn from a hundred and sixty thousand possibilities, so a recording cannot answer it. And for a large transfer the final step is never the voice: a notification goes to the real person's registered phone. No tap there, no money.
>
> **Layer four, the ledger.** Every score, decision, challenge and approval becomes a block, fingerprinted together with the previous block. Edit any past entry and every later fingerprint breaks. That is the blockchain half of this theme, done as a tamper-evident record rather than a token.
>
> *(move to slide 3)*
>
> Now what is genuinely new, and it is not the algorithm.
>
> **A detector only catches the kinds of fake it has already heard.** Show it one cloning tool and a different tool walks straight past. So instead of downloading one dataset, we built **8 different families of fake speech ourselves on this laptop**, and then tested against one more cloning tool, released this year, that the system had never heard.
>
> The result: with only one or two families, the outcome is a lottery depending on which you happen to have. The error went as high as 39.6%. With all 8, it is 13.2%, every time. **Diversity does not buy you a lucky number, it removes the unlucky one.**
>
> Second, our hardest test is same speaker, same sentence: the unseen cloner clones the exact recording it is compared against, so it cannot be caught out by the words or the recording quality.
>
> Third, and this is the design decision that matters most: **detection is a router, not a judge.** The score decides whether to challenge. The challenge decides whether to escalate. The real person's phone decides whether money moves."

**Hand over:** "S3 will show you all four layers running live."

---

## 2 · The two brains, in depth

A judge will ask "what model are you using?". This is the answer.

### Brain 1 · the borrowed model that listens

**XLS-R** (cross-lingual speech representations), released free by Meta. The exact name is `facebook/wav2vec2-xls-r-300m`.

| fact | value |
|---|---|
| numbers inside it | about 315 million |
| size on disk | 2.4 GB |
| what it was trained on | 436,000 hours of speech in 128 languages |
| trained by | Meta, not us |
| does it learn from us | **no, we freeze it** |
| licence | Apache 2.0, free for commercial use |

Its job is to turn a piece of audio into numbers that describe **how the sound was physically produced**, not what was said.

Concretely, for a 4-second clip:

```
  64,000 audio samples          (4 seconds at 16,000 samples per second)
        │
        ▼
  199 frames x 1024 numbers     (one frame every 20 milliseconds)
```

Two choices inside it, both with reasons:

1. **We read stage 5 out of 25.** The model processes audio in 25 stages. Early stages still hold the physical detail of how the sound was made: texture, breath, micro-timing. The last stages have discarded that and kept only the meaning of the words, which is useless for spotting a fake. So we tap it early-middle.
2. **We summarise the 199 frames two ways**: the *average* of each column (the typical texture) and the *spread* of each column (how much it varies, and humans vary more). That gives **2048 numbers describing the whole clip**, regardless of how long the call is.

**If asked "what are the features?"**, answer in two parts.

Part one, the honest bit:
> "They are learned, not designed. Nobody can point at column 37 and say 'that is pitch'. The model invented those 1024 measurements for itself while learning 128 languages. We never chose them, and that is exactly why the method carries over to languages and cloning tools we did not plan for."

Part two, and this is what separates us from a team that just says "it's a black box". **We ran a probe.** We measured ordinary, nameable properties of 300 real and fake clips, and checked which ones line up with the classifier's score. Five things came out, and all five make physical sense:

| what we measured | in fake voices | how strong |
|---|---|---|
| **spectral flux**, how fast the sound changes from moment to moment | **much higher** | by far the strongest signal |
| **shimmer**, tiny wobble in loudness between one moment and the next | higher | clear |
| **silence**, real pauses and breaths between words | **less of it** | clear |
| **pitch variation**, how much the voice moves up and down | **less of it** | clear |
| **high-frequency energy** above 5 and 7 kHz | **less of it** | present, and it is what a phone line destroys |

Say it like this:
> "We probed it, and what it responds to makes physical sense. Synthetic speech changes too abruptly frame to frame, its pitch is flatter than a real person's, it has less of the breath and silence that real speaking leaves behind, and it is missing energy at the top of the spectrum, which is the part a vocoder smooths away. About 55% of the decision weight sits on the average texture of the voice, and 45% on how much it varies over time. Both halves matter, which is why we keep both."

That probe is `eval/what_it_hears.py` and its output is saved in `eval/results/what_it_hears.json`.

### Brain 2 · our classifier, the only thing we trained

On top of those 2048 numbers sits our own classifier: **2,049 numbers.** One weight for each feature, plus one bias. The file is 61 KB, next to a 2.4 GB frozen model.

It does two things:

1. **Scales** each of the 2048 features against the average and spread seen across training, so "unusual" means the same thing on every feature.
2. **Multiplies each by its weight and adds them up.** It is a tug of war. On a real clone we measured: evidence for synthetic +30.4, evidence for human -22.3, net **+12.2**, so the synthetic side wins. No single feature decides anything.

**Why so small? This is the question, and here is the answer:**
> "We have about 2,500 training clips. A large model with that little data simply memorises the specific cloning tools we showed it and then fails completely on the next tool released. Freezing the big model and training a tiny head on top generalises better. That is a published result, Interspeech 2024, not our preference. And it means training takes seconds on a laptop CPU, which is what makes retraining against every new cloner a practical business rather than a promise."

### Brain 3 · the calibrator

The classifier outputs a raw score like +12.2. That means nothing to an operator. The **calibrator** is a lookup table built on held-out clips: for each score, what fraction really were synthetic. So 0.8 genuinely means 80%.

There are **eight** of them, one for each audio length from 0.5 to 4 seconds, because a score from 1.5 seconds and a score from 4 seconds are not the same kind of evidence.

Without this, the problem statement's phrase "actionable risk score" would be a lie.

### The whole path, one diagram

```
  64,000 audio samples
     │  frozen XLS-R, 315 million numbers, unchanged
     ▼
  199 frames x 1024 features
     │  average and spread of each column
     ▼
  2048 numbers
     │  our 2,049-number classifier
     ▼
  one raw score           clone: +12.2      human: -8.6
     │  calibrator lookup table
     ▼
  one probability         clone: 0.99       human: 0.01
     │  the Gate
     ▼
  SYNTHETIC / HUMAN / DEFER
```

You can run this yourself and see every number: `scripts/explain.sh data/samples/clone_xtts_v2.wav --compare data/samples/human_hindi.wav`. The saved output is in `docs/WALKTHROUGH_EXAMPLE.txt`.

---

## 3 · The rest of the stack

| part | what it is | why |
|---|---|---|
| **Python and PyTorch** | the programming language and the library for running AI models | standard, free |
| **FastAPI and WebSocket** | the web server, and the connection type that streams audio continuously instead of one request at a time | a call is a stream, not a file |
| **the console** | plain HTML, CSS and JavaScript, no external libraries | it must work with the Wi-Fi off |
| **ffmpeg** | free audio conversion tool | applies the telephone codecs |
| **SHA-256** | secure hash algorithm, 256 bits: a function that turns any data into a fixed fingerprint | one changed character changes the whole fingerprint, which is what makes the ledger tamper-evident |
| **MPS / CPU** | Metal Performance Shaders, the Mac's graphics chip / the ordinary processor | works on both; we quote the CPU number because it is the honest deployment case |

---

## 4 · Full forms and terms you must know

| term | full form | plain meaning |
|---|---|---|
| **XLS-R** | cross-lingual speech representations | Meta's multilingual speech model, our "ears" |
| **wav2vec2** | | the family of models XLS-R belongs to |
| **frozen** | | we never change the model's numbers; we only use its output |
| **classifier** | | the part that draws the line between two answers |
| **feature** | | one measured number describing the audio |
| **parameter** | | one adjustable number inside a model |
| **calibration** | | making a score mean a real probability |
| **inference** | | running a trained model on new data |
| **TTS** | text to speech | software that reads text aloud in a synthetic voice |
| **VC** | voice conversion | software that reshapes one person's recorded voice into another's |
| **codec** | coder-decoder | compression used to squeeze voice down a phone line |
| **VoIP** | voice over internet protocol | phone calls carried over the internet, like WhatsApp calls |
| **SSL** | self-supervised learning | training a model on unlabelled audio by making it predict hidden parts of it; how XLS-R was built |
| **hash** | | a fixed-length fingerprint of some data |
| **FIDO2** | fast identity online, version 2 | the standard behind phone and fingerprint logins |
| **API / SDK** | application programming interface / software development kit | the connection point another system plugs into, and the package we would ship |

---

## 5 · The numbers you own

| number | value | when to use it |
|---|---|---|
| model size, frozen | 315 million numbers, 2.4 GB | "what model do you use?" |
| languages it already knows | 128, trained on 436,000 hours | why it works for Indian languages |
| what we trained | **2,049 numbers** | the headline of your slot |
| features per clip | 2048, from 199 frames | if they push on architecture |
| generator families we built | **8** | the "what is new" line |
| diversity result | 39.6% worst case with few, 13.2% with all 8 | the "what is new" line |
| challenge phrases possible | 160,000 | the ladder. Arithmetic, not a claim: 10,000 four-digit strings x 16 lexicon words x 1 task template, straight out of `src/pramaan/challenge.py` |

Everything about held-out accuracy belongs to **S4**. Everything about speed and cost belongs to **S5**.

---

## 6 · Questions you will get

**"Why not fine-tune the big model?"**
> "Because with 2,500 clips fine-tuning memorises the six cloners we showed it and fails on the seventh. Frozen plus a small head generalises better; that is Pascu and colleagues, Interspeech 2024. It also removes the GPU from the critical path entirely."

**"Why layer 5? Why not the last layer?"**
> "The last layers describe what was said. We need how it was made. The early-middle layers still hold the physical texture, and that is what a synthesiser gets subtly wrong."

**"2,000 parameters sounds too simple to work."**
> "The 315 million parameters doing the hard work are still there, they are just borrowed and frozen. Our part only has to draw a boundary in the space they produce. And the measured result is on slide 4, including the cases where it fails."

**"Is this a transformer? What architecture?"**
> "XLS-R is a transformer with a convolutional front end, trained self-supervised. Our head is logistic regression, which is the simplest linear classifier there is. We tried a neural network and a support vector machine and compared them properly; the simple one generalised best to the unseen cloner, and that comparison is in the repository."

**"Where is the blockchain? This looks like just a log file."**
> "It is a hash chain. Each block carries a SHA-256 fingerprint computed over its own contents plus the previous block's fingerprint. Change one past score and every later fingerprint stops matching, which S3 demonstrates live. It is append-only and verifiable, and the final fingerprint can be anchored to a bank's own chain. We did not build a token because a token would not make a decision more auditable."

**"Does it work in real time?"**
> "Yes, and S5 has the exact numbers. Short version: 185 milliseconds per update on a laptop CPU with no GPU."

---

## 7 · What not to say

- **Never say we built or trained XLS-R.** We borrowed it. Saying otherwise is checkable in one search and would cost us the credibility mark.
- **Never say "our own AI model"** about the big model. Say "a frozen open-source model from Meta, with our own classifier on top".
- **Do not claim the streaming idea or the authorisation idea is ours.** Both are published prior work, we cite them on slide 6, and S6 names them. Our contribution is the generator diversity, the Indian-language evaluation and the integrated system.
- Do not go past 3:00. If you are late, cut the stack table and keep the four layers and the diversity finding.
