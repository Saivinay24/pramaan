# Demo video kit

Everything needed to finish the SIH 2026 national-round demo video. The cut is assembled and timed.
The only thing missing is the six narration recordings.

**Current state:** `video/out/pramaan_demo.mp4`, 527.04 s (8:47), 1920x1080, 30 fps, silent.
That matches `docs/VIDEO_SCRIPT.md` exactly, with 1:13 of headroom under the 10:00 limit.

**There are no presentation slides in this video.** Every visual is the running operator console,
apart from beat 1 (cold open) and beat 18 (closing title card). The deck is a separate submission
artifact and does not appear here. A demo video demonstrates the product.

## Finish it in one command

1. Each speaker records their section from `docs/VIDEO_SCRIPT.md`, following the recording protocol
   in that file.
2. Drop the files in as `docs/vo/S1.wav` through `docs/vo/S6.wav`.
3. Run:

```bash
cd ~/Desktop/hackathons/2026-sih-26104-kempelen/pramaan
python3 video/build.py
```

Partial recordings are fine. A speaker with no file keeps their planned timing and runs silent, so
the cut stays assemblable at every stage.

## How the timing works

Each speaker owns a contiguous run of beats. When their recording exists, only their own beats are
rescaled, by `actual_length / planned_length`. A speaker who reads slowly stretches their own
visuals and nobody else's, so one slow reader cannot push the whole video over the limit. Check the
printed total after every build.

## The cut

Eighteen beats. `clip` is motion from a capture; `panel` is a high-DPI still of one console panel,
held with a slow push.

| Beat | Spk | Planned | Visual | Source |
|---|---|---|---|---|
| 1 | S1 | 14 s | Cold open, one whole Hindi sentence, real then clone | built by `video/coldopen.py` from `data/samples` |
| 2 | S1 | 35 s | Console at rest, cycling all ten lines, each naming its true recording origin | `atrest_master` marks `start`..`end` |
| 3 | S1 | 27 s | Prevention ladder, five rungs | panel `ladder` |
| 4 | S2 | 36 s | About panel, Detector and Gate | panel `about` |
| 5 | S2 | 22 s | Risk trace, carrier swept, uncertainty band visibly moves | marks `C0 carrier sweep begin`..`A1 audit tab` |
| 6 | S2 | 51 s | Diversity curve, min-to-max band collapsing | panel `diversity` |
| 7 | S3 | 33 s | Live call, genuine Hindi caller, Opus 24 kbps | marks `L1 genuine hindi opus24 :: start`..`:: end` |
| 8 | S3 | 23 s | Known XTTS-v2 clone, blocked | marks `L2 clone xtts seen :: start`..`:: end` |
| 9 | S3 | 60 s | Pair A then Pair B, challenge, device push, blocked, uncut | marks `L3 pairA real :: start`..`L4 pairB clone 2025 :: end` |
| 10 | S3 | 28 s | Audit chain verified, altered, broken, restored | marks `A1 audit tab`..`A5 restore` |
| 11 | S4 | 40 s | Held-out generator heat map | panel `heatmap` |
| 12 | S4 | 7 s | Calibration error, raw, Platt, isotonic | panel `calibration` |
| 13 | S4 | 27 s | Heat map again, the known limits | panel `heatmap` |
| 14 | S5 | 37 s | Scoring cost on this laptop, real-time factor 0.046 | panel `scoringcost` |
| 15 | S5 | 33 s | Cost of adapting to a new cloner | panel `adaptcost` |
| 16 | S6 | 19 s | About panel, Measurements and Network, external requests "none" | panel `about` |
| 17 | S6 | 25 s | Evidence tab, slow scroll across all six panels | marks `E1 evidence tab`..`B1 about open` |
| 18 | S6 | 10 s | Title card | generated |

Beats 7 to 10 are 2:24 of continuous demo. Per the script's direction notes, do not cut inside a
demo beat, and put no music under them.

## How the footage was captured

Recorded by driving the live console at `http://127.0.0.1:8770` in headless Chrome over the Chrome
DevTools Protocol, at exactly 1920x1080, light theme pinned and asserted at every step. Nothing is
staged or mocked: every score, verdict, ledger hash and challenge phrase came from the running
server. `console_master.mp4` is a single 494 s take covering live calls, a carrier sweep, the audit
chain and the Evidence tab.

Four capture notes worth keeping, because each one cost time:

- The CDP screencast writes a WebM that **declares 25 fps while actually capturing about 29.7 fps**,
  so the raw file plays roughly 1.19x too slow and every seek lands early. Every master is rescaled
  with `setpts` against measured wall-clock before use. If you re-capture, redo that correction or
  every timecode above will be wrong.
- Concatenating segments with `-c copy` mangles timestamps across differing timebases and turned
  8:42 of correct parts into a 26 minute file. `build.py` re-encodes on concat instead.
- A fresh Chrome profile inherits `prefers-color-scheme: dark`. The theme is pinned through
  `localStorage` before first paint and asserted after every step, so no dark frame can enter.
- **Beats address capture marks by name, not raw seconds.** An earlier version hardcoded
  timecodes, so re-capturing silently shifted every beat. `build.py` now resolves each clip from
  the capture's `.marks.json`, and fails loudly if a mark is missing.
- **The cold open uses one whole sentence.** Both pair clips fall silent at 4.00 s, so 0 to 4.0 is
  a complete utterance in each. An earlier 7 s cut landed inside the second utterance and sounded
  like spliced fragments. `video/coldopen.py` derives the clips at build time and draws the
  waveform across the full content width with a playhead.
- Panel close-ups are **not** crops of the 1080p video, which would be a 4x upscale and look soft.
  They are element screenshots taken at `deviceScaleFactor: 2` and fitted onto the console
  background, so the text stays crisp.

## Known gaps

- **Beat 7 calls for the Wi-Fi menu being switched off on camera.** That is a macOS menu bar shot
  headless capture cannot produce. Either film it on the presenting laptop and drop it in ahead of
  beat 7, or let the console's own "Audio stays on this machine" indicator carry the claim. The
  current cut uses the console indicator.
- **`ffmpeg` here has no `libfreetype`**, so `drawtext` is unavailable. Text cards are rendered to
  PNG with PIL and composited. Do not add a `drawtext` filter; it will fail.
- The **Podonos cross-vendor latency comparison has no console view.** Beat 14 shows the measured
  real-time factor on this laptop while the speaker names the benchmark and its date aloud.
- Check the portal's file size cap and re-encode at a higher CRF if needed.

## Outputs

| File | What it is |
|---|---|
| `video/out/pramaan_demo.mp4` | Working master, CRF 18 |
| `video/out/pramaan_demo_delivery.mp4` | Delivery encode, CRF 21, faststart |
| `video/source/console_master.mp4` | Main console capture, 494.63 s |
| `video/source/atrest_master.mp4` | Console at rest, cycling lines, 48.10 s |
| `video/source/panels/*.png` | Nine high-DPI console panel stills |
| `video/source/*.marks.json` | Wall-clock marks for every action in the captures |
