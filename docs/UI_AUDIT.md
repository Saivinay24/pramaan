# Operator console: audit and rebuild

Audit run 18 September 2026 against the live server on `http://127.0.0.1:8770`, Chrome,
1920x1080. Every defect below was reproduced in the browser, not read off the source.

Status key: **fixed** in the rebuilt console, **kept** deliberately, **open** still outstanding.

## A. Defects that broke a demo beat

| # | Defect | Evidence | Status |
|---|---|---|---|
| A1 | **The Evidence tab rendered nothing at all.** `loadEvidence()` threw `TypeError: Cannot read properties of undefined (reading 'streams_per_core')` on `lat.capacity?.cpu_hop_1.streams_per_core`. The real key in `eval/results/latency.json` is `cpu_hop_1.0`, not `cpu_hop_1`. The optional chain stopped one level too early, the exception escaped an `async` handler as an unhandled rejection, and the tab sat on "Loading results…" forever. Every evidence table, the heat map and the diversity curve were dead. | console: `REJ TypeError ... streams_per_core`; `#ev` innerText was 16 characters | fixed |
| A2 | **The challenge line printed "1 of 0".** The console reads `c.space` from the server and falls back to `0`, so a server that does not send the field advertises a challenge space of zero, on screen, in front of judges. Root cause on the day: the running server was started 10 Sep and `src/pramaan/challenge.py` gained the `space` field on 14 Sep, so the live process was serving stale code. | `challenge f6b971a2a5 · 1 of 0`; API response had no `space` key; `ps` start time 10 Sep vs file mtime 14 Sep | fixed (no invented fallback: the field is omitted when the server does not send it) |
| A3 | **Microphone denial left the console frozen mid-call.** `startMic()` is awaited inside `ws.onopen`; a `NotAllowedError` from `getUserMedia` becomes an unhandled rejection, the socket stays open, Start stays disabled and the screen sits on "Collecting the first 1.5 s of audio" forever. No message reaches the operator. | forced `getUserMedia` rejection: two unhandled rejections, `start.disabled === true`, `ws.readyState === 1` | fixed |
| A4 | **Start is silently ignored while a call is running.** The button is disabled but nothing says why, and the source and channel selectors keep accepting changes. Pressing Start after switching source looks like a dead button. | clicked Start during an in-flight call: no new socket, no feedback | fixed |

## B. State and lifecycle

| # | Defect | Evidence | Status |
|---|---|---|---|
| B1 | **The "true origin" caption updates on source change while a different call is on screen.** Switching the dropdown mid-call relabels the running call with the newly selected clip's provenance. On a stage this is the one caption that must never lie. | selected `pair_real_hindi` during an XTTS call: caption read "real human speech" while the screen showed the synthetic verdict | fixed |
| B2 | **The call never visibly ends.** On the `end` message the console appends " · call ended, ledger saved." to the reason string and re-enables Start, but leaves End call enabled, the socket open and the header still reading as a live call. | after the sample finished: `start.disabled false`, `stop.disabled false`, `ws.readyState 1` | fixed |
| B3 | **Stale socket race.** Starting a second call without ending the first overwrites `ws`; the old socket's `onclose` later fires and calls `stopMic()` and re-enables buttons, which can kill the microphone of the call that is actually running. | code path reachable whenever `end` arrives before the operator presses End | fixed |
| B4 | **A challenge issued after the audio ends never resolves.** `answer_challenge` only runs on a new audio chunk, so a manually issued challenge on a finished call stays "awaiting" with no deadline shown and no timeout in the UI. | beat 3: `L2s` stuck on "awaiting" indefinitely | fixed (the challenge card now shows the deadline and marks it as expired when the deadline passes) |
| B5 | **Channel selector can be changed mid-call with no effect**, and the call card keeps showing the channel the call actually started on only because `resetUI` snapshots it. The mismatch between the control and the running call is invisible. | changed channel mid-call | fixed |

## C. Numbers and empty states

