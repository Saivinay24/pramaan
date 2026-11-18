#!/usr/bin/env python3
"""Recompute every timing in docs/VIDEO_SCRIPT.md from the lines themselves.

Editing a spoken line changes that speaker's block, which changes every downstream start time,
the beat sheet and the totals table. Doing that by hand is how the script drifted before. This
derives all of it from the per-line word counts and rewrites the derived fields in place.

    python3 scripts/retime_script.py          # rewrite
    python3 scripts/retime_script.py --check   # verify only, non-zero exit if stale
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "VIDEO_SCRIPT.md"
WPM = 145
LIMIT = 600

LINE = re.compile(r"^\*\*Line (\d)\.(\d+)\*\* · (\d+) words · [\d.]+ s$", re.M)
HEADER = re.compile(
    r"^\*\*Beats ([\d, and]+)\. \d:\d\d to \d:\d\d\. Block length \d:\d\d\. \d+ words, which at 145 wpm is \d+ s of\s*\n?\s*speech,",
    re.M)


def mmss(t):
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def main():
    check = "--check" in sys.argv
    s = SRC.read_text()

    # words actually spoken, per speaker
    words = {}
    for m in LINE.finditer(s):
        spk = int(m.group(1))
        words[spk] = words.get(spk, 0) + int(m.group(3))

    # held and breath are editorial, read them from the existing totals table
    held, breath = {}, {}
    for m in re.finditer(r"^\| S(\d) \| [^|]+ \| \d+ \| [\d.]+ s \| (\d+) s \| (\d+) s \|", s, re.M):
        held[int(m.group(1))] = int(m.group(2))
        breath[int(m.group(1))] = int(m.group(3))

    rows, t = [], 0
    for spk in range(1, 7):
        w = words[spk]
        speech = round(w / WPM * 60, 1)
        exact = round(speech + held[spk] + breath[spk], 1)
        block = int(round(exact))
        rows.append(dict(spk=spk, w=w, speech=speech, held=held[spk], breath=breath[spk],
                         exact=exact, block=block, start=t, end=t + block))
        t += block

    total_block = t
    stale = []

    # 1. per-speaker headers
    def header_sub(m):
        spk = int(re.search(r"### S(\d)\.", s[:m.start()][::-1][::-1].rsplit("### S", 1)[0] if False else
                            s[:m.start()]).group(1)) if False else None
        return m.group(0)

    for r in rows:
        pat = re.compile(
            rf"(### S{r['spk']}\.[^\n]*\n\n\*\*Beats [^.]+\. )\d:\d\d to \d:\d\d(\. Block length )\d:\d\d(\. )\d+( words, which at 145 wpm is )\d+( s of)")
        new = rf"\g<1>{mmss(r['start'])} to {mmss(r['end'])}\g<2>{mmss(r['block'])}\g<3>{r['w']}\g<4>{int(round(r['speech']))}\g<5>"
        s2 = pat.sub(new, s)
        if s2 != s:
            stale.append(f"S{r['spk']} header")
        s = s2

    # 2. totals table
    for r in rows:
        pat = re.compile(rf"^\| S{r['spk']} \| ([^|]+) \| \d+ \| [\d.]+ s \| \d+ s \| \d+ s \| [\d.]+ s \| \*\*\d:\d\d\*\* \| \d:\d\d to \d:\d\d \|$", re.M)
        new = (rf"| S{r['spk']} | \g<1> | {r['w']} | {r['speech']} s | {r['held']} s | {r['breath']} s | "
               rf"{r['exact']} s | **{mmss(r['block'])}** | {mmss(r['start'])} to {mmss(r['end'])} |")
        s2 = pat.sub(new, s)
        if s2 != s:
            stale.append(f"S{r['spk']} table row")
        s = s2

    tw = sum(r["w"] for r in rows)
    tsp = round(sum(r["speech"] for r in rows), 1)
    th = sum(r["held"] for r in rows)
    tb = sum(r["breath"] for r in rows)
    tex = round(tsp + th + tb, 1)
    s2 = re.sub(r"^\| \*\*Total\*\* \| 18 \| \*\*[\d,]+\*\* \| \*\*[\d.]+ s\*\* \| \*\*\d+ s\*\* \| \*\*\d+ s\*\* \| \*\*[\d.]+ s\*\* \| \*\*\d:\d\d\*\* \| \|$",
                f"| **Total** | 18 | **{tw:,}** | **{tsp} s** | **{th} s** | **{tb} s** | **{tex} s** | **{mmss(total_block)}** | |",
                s, flags=re.M)
    if s2 != s:
        stale.append("totals row")
    s = s2

    # 3. headline and the arithmetic block
    head = round(LIMIT - total_block)
    s2 = re.sub(r"^\*\*Total runtime \d:\d\d\. Hard limit 10:00\. Headroom \d:\d\d\.\*\*$",
                f"**Total runtime {mmss(total_block)}. Hard limit 10:00. Headroom {mmss(head)}.**", s, flags=re.M)
    if s2 != s:
        stale.append("runtime headline")
    s = s2
    s = re.sub(r"^\| \*\*Exact total\*\* \| \*\*[\d.]+ s\*\* \|$",
               f"| **Exact total** | **{tex} s** |", s, flags=re.M)
    s = re.sub(r"^\| \*\*After per-beat rounding to whole seconds\*\* \| \*\*\d+ s = \d:\d\d\*\* \|$",
               f"| **After per-beat rounding to whole seconds** | **{total_block} s = {mmss(total_block)}** |", s, flags=re.M)
    s = re.sub(r"^\| Headroom to the 10:00 limit \| \*\*\d+ s \(\d:\d\d\)\*\* \|$",
               f"| Headroom to the 10:00 limit | **{head} s ({mmss(head)})** |", s, flags=re.M)

    print(f"{'STALE' if (check and stale) else 'timing'}: total {total_block} s = {mmss(total_block)}, "
          f"headroom {head} s, limit {LIMIT} s")
    for r in rows:
        print(f"  S{r['spk']}  {r['w']:>4} words  speech {r['speech']:>5} s  "
              f"block {mmss(r['block'])}  {mmss(r['start'])} to {mmss(r['end'])}")
    if total_block > LIMIT:
        print(f"OVER THE LIMIT by {total_block - LIMIT} s", file=sys.stderr)
        sys.exit(2)

    if check:
        if stale:
            print("stale fields: " + ", ".join(stale), file=sys.stderr)
            sys.exit(1)
        print("script timing is current")
        return
    SRC.write_text(s)
    print("rewrote derived timing fields")


if __name__ == "__main__":
    main()
