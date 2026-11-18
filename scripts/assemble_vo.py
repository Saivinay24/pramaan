#!/usr/bin/env python3
"""Turn per-line recordings into the six narration tracks video/build.py expects.

The team recorded one file per line ("Line 2.4.m4a") rather than one per speaker. Each clip is
trimmed of its head and tail silence, levelled, and the lines belonging to a speaker are joined
in script order with a short gap, producing docs/vo/S1.wav .. S6.wav.

    python3 scripts/assemble_vo.py [SOURCE_DIR]      default: ~/Downloads/voices
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "docs" / "VIDEO_SCRIPT.md"
VO = ROOT / "docs" / "vo"
WORK = VO / "_work"

GAP_S = 0.45          # breath between lines; the editor cuts on these
TRIM_DB = "-42dB"     # anything quieter than this at head/tail is room tone
TARGET_I = "-18"      # integrated loudness for narration


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("FAILED:", " ".join(map(str, cmd)), file=sys.stderr)
        print(p.stderr[-1500:], file=sys.stderr)
        sys.exit(1)
    return p


def dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)]).stdout.strip())


def main():
    src = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Downloads" / "voices"
    if not src.is_dir():
        sys.exit(f"no such directory: {src}")

    order = [f"{a}.{b}" for a, b in re.findall(r"^\*\*Line (\d+)\.(\d+)\*\*", SCRIPT.read_text(), re.M)]

    # map line id -> file, preferring a later take when several exist
    found = {}
    for f in sorted(src.glob("*.m4a")) + sorted(src.glob("*.wav")) + sorted(src.glob("*.mp3")):
        m = re.match(r"Line (\d+)\.(\d+)(.*)\.(m4a|wav|mp3)$", f.name, re.I)
        if not m:
            continue
        key = f"{m.group(1)}.{m.group(2)}"
        suffix = m.group(3).strip()
        # The bare name wins. A suffixed file is not reliably a better take: "Line 3.9 pt 2" is
        # the script's contingency alternate for a different on-screen outcome, and using it made
        # the narration contradict the footage.
        rank = 0 if suffix else 1
        if key not in found or rank > found[key][0]:
            found[key] = (rank, f)

    missing = [k for k in order if k not in found]
    if missing:
        print(f"WARNING: no recording for {missing}. Those lines will be silent.", file=sys.stderr)

    WORK.mkdir(parents=True, exist_ok=True)
    VO.mkdir(parents=True, exist_ok=True)

    silence = ("silenceremove=start_periods=1:start_silence=0.08:start_threshold=" + TRIM_DB +
               ":detection=peak,areverse,"
               "silenceremove=start_periods=1:start_silence=0.08:start_threshold=" + TRIM_DB +
               ":detection=peak,areverse")

    totals = {}
    for spk in "123456":
        ids = [k for k in order if k.startswith(spk + ".") and k in found]
        if not ids:
            print(f"S{spk}: nothing recorded, skipping")
            continue
        parts = []
        for key in ids:
            _, f = found[key]
            clean = WORK / f"S{spk}_{key.replace('.', '_')}.wav"
            run(["ffmpeg", "-y", "-v", "error", "-i", str(f),
                 "-af", f"{silence},loudnorm=I={TARGET_I}:TP=-2:LRA=11,"
                        f"apad=pad_dur={GAP_S}",
                 "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(clean)])
            parts.append(clean)

        lst = WORK / f"S{spk}.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        out = VO / f"S{spk}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out)])
        totals[spk] = dur(out)
        print(f"S{spk}: {len(parts):>2} lines -> {out.name}  {totals[spk]:6.2f} s")

    if totals:
        t = sum(totals.values())
        print(f"\nnarration total {t:.1f} s ({int(t//60)}:{t%60:04.1f})")


if __name__ == "__main__":
    main()