| # | Defect | Evidence | Status |
|---|---|---|---|
| C1 | `(c.space \|\| 0).toLocaleString()` prints a hard zero rather than an empty state. Same pattern in the latency badge, which prints `– ms` but re-renders on every update. | see A2 | fixed |
| C2 | **The ledger picker only ever lists the call in memory.** `runs/` holds 40 saved calls and the server has no endpoint to enumerate them, so a compliance officer cannot open yesterday's call. The picker shows one option. | `#lg-run` options: one entry | fixed (new `GET /api/runs`, picker lists saved calls newest first) |
| C3 | **The ledger table dumps raw JSON.** `JSON.stringify(b.data).slice(0,160)` truncates mid-token, has no actor column, and the hash columns are cut to 14 characters with no way to see the full value. | ledger view | fixed |
| C4 | **Tampering is irreversible in the view.** After "Tamper with block 2" there is no way back to the true chain short of re-running the call, because the picker's `change` event does not fire on the same value. | ledger view | fixed (Restore button) |

## D. Visualisation

| # | Defect | Evidence | Status |
|---|---|---|---|
| D1 | **The risk meter is unreadable at the shipped operating point.** The commit band on a clean line is `[0.010, 0.014]`, so the striped "undecidable band" is 0.4% of a linear 0 to 1 meter, invisible, while the label spans the whole width and implies the band sits in the middle. On `opus_8k` it is 55% wide. The same linear scale flattens every genuine trace onto the x axis. | measured `#band` width: 0.39% on clean, 55.75% on opus_8k | fixed (the meter and the trace are drawn on a symmetric log-odds axis, with the measured band drawn where it actually is) |
| D2 | The score trace has no legend, no units on the y axis beyond 0/0.5/1, and event dots are drawn in the verdict colour with no key. | live view | fixed |
| D3 | The live waveform panel is blank whenever sample playback is blocked by autoplay policy, and it is fed by `player.currentTime` rather than by the audio the server actually scored. | `player.currentTime === 0`, empty canvas | fixed (the trace panel no longer depends on playback; the waveform is drawn only for the microphone source, where it is real) |
| D4 | The evidence heat map used a hand-rolled green-to-red ramp with no accessible contrast and no tabular alignment. | evidence view | fixed |

## E. Product framing (the substance of the rebuild)

| # | Defect | Status |
|---|---|---|
| E1 | **The top bar advertised the model.** A badge read "XLS-R 300M frozen · head calibrated". No production fraud console names its model to an operator. | fixed: moved to an About and diagnostics panel |
| E2 | **The ladder explained its own methodology in the primary surface.** "Frozen multilingual speech model + calibrated head, every 0.5 s" is documentation, not an operator instruction. | fixed: the ladder now states what the operator must DO and what the result was; the method text lives under About |
| E3 | **The audit ledger was staged as a concept demo.** A button labelled "Tamper with block 2 (demo)" sat in the primary toolbar. | fixed: rebuilt as a chronological event log with time, actor, event, hash prefix and chain status per block, a verify action that reports pass or fail, and an export. The integrity check is the product; tamper and restore are a clearly separated integrity test inside it |
| E4 | **No decision surface.** The screen answered "how does this work" before "what do I do now". | fixed: a decision bar carries the caller, the claimed identity, the requested action, its value, the verdict and the recommended next step, above everything else |
| E5 | **Evidence, calibration bands, generator families and per-channel numbers sat at the same level as the live call.** | fixed: demoted to a secondary Evidence view; the live view carries only what an operator acts on |
| E6 | **Light mode only.** No dark tokens, no `prefers-color-scheme`. A projector in a dark room is the presenting condition. | fixed: tokens on `:root`, a dark override, and a manual toggle |

## F. Accessibility and presentation conditions

| # | Defect | Status |
|---|---|---|
| F1 | Tabs were `<button>` elements with no `role="tab"`, no `aria-selected`, no keyboard arrow navigation. | fixed |
| F2 | Verdict was carried by colour alone (green/amber/red pills). | fixed: every verdict carries a text label and a shape, not only a hue |
| F3 | Live score updates were not announced; no `aria-live` region anywhere. | fixed: the verdict line is an `aria-live="polite"` region |
| F4 | The toast was `display:none` toggled with no `role="status"`, so failures were invisible to assistive tech and easy to miss on a projector. | fixed |
| F5 | `max-width:1500px` centred the grid inside 1920 with dead margins, and at 110% zoom the three-column grid crowded. | fixed: fluid grid, no fixed max width, verified at 1920x1080 and at 110% zoom |
| F6 | No focus-visible styling on any control. | fixed |

## G. Offline constraint

