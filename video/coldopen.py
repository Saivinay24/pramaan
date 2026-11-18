#!/usr/bin/env python3
"""Cold open: one complete Hindi sentence, spoken once by the real person and once by the clone.

Both source clips carry the same sentence and both fall silent at 4.00 s, so 0 to 4.0 is a whole
utterance in each. Nothing is cut mid word.

Layout is fixed and centred: the question sits above, the label in the middle, and the waveform
spans the full content width with a playhead that tracks the audio.
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
BG = "0x0b0d10"
MARGIN = 160                      # content gutter, same on both sides
WAVE_W, WAVE_H = W - MARGIN * 2, 200
WAVE_X, WAVE_Y = MARGIN, 520

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SAMPLES = ROOT / "data" / "samples"
# The opening pair: the same speaker saying the same sentence, once for real and once as an
# ElevenLabs clone of himself. Cut to the sentence both share, on the silences either side of it,
# so neither is clipped mid word.
CLIPS = [
    ("real",  "emergency_real.m4a",  2.74, 8.90),
    ("clone", "emergency_clone.mp3", 2.31, 8.75),
]


def prepare(work):
    """Cut the shared sentence out of each recording and draw its full width waveform."""
    work.mkdir(parents=True, exist_ok=True)
    lengths = {}
    for tag, src, start, end in CLIPS:
        wav = work / f"{tag}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(start), "-to", str(end),
             "-i", str(SAMPLES / src),
             "-af", "loudnorm=I=-18:TP=-2:LRA=11", "-ar", "48000", "-ac", "2",
             "-c:a", "pcm_s16le", str(wav)])
        lengths[tag] = round(end - start, 3)
        loud = work / f"{tag}_loud.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(wav),
             "-af", "volume=10dB,alimiter=limit=0.98", "-c:a", "pcm_s16le", str(loud)])
        run(["ffmpeg", "-y", "-v", "error", "-i", str(loud), "-filter_complex",
             f"showwavespic=s={WAVE_W}x{WAVE_H}:colors=0x7aa2f7|0x7aa2f7:scale=sqrt",
             "-frames:v", "1", str(work / f"{tag}_wave.png")])
    return lengths


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("FAILED:", " ".join(map(str, cmd)), file=sys.stderr)
        print(p.stderr[-2000:], file=sys.stderr)
        sys.exit(1)


def font(sz, bold=False):
    for c in ("/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, sz, index=1 if bold else 0)
            except Exception:
                try:
                    return ImageFont.truetype(c, sz)
                except Exception:
                    pass
    return ImageFont.load_default()


def card(dst, label=None, sub=None, question=True, tail=None):
    """Transparent overlay: question, big label, caption under the waveform."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def centre(text, f, y, fill):
        b = d.textbbox((0, 0), text, font=f)
        d.text(((W - (b[2] - b[0])) / 2, y), text, font=f, fill=fill)

    if question:
        centre("Same speaker. Same sentence.", font(52), 196, (236, 238, 242, 255))
        centre("One of these is a clone.", font(52), 258, (236, 238, 242, 255))
    if label:
        centre(label, font(96, bold=True), 366, (255, 255, 255, 255))
    if sub:
        centre(sub, font(32), WAVE_Y + WAVE_H + 56, (150, 158, 170, 255))
    if tail:
        centre(tail, font(38), WAVE_Y + WAVE_H + 56, (150, 158, 170, 255))
    img.save(dst)
    return dst


def hold(dst, seconds, overlay):
    run(["ffmpeg", "-y", "-v", "error",
         "-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={seconds}",
         "-i", str(overlay),
         "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={seconds}",
         "-filter_complex", "[0:v][1:v]overlay=0:0,setsar=1[v]",
         "-map", "[v]", "-map", "2:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000",
         "-t", str(seconds), str(dst)])


def play(dst, wav, wave_png, overlay, seconds):
    """Waveform spanning the full content width, with a playhead tracking the audio."""
    run(["ffmpeg", "-y", "-v", "error",
         "-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={seconds}",
         "-i", str(wave_png),
         "-i", str(overlay),
         "-f", "lavfi", "-i", f"color=c=0xe8ecf4:s=3x{WAVE_H}:r={FPS}:d={seconds}",
         "-i", str(wav),
         "-filter_complex",
         (f"[0:v][1:v]overlay={WAVE_X}:{WAVE_Y}[b1];"
          f"[b1][2:v]overlay=0:0[b2];"
          f"[b2][3:v]overlay=x='{WAVE_X}+(t/{seconds})*{WAVE_W}':y={WAVE_Y}[v]"),
         "-map", "[v]", "-map", "4:a",
         # the two clips are the point of this beat, so bring them to the narration's level
         "-af", "aresample=48000,aformat=channel_layouts=stereo",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "48000",
         "-t", str(seconds), str(dst)])


def build(out, total=14.0, work=None):
    work = Path(work) if work else HERE / "_work"
    lengths = prepare(work)
    lead, gap = 1.6, 0.8
    tail = max(0.5, total - (lead + lengths["real"] + gap + lengths["clone"]))

    q = card(work / "ov_q.png")
    a = card(work / "ov_a.png", label="A", sub="Recording A")
    b = card(work / "ov_b.png", label="B", sub="Recording B")
    t = card(work / "ov_t.png", tail="Same sentence, both times.")

    segs = []
    hold(work / "s1.mp4", lead, q);                      segs.append(work / "s1.mp4")
    play(work / "s2.mp4", work / "real.wav",  work / "real_wave.png",  a, lengths["real"]); segs.append(work / "s2.mp4")
    hold(work / "s3.mp4", gap, q);                       segs.append(work / "s3.mp4")
    play(work / "s4.mp4", work / "clone.wav", work / "clone_wave.png", b, lengths["clone"]); segs.append(work / "s4.mp4")
    hold(work / "s5.mp4", tail, t);                      segs.append(work / "s5.mp4")

    lst = work / "list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-vsync", "cfr", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)])
    print("cold open built:", out)


if __name__ == "__main__":
    build(HERE / "coldopen.mp4", float(sys.argv[1]) if len(sys.argv) > 1 else 14.0)
