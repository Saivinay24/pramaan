#!/usr/bin/env python3
"""Burn captions into the finished demo video.

Timing comes from the build itself, not from transcribing the render: every line's audio file
and its exact placement are already known, so each caption sits on the words it belongs to.
The text comes from docs/VIDEO_SCRIPT.md, so captions say what was written rather than what a
recogniser guessed.

This ffmpeg has neither libass nor libfreetype, so captions are drawn with PIL into a
transparent track and composited.

    python3 scripts/burn_captions.py           ->  video/out/pramaan_demo_captioned.mp4
    python3 scripts/burn_captions.py --srt     ->  also writes video/out/pramaan_demo.srt
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "video"))
import build as B                                     # noqa: E402
from PIL import Image, ImageDraw, ImageFont            # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "video" / "out"
WORK = OUT / "capwork"
SRC = OUT / "pramaan_demo.mp4"
DST = OUT / "pramaan_demo_captioned.mp4"

W, H, FPS = 1920, 1080, 30
MAX_CHARS = 44          # per caption line
MAX_LINES = 2
FONT_PX = 40
PAD_X, PAD_Y = 30, 18
BOTTOM = 62             # distance from frame bottom to the box

# what the two cold open clips say, cut to the sentence they share
COLD_TEXT = ("I was in an accident and I'm in hospital. I'm okay, but they won't "
             "start the treatment until I pay the emergency bill upfront.")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("FAILED:", " ".join(map(str, cmd))[:220], file=sys.stderr)
        print(p.stderr[-1500:], file=sys.stderr)
        sys.exit(1)
    return p


def font(sz):
    for c in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap(text, limit=MAX_CHARS):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= limit:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def split_even(words, n):
    """Split words into n chunks of near equal length, so no chunk is a stray few words."""
    if n <= 1:
        return [" ".join(words)]
    target = sum(len(w) + 1 for w in words) / n
    out, cur, acc = [], [], 0.0
    for i, w in enumerate(words):
        remaining_chunks = n - len(out)
        if remaining_chunks > 1 and acc >= target and len(words) - i >= remaining_chunks - 1:
            out.append(" ".join(cur)); cur, acc = [], 0.0
        cur.append(w); acc += len(w) + 1
    if cur:
        out.append(" ".join(cur))
    return out


def chunk(text):
    """Split a spoken line into caption sized pieces, preferring sentence ends."""
    pieces, cur = [], ""
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):
        if not sent:
            continue
        cand = (cur + " " + sent).strip()
        if len(wrap(cand)) <= MAX_LINES:
            cur = cand
            continue
        if cur:
            pieces.append(cur)
            cur = ""
        if len(wrap(sent)) <= MAX_LINES:
            cur = sent
            continue
        # one sentence too long for a caption: divide it evenly rather than filling then
        # leaving a three word tail on screen by itself
        words = sent.split()
        n = 2
        while True:
            parts = split_even(words, n)
            if all(len(wrap(x)) <= MAX_LINES for x in parts) or n > len(words):
                break
            n += 1
        pieces.extend(parts[:-1])
        cur = parts[-1]
    if cur:
        pieces.append(cur)
    return pieces or [text]


def render(text, dst):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(FONT_PX)
    lines = wrap(text)[:MAX_LINES]
    widths = [d.textbbox((0, 0), l, font=f)[2] for l in lines]
    lh = int(FONT_PX * 1.34)
    bw, bh = max(widths) + PAD_X * 2, lh * len(lines) + PAD_Y * 2
    x0, y0 = (W - bw) // 2, H - BOTTOM - bh
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=14, fill=(8, 10, 14, 214))
    for i, l in enumerate(lines):
        tw = widths[i]
        d.text(((W - tw) / 2, y0 + PAD_Y + i * lh), l, font=f, fill=(255, 255, 255, 255))
    img.save(dst)


def cues():
    """(start, end, text) for the cold open clips and every spoken line, in order."""
    lines_for = B.beat_lines()
    script = (ROOT / "docs" / "VIDEO_SCRIPT.md").read_text()
    text_of = {}
    cur = None
    for ln in script.split("\n"):
        m = re.match(r"^\*\*Line (\d+\.\d+)\*\*", ln)
        if m:
            cur = m.group(1); continue
        if cur and ln.startswith("> "):
            text_of.setdefault(cur, ln[2:].strip("*").strip())
            cur = None

    out, t = [], 0.0
    for num, spk, planned, vis in B.BEATS:
        ids = lines_for.get(num, [])
        aud, alen = B.beat_audio(num, ids)
        hold = B.COLD_CLIPS_S if num == 1 else 0.0
        secs = (hold + alen + 0.35) if aud else float(planned)

        if num == 1:                       # the two clips, before any narration
            lead, gap = 1.6, 0.8
            a_len = next(e - s for tag, _, s, e in __import__("coldopen").CLIPS if tag == "real")
            b_len = next(e - s for tag, _, s, e in __import__("coldopen").CLIPS if tag == "clone")
            for st, ln_ in ((t + lead, a_len), (t + lead + a_len + gap, b_len)):
                parts = chunk(COLD_TEXT)
                total = sum(len(p) for p in parts)
                off = st
                for p in parts:
                    d = ln_ * len(p) / total
                    out.append((off, off + d, p))
                    off += d

        off = t + hold
        for lid in ids:
            f = B.VO / "_work" / f"S{lid.split('.')[0]}_{lid.replace('.', '_')}.wav"
            if not f.exists():
                continue
            d_line = B.duration(f)
            spoken = max(0.1, d_line - 0.45)          # the pad is silence, do not caption it
            parts = chunk(text_of.get(lid, ""))
            total = sum(len(p) for p in parts) or 1
            o = off
            for p in parts:
                dd = spoken * len(p) / total
                out.append((o, o + dd, p))
                o += dd
            off += d_line
        t += secs
    return out


def srt_time(s):
    h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC}; run video/build.py first")
    c = cues()
    print(f"{len(c)} captions across {c[-1][1]:.1f}s")

    if "--srt" in sys.argv:
        p = OUT / "pramaan_demo.srt"
        p.write_text("".join(
            f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(c, 1)))
        print("wrote", p.relative_to(ROOT))

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    # a transparent caption track: one still per cue, plus blanks in the gaps
    blank = WORK / "blank.png"
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    entries, prev = [], 0.0
    for a, b, text in c:
        if a - prev > 0.04:
            entries.append((blank, a - prev))
        png = WORK / f"c{len(entries):04d}.png"
        render(text, png)
        entries.append((png, max(0.08, b - a)))
        prev = b

    total = B.duration(SRC)
    if total > prev:
        entries.append((blank, total - prev))

    lst = WORK / "track.txt"
    lst.write_text("".join(f"file '{p}'\nduration {d:.3f}\n" for p, d in entries)
                   + f"file '{entries[-1][0]}'\n")
    track = WORK / "captions.mov"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-vsync", "cfr", "-r", str(FPS), "-c:v", "qtrle", "-pix_fmt", "argb", str(track)])

    run(["ffmpeg", "-y", "-v", "error", "-i", str(SRC), "-i", str(track),
         "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "21",
         "-profile:v", "high", "-level", "4.1",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(DST)])
    print(f"wrote {DST.relative_to(ROOT)}  {B.duration(DST):.2f}s")


if __name__ == "__main__":
    main()
