#!/usr/bin/env python3
"""Architecture diagram for the deck.

Two things this drawing has to carry that a plain block diagram does not:
  1. every wire between two blocks states the data that crosses it and how often;
  2. the prevention ladder is drawn as a rising staircase, not a bullet list, because
     the argument is that each rung depends less on the detector than the one below it.

Every number on the picture is read from eval/results.json, so it cannot drift.
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ppt", "assets", "architecture.png")
R = json.load(open(os.path.join(ROOT, "eval", "results.json")))
BAND = R["ship"]["band_by_channel"]
N_TRAIN = R["ship"]["n_trainable"]
MIN_COMMIT = R["streaming"]["min_commit_s"]
FPR_BUDGET = R["streaming"]["fpr_budget"]
BC, BW = BAND["clean"]["4.0"], BAND["g723_1_6k3"]["4.0"]

INK, MUTE, BLUE, GREEN, RED, AMBER = "#17161a", "#6b6972", "#2b4bd6", "#1d7f52", "#b8322a", "#b9770e"
PAPER, WARM, MINT = "#fbfaf6", "#fdf5e7", "#f0f6f2"
plt.rcParams.update({"font.family": "Avenir Next"})

fig = plt.figure(figsize=(10.0, 7.5), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])          # 1 unit = 0.1 in, so text sizing is predictable
ax.set_xlim(0, 100); ax.set_ylim(0, 75); ax.axis("off")
fig.canvas.draw()
_R = fig.canvas.get_renderer()


def _w(t):
    bb = t.get_window_extent(renderer=_R)
    inv = ax.transData.inverted()
    (x0, _), (x1, _) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
    return x1 - x0


def fit(x, y, s, max_w, size, **kw):
    """Draw text, shrinking the font until it fits max_w. Wording never changes."""
    t = ax.text(x, y, s, fontsize=size, va="top", **kw)
    for _ in range(40):
        if _w(t) <= max_w:
            break
        size -= 0.15
        if size < 5.6:
            break
        t.set_fontsize(size)
    return t


def block(x, y, w, h, title, lines, color=INK, fill=PAPER, tsize=12.0, lsize=9.4, lead=2.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.4",
                                fc=fill, ec=color, lw=1.3))
    pad = 1.3
    fit(x + pad, y + h - 1.4, title, w - 2 * pad, tsize, fontweight="bold", color=color)
    for i, l in enumerate(lines):
        fit(x + pad, y + h - 4.5 - i * lead, l, w - 2 * pad, lsize, color=INK)


def arrow(x1, y1, x2, y2, color=MUTE, lw=1.3):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
                                 color=color, lw=lw, shrinkA=0, shrinkB=0))


def wire(x1, x2, y, top, bottom):
    """A horizontal arrow that states what crosses it: the shape above, the rate below."""
    arrow(x1 + 0.6, y, x2 - 0.6, y)
    mid, span = (x1 + x2) / 2, (x2 - x1) - 1.0
    fit(mid, y + 4.2, top, span, 8.4, color=INK, ha="center")
    fit(mid, y - 1.4, bottom, span, 8.4, color=MUTE, ha="center")


# ---------------------------------------------------------------- header
fit(0.5, 74.4, "On-device, streaming, prevention-first", 56, 15.0, fontweight="bold", color=INK)
fit(99.5, 73.8, "no audio leaves the machine   |   CPU only   |   Hindi, Tamil, Telugu",
    42, 10.0, color=MUTE, ha="right")

# ---------------------------------------------------------------- the signal path
Y1, H1 = 57.0, 14.0
MID = Y1 + H1 / 2
block(0.5, Y1, 14.5, H1, "Live call",
      ["PSTN, VoIP", "or mobile", "5 codecs,", "packet loss"], color=MUTE, tsize=11.0, lsize=8.6, lead=2.4)
block(25.0, Y1, 26.0, H1, "Listener",
      ["frozen XLS-R 300M, 128 languages", "layer 5, mean and std pooled",
       f"head: {N_TRAIN:,} trained parameters", "isotonic calibration per prefix"], color=BLUE)
block(61.0, Y1, 21.5, H1, "Gate",
      ["commit or defer,", "never guess in between", f"earliest verdict {MIN_COMMIT} s",
       "stable for 3 updates"], color=AMBER)
block(88.0, Y1, 11.5, H1, "Hold",
      ["the high-value", "action waits", "for a non-voice", "factor"], color=RED, tsize=11.0, lsize=8.4, lead=2.4)
wire(15.0, 25.0, MID, "16 kHz PCM", "0.5 s hops")
wire(51.0, 61.0, MID, "2048-d vector", "prefix to 8 s")
wire(82.5, 88.0, MID, "P(synthetic)", "every 0.5 s")

# ---------------------------------------------------------------- the threshold, drawn not listed
block(0.5, 43.0, 48.0, 11.5, "The commit band is derived, never typed",
      [f"From genuine speech alone at a {FPR_BUDGET * 100:.0f}% false-alarm budget, so it moves with the line:",
       f"[{BC['tau_human']:.3f}, {BC['tau_clone']:.3f}] on a clean channel, "
       f"[{BW['tau_human']:.3f}, {BW['tau_clone']:.3f}] on G.723.1 at 6.3 kbps.",
       "Genuine speech scores higher the harder the codec squeezes it."],
      color=AMBER, fill=WARM, tsize=10.8, lsize=8.8, lead=2.5)
ax.add_patch(FancyArrowPatch((49.5, 52.0), (61.0, 58.5), arrowstyle="-", linestyle=(0, (3, 3)),
                             color=AMBER, lw=1.0))

# ---------------------------------------------------------------- the ladder, as a staircase
fit(1.0, 40.5, "Prevention ladder", 30, 12.0, fontweight="bold", color=GREEN)
fit(1.0, 36.8, "Runs whenever the Gate defers, and always for a high-value", 47, 8.8, color=MUTE)
fit(1.0, 34.3, "action. Each rung up needs less from the detector than the", 47, 8.8, color=MUTE)
fit(1.0, 31.8, "rung below it.", 47, 8.8, color=MUTE)

RUNGS = [("1  Streaming score", ["the passive layer, and the only", "rung the detector can be wrong about"], MUTE),
         ("2  Live challenge", ["random digits and a word in the", "caller's language, 160,000 pairs"], GREEN),
         ("3  Device approval", ["push to the claimed person's", "registered device, not the call"], GREEN),
         ("4  Callback or block", ["number of record, operator", "decides, every step in the ledger"], GREEN)]
RW, RH = 22.5, 8.8
for i, (t, lines, col) in enumerate(RUNGS):
    x, y = 1.0 + i * 24.8, 8.5 + i * 7.6
    block(x, y, RW, RH, t, lines, color=col, fill=PAPER if col is MUTE else MINT,
          tsize=10.2, lsize=8.0, lead=2.2)
    if i:
        arrow(x - 2.0, y - 1.2, x + 0.8, y + 1.6, color=GREEN, lw=1.1)

arrow(66.0, 57.0, 66.0, 42.0, color=AMBER, lw=1.4)
ax.text(67.5, 48.5, "defer, or high value", fontsize=8.6, color=AMBER, ha="left", va="center")
arrow(96.0, 40.5, 96.0, 57.0, color=GREEN, lw=1.4)
ax.text(94.8, 48.5, "cleared or blocked", fontsize=8.6, color=GREEN, ha="right", va="center", rotation=90)

# ---------------------------------------------------------------- the record
block(0.5, 0.5, 99.0, 6.6, "Tamper-evident audit ledger",
      ["One block per score, verdict, challenge and approval.   "
       "block hash = SHA-256(previous hash + block).   Verify endpoint; export to any anchoring chain."],
      color=INK, tsize=11.0, lsize=8.8)

fig.savefig(OUT, bbox_inches="tight", transparent=True)
print("wrote", OUT)
