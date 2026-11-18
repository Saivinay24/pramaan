# Run sheet for Saturday 5 September 2026

**Slot 11:18 to 11:30. Ten minutes to present, two for questions. Team Davinciable. Six speakers.**

## Which file is yours

Each speaker has one file with everything they need: their words, their background, every full form, their numbers, and the questions they will get.

| you are | read | also read |
|---|---|---|
| S1, the problem | `docs/SPEAKER_S1.md` | `docs/TEAM_GUIDE.md` part 1 |
| S2, what we built | `docs/SPEAKER_S2.md` | `docs/TEAM_GUIDE.md` part 2 |
| S3, the demo | `docs/SPEAKER_S3.md` | this run sheet |
| S4, the evidence | `docs/SPEAKER_S4.md` | `docs/QA_PREP.md` |
| S5, impact and business | `docs/SPEAKER_S5.md` | `docs/QA_PREP.md` |
| S6, research and close | `docs/SPEAKER_S6.md` | `docs/QA_PREP.md` |
| everyone | `docs/TEAM_GUIDE.md` | `docs/NUMBERS.json` for the allowed numbers |

## Tonight, before sleeping

1. Assign the six slots in `docs/PRESENTATION_SCRIPT.md`. S3 is whoever has run the demo end to end at least twice. S4 is whoever stays calmest when challenged.
2. Everyone reads their slot and `docs/QA_PREP.md`. Nobody memorises a number that is not in `docs/NUMBERS.json`.
3. One full timed run, ten minutes. Then a hostile round: two people ask the worst five questions from QA_PREP at random.

## Morning, on the presenting laptop

```bash
cd ~/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
scripts/demo.sh            # console on http://127.0.0.1:8770, offline
```

- [ ] **Wi-Fi off** before the server starts. The console must work with it off; it loads no CDN and no model from the network.
- [ ] Browser: Chrome, full screen, `http://127.0.0.1:8770`, zoom 110% for the projector.
- [ ] Mains power, notifications off, volume up, screen mirroring tested in the room if possible.
- [ ] Run the four demo beats once in the room: `human_hindi`, `clone_xtts_v2`, `pair_real_hindi`, `pair_clone_hindi`, then the ledger tamper.
- [ ] Deck open in Keynote or PowerPoint: `ppt/Pramaan_SIH2026_Idea.pptx`. Six slides. Check every number matches `docs/NUMBERS.json`.
- [ ] Phone with `docs/PRESENTATION_SCRIPT.md` open for each speaker, as a safety net, not a script to read.

## The demo beats, in order

| Beat | Source | Channel | What to say |
|---|---|---|---|
| 1 | Genuine caller, Hindi | Opus 24k | Real recording, VoIP codec, no decision before {{min_commit}} s, then genuine; transfer still held. |
| 2 | Clone, XTTS-v2 | Opus 24k | Seen family: synthetic at {{min_commit}} s, blocked. {{lat_cpu4}} ms per update on CPU. |
| 3 | Pair A then Pair B | clean | Same person, same sentence, 2025 cloner never seen. Challenge, push, "Not me", blocked. |
| 4 | Audit ledger tab | | Tamper with block 2, verify, broken. |

If the microphone is requested by a judge: source "Laptop microphone", speak Hindi or English, or play the ElevenLabs clone from a phone held near the laptop (tested: synthetic at 1.5 s). Say that it is live. The Chatterbox clone through the mic reads as human; that is the beat where the device push does the blocking.

## If something breaks

Say what broke in one sentence, switch to the next sample, keep presenting. S3 owns the laptop; nobody else touches it. A team that recovers calmly reads as a team that has shipped before.

## Rules for the room

- Every number comes from `docs/NUMBERS.json`. If it is not there, "I would have to check that."
- Never say "unfortunately" or "we did not have time". State the limit, then the design that handles it.
- One speaker per slot. In Q&A the owner of the topic answers, alone.
- No em dashes anywhere a judge reads. The deck and docs are generated without them.