Verified by grepping every URL in the rebuilt `index.html`: the only non-relative reference is an
inline `data:image/svg+xml` URI for the select chevron. No CDN, no webfont, no `<link rel>` to an
external origin, no `fetch` to anything but `/api/*` and the two websocket endpoints on
`location.host`. System font stacks only. Confirmed **fixed** and **kept fixed**.

## H. Left alone deliberately

- **The server's scoring, gate, ledger, challenge and warrant logic.** Untouched. The rebuild is a
  console, not a change of model behaviour, and the numbers on screen must keep tracing to the same
  code that produced `eval/results.json`.
- **`ScriptProcessorNode` for the microphone.** Deprecated in favour of `AudioWorklet`, but an
  `AudioWorklet` needs a separate module file served over HTTP and the current path is measured and
  working. Not worth changing days before a live demo. Recorded here rather than fixed.
- **`asyncio.iscoroutinefunction` deprecation warnings** from `server.py` line 136 under Python
  3.14. Noise in the log, no effect on behaviour.
- **The Pair B beat reading as genuine.** `pair_clone_hindi` commits HUMAN at p = 0.03 on a clean
  channel. That is the honest measured behaviour of the shipped head against a cloner held out of
  training, it is what the run sheet already tells the presenter to say, and the console must not
  paper over it. The rebuild makes the resulting operator action, challenge then device push, the
  most prominent thing on the screen instead.

## I. Server changes the rebuild required

The console is a view; three things it needed did not exist on the server, so they were added
rather than faked in the browser.

- `GET /api/runs` lists every call on record, live sessions first and then `runs/*.json`, newest
  first. Without it the audit view could only ever show the call in memory (defect C2).
- `GET /api/about` returns the running process's own configuration for the About panel: model,
  layer, trainable parameter count, hop, commit floor, stability window, challenge space, the
  channels a band was measured for, and the fallback channel. Nothing about the build is written
  into the HTML, so no version string in the UI can drift from the process serving it (defect E1).
- `POST /api/call/{id}/action` accepts `callback`, which appends a `callback_requested` block and
  deliberately does **not** move the transaction. Step 4 of the ladder existed in the docs and in
  the pitch but had no code and no ledger entry behind it, so the console could not have offered
  it honestly.

`CallSession` gained `closed`, set when a stream finishes or the socket drops, so the audit view
can tell a call still running from one that ended. Scoring, the gate, the ledger, the challenge
and the warrant are untouched.

## J. Verification run

Headless Chrome at exactly 1920x1080, against the live server, all four run-sheet beats plus the
ledger tamper and restore in one uninterrupted session:

| Beat | Line | Carrier | Result |
|---|---|---|---|
| 1 | Genuine caller, Hindi | Opus 24 kbps | reads genuine, committed at 1.5 s on risk 0.010, approval still held for the device factor |
| 2 | Clone, XTTS-v2 | Opus 24 kbps | reads synthetic, committed at 1.5 s on risk 0.990, transaction blocked |
| 3a | Pair A, the real person | clean | reads genuine, committed at 1.5 s |
| 3b | Pair B, 2025 cloner held out of training | clean | reads genuine at 1.5 s and drifts to 0.028, so the operator issues the challenge and the device push; "Not me" blocks the transfer |
| 4 | Audit, alter block 2 | | chain verified before, broken at block 2 after, every later block marked unverifiable, restore returns the view to the stored chain |
| extra | Clone, ElevenLabs 2026, dark theme | G.723.1 6.3 kbps | reads synthetic, committed at 1.5 s above a band of 0.571 measured for that carrier |

**Console errors across the whole session: none.** Every codec channel in the grid was also
exercised on a genuine recording without a server exception.

Screenshots, `docs/ui_shots/`, PNG at 1920 wide:

| File | View |
|---|---|
| `01-live-genuine-caller.png` | beat 1 |
| `02-live-known-clone-blocked.png` | beat 2 |
| `03-live-pair-a-real-person.png` | beat 3a |
| `04-live-unseen-clone-challenge-and-push.png` | beat 3b, challenge phrase and device push on screen |
| `05-live-unseen-clone-blocked-by-device.png` | beat 3b after "Not me" |
| `06-audit-chain-verified.png` | audit, chain verified |
| `07-audit-chain-broken-after-tamper.png` | audit, chain broken at block 2 |
| `08-evidence.png` | evidence |
| `09-about-diagnostics.png` | About and diagnostics |
| `10-live-dark-worst-carrier.png` | dark theme on the worst carrier |
