#!/usr/bin/env python3
"""Assemble the SIH 2026 national-round demo video.

Sources live in video/source. Narration, when it exists, lives in docs/vo/S1.wav .. S6.wav.

Each speaker owns a contiguous run of beats. The beat lengths in BEATS are the ones planned in
docs/VIDEO_SCRIPT.md. When a speaker's recording exists, that speaker's beats are scaled by
actual_audio_length / planned_block_length, so a speaker who reads slowly stretches their own
visuals and nobody else's. With no recording present the planned length is used and the segment
runs silent, which is the timed silent cut.

    python3 video/build.py            # build whatever is available
    python3 video/build.py --silent   # ignore docs/vo entirely, build the silent reference cut

Output: video/out/pramaan_demo.mp4
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys_path_added = False

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "video" / "source"
VO = ROOT / "docs" / "vo"
OUT = ROOT / "video" / "out"
WORK = OUT / "work"

W, H, FPS = 1920, 1080, 30

# beat, speaker, planned seconds, visual
# visual: ("panel", name) | ("clip", file, start, end) | ("coldopen",) | ("titlecard",)
# There are NO presentation slides in this video. Every visual is the running console,
# apart from beat 1 (cold open) and beat 18 (title card). See docs/VIDEO_SCRIPT.md.
BEATS = [
    (1,  "S1", 14, ("coldopen",)),
    (2,  "S1", 62, ("clipm", "atrest_master.mp4", "start", "end")),
    (3,  "S1", 33, ("panel", "ladder")),
    (4,  "S2", 36, ("panel", "about")),
    (5,  "S2", 22, ("clipm", "console_master.mp4", "C0 carrier sweep begin", "A1 audit tab")),
    (6,  "S2", 57, ("panel", "diversity")),
    (7,  "S3", 33, ("clipm", "console_master.mp4",
                    "L1 genuine hindi opus24 :: start", "L1 genuine hindi opus24 :: end")),
    (8,  "S3", 23, ("clipm", "console_master.mp4",
                    "L2 clone xtts seen :: start", "L2 clone xtts seen :: end")),
    (9,  "S3", 63, ("clipm", "console_master.mp4",
                    "L3 pairA real :: start", "L4 pairB clone 2025 :: end")),
    (10, "S3", 28, ("clipm", "console_master.mp4", "A1 audit tab", "A5 restore")),
    (11, "S4", 30, ("panel", "heatmap")),
    (12, "S4",  7, ("panel", "calibration")),
    # 4.5 and 4.6 describe the adversarial sweep, which has no console panel of its own, so they
    # play over the Evidence tab itself. 4.7 is about the streaming curve, so it gets that panel.
    (13, "S4", 16, ("clipm", "console_master.mp4", "E1 evidence tab", "B1 about open")),
    (14, "S4", 11, ("panel", "audioarrives")),
    (15, "S5", 38, ("panel", "scoringcost")),
    (16, "S5", 33, ("panel", "adaptcost")),
    (17, "S6", 19, ("panel", "about")),
    (18, "S6", 34, ("clipm", "console_master.mp4", "E1 evidence tab", "B1 about open")),
    (19, "S6", 10, ("titlecard",)),
]

SPEAKERS = ["S1", "S2", "S3", "S4", "S5", "S6"]



def _font(size):
    from PIL import ImageFont
    for cand in ("/System/Library/Fonts/Helvetica.ttc",
                 "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/Library/Fonts/Arial.ttf"):
        if Path(cand).exists():
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass
    return ImageFont.load_default()


def text_png(dst, lines):
    """lines: list of (text, size, fill, y_fraction). Transparent RGBA overlay."""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, size, fill, yf in lines:
        f = _font(size)
        box = d.textbbox((0, 0), text, font=f)
        d.text(((W - (box[2] - box[0])) / 2, H * yf), text, font=f, fill=fill)
    img.save(dst)
    return dst


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("FAILED:", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(p.stderr[-2500:], file=sys.stderr)
        sys.exit(1)
    return p


def duration(path):
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)])
    return float(p.stdout.strip())



_MARKS_CACHE = {}


def marks_for(src_name):
    if src_name not in _MARKS_CACHE:
        mf = SRC / (Path(src_name).stem + ".marks.json")
        if not mf.exists():
            print(f"missing marks file {mf}", file=sys.stderr)
            sys.exit(1)
        _MARKS_CACHE[src_name] = json.loads(mf.read_text())
    return _MARKS_CACHE[src_name]


def mark_time(src_name, name):
    """Time of a named capture mark. Beats reference marks, not raw seconds, so a
    re-capture cannot silently shift every beat."""
    for m in marks_for(src_name):
        if m["name"] == name:
            return float(m["t"])
    print(f"mark not found in {src_name}: {name}", file=sys.stderr)
    sys.exit(1)


def make_coldopen(dst, seconds):
    """Beat 1. One whole Hindi sentence, spoken by the real person then by the clone.

    Composed in video/coldopen.py: full width waveform, playhead tracking the audio, and a
    sentence that is never cut mid word. See that file for the layout.
    """
    import coldopen
    coldopen.build(dst, total=seconds, work=WORK / "cold")
    return True


def make_titlecard(dst, seconds):
    cap = text_png(WORK / f"{dst.stem}_card.png", [
        ("Pramaan", 130, (255, 255, 255, 255), 0.36),
        ("Proof before approval", 52, (170, 170, 170, 255), 0.54),
    ])
    run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={seconds}",
        "-i", str(cap),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={seconds}",
        "-filter_complex", "[0:v][1:v]overlay=0:0,setsar=1[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{seconds}", str(dst),
    ])


PAGE_BG = "0xf5f6f7"


def make_panel(dst, name, seconds):
    """A high-DPI panel screenshot, fitted on the console background with a slow push."""
    img = SRC / "panels" / f"{name}.png"
    if not img.exists():
        print(f"missing panel {img}", file=sys.stderr)
        sys.exit(1)
    frames = max(1, int(seconds * FPS))
    run([
        "ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(img),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={seconds}",
        "-filter_complex",
        (f"[0:v]scale=w='min(iw,{int(W*0.86)})':h='min(ih,{int(H*0.86)})':"
         f"force_original_aspect_ratio=decrease:flags=lanczos,"
         f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={PAGE_BG},"
         f"zoompan=z='min(1.05,1+0.05*on/{frames})':d={frames}:"
         f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
         f"setsar=1[v]"),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{seconds}", str(dst),
    ])


def make_clip(dst, src_name, start, end, seconds):
    """Cut from a capture. If the beat outlasts the source, hold the last frame."""
    src = SRC / src_name
    if not src.exists():
        print(f"missing {src}", file=sys.stderr)
        sys.exit(1)
    available = end - start
    take = min(seconds, available)
    pad = seconds - take
    vf = f"fps={FPS},scale={W}:{H},setsar=1"
    if pad > 0.04:
        vf += f",tpad=stop_mode=clone:stop_duration={pad:.3f}"
    run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{start}", "-i", str(src),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=48000:d={seconds}",
        "-t", f"{take}", "-vf", vf,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{seconds}", str(dst),
    ])



# ---------------------------------------------------------------- beat level audio placement
def _cold_clips_s():
    """Seconds of beat 1 that belong to the two clips, so narration starts after them."""
    import coldopen
    lead, gap = 1.6, 0.8
    return round(lead + sum(e - st for _, _, st, e in coldopen.CLIPS) + gap, 3)


COLD_CLIPS_S = _cold_clips_s()   # narration-free head of beat 1


def beat_lines():
    """Which script lines fall under which beat, in order. Parsed from the script itself."""
    import re as _re
    txt = (ROOT / "docs" / "VIDEO_SCRIPT.md").read_text()
    out, beat = {}, None
    for ln in txt.split("\n"):
        m = _re.match(r"^\*\*BEAT (\d+)\.", ln)
        if m:
            beat = int(m.group(1)); out.setdefault(beat, []); continue
        m = _re.match(r"^\*\*Line (\d+\.\d+)\*\*", ln)
        if m and beat:
            out[beat].append(m.group(1))
    return out


def beat_audio(num, line_ids):
    """One audio file per beat: that beat's lines, in order. None when nothing was recorded."""
    parts = []
    for lid in line_ids:
        spk = lid.split(".")[0]
        f = VO / "_work" / f"S{spk}_{lid.replace('.', '_')}.wav"
        if f.exists():
            parts.append(f)
    if not parts:
        return None, 0.0
    dst = WORK / f"beat{num:02d}.wav"
    if len(parts) == 1:
        shutil.copy(str(parts[0]), str(dst))
    else:
        lst = WORK / f"beat{num:02d}_audio.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)])
    return dst, duration(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--silent", action="store_true",
                    help="ignore docs/vo and build the timed silent reference cut")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    lines_for = beat_lines()

    # Each beat is as long as the narration that belongs to it. A line is therefore always
    # spoken while its own visual is on screen, which concatenating per speaker did not do.
    plan = []
    for num, spk, planned, vis in BEATS:
        aud, alen = (None, 0.0) if args.silent else beat_audio(num, lines_for.get(num, []))
        hold = COLD_CLIPS_S if num == 1 else 0.0
        if aud is None:
            secs = float(planned)          # nothing recorded: keep the planned length
        else:
            secs = hold + alen + 0.35      # a breath after the last line of the beat
        plan.append(dict(num=num, spk=spk, vis=vis, aud=aud, hold=hold, secs=round(secs, 3)))

    t = 0.0
    for b in plan:
        b["start"] = t
        t += b["secs"]
    total = t

    for b in plan:
        dst = WORK / f"beat{b['num']:02d}.mp4"
        kind = b["vis"][0]
        if kind == "coldopen":
            make_coldopen(dst, b["secs"])
        elif kind == "titlecard":
            make_titlecard(dst, b["secs"])
        elif kind == "panel":
            make_panel(dst, b["vis"][1], b["secs"])
        elif kind == "clip":
            make_clip(dst, b["vis"][1], b["vis"][2], b["vis"][3], b["secs"])
        elif kind == "clipm":
            src_name = b["vis"][1]
            make_clip(dst, src_name, mark_time(src_name, b["vis"][2]),
                      mark_time(src_name, b["vis"][3]), b["secs"])
        say = ",".join(lines_for.get(b["num"], [])) or "no narration"
        print(f"  beat {b['num']:>2} [{b['spk']}] {b['secs']:7.2f}s  {kind:<9} {say}")

    lst = WORK / "all.txt"
    lst.write_text("".join(f"file '{WORK}/beat{b['num']:02d}.mp4'\n" for b in plan))
    spine = WORK / "spine.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-vsync", "cfr", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(spine)])

    final = OUT / "pramaan_demo.mp4"
    voiced = [b for b in plan if b["aud"]]
    if not voiced:
        shutil.move(str(spine), str(final))
        print(f"\nsilent reference cut: {final}  {duration(final):.2f}s")
        return

    # lay every beat's narration at that beat's own start, after any narration-free hold
    # input 0 is the spine, which carries the cold open's two clips. That audio is part of the
    # film, not a placeholder: mixing only the narration silenced the very thing beat 1 exists
    # to play.
    inputs, filters, mixes = ["-i", str(spine)], [], []
    filters.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[a0]")
    mixes.append("[a0]")
    for i, b in enumerate(voiced, start=1):
        inputs += ["-i", str(b["aud"])]
        ms = int(round((b["start"] + b["hold"]) * 1000))
        filters.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{i}]")
        mixes.append(f"[a{i}]")
    filters.append("".join(mixes) + f"amix=inputs={len(voiced) + 1}:normalize=0[mixed]")
    filters.append("[mixed]alimiter=limit=0.95[aout]")

    run(["ffmpeg", "-y", *inputs, "-v", "error",
         "-filter_complex", ";".join(filters),
         "-map", "0:v:0", "-map", "[aout]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
         "-shortest", str(final)])

    d = duration(final)
    print(f"\nbuilt: {final}  {d:.2f}s ({int(d//60)}:{d%60:04.1f})")
    if d > 600:
        print(f"WARNING: over the 10:00 limit by {d-600:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
