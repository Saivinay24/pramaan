#!/usr/bin/env python3
"""Split docs/VIDEO_SCRIPT.md into six standalone recording sheets, one per speaker.

Each sheet is self contained: what to do, how to record, your lines, how to say the hard words,
and what to send back. Nobody should have to open the master script or read anyone else's part.

    python3 scripts/make_vo_sheets.py

Writes docs/vo_scripts/S1.md .. S6.md. Export to PDF with scripts/export_pdfs.py if wanted.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "VIDEO_SCRIPT.md"
OUT = ROOT / "docs" / "vo_scripts"


def section(lines, start_pat, stop_pat):
    """Lines from the first heading matching start_pat up to the next matching stop_pat."""
    out, on = [], False
    for ln in lines:
        if not on and re.match(start_pat, ln):
            on = True
            out.append(ln)
            continue
        if on:
            if re.match(stop_pat, ln):
                break
            out.append(ln)
    return "\n".join(out).rstrip()


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC}")
    lines = SRC.read_text().split("\n")

    protocol = section(lines, r"^## 4\. Recording instructions", r"^## 5\.")
    protocol = protocol.replace("## 4. Recording instructions", "## How to record")
    pronounce = section(lines, r"^## 5\. Pronunciation", r"^## 6\.")
    pronounce = pronounce.replace("## 5. Pronunciation and delivery guide", "## How to say the hard words")

    # the one-line runtime header from the master script
    total = next((l for l in lines if l.startswith("**Total runtime")), "").strip("* ").rstrip(".")

    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for n in range(1, 7):
        tag = f"S{n}"
        body = section(lines, rf"^### {tag}\.", r"^### S[1-6]\.|^## \d\.")
        if not body:
            sys.exit(f"could not find section for {tag}")

        title = body.split("\n", 1)[0].replace("### ", "").strip()

        sheet = f"""# Pramaan demo video, recording sheet for {tag}

**{title}**

You are one of six speakers. This sheet has everything you need. You do not need the master
script and you do not need anyone else's part.

Whole video: {total}. Read only your own lines, below.

---

## What to do, in short

1. Read **How to record** below. It is short and it matters more than your delivery.
2. Record **your lines only**, in order.
3. Name the file `{tag}.wav` (or `{tag}.m4a`) and send it back.

Do not add music. Do not edit or trim the file. Do not record with anyone else in the room.

---

{protocol}

---

## Your lines

Everything below is yours. The numbers beside each line are the target length. They are a guide,
not a stopwatch: read at a natural pace and the edit adjusts to you. What matters is that you do
not rush the pauses.

{body}

---

{pronounce}

---

## Sending it back

File name `{tag}.wav` or `{tag}.m4a`. Put it in `docs/vo/` in the repository, or send it to
whoever is assembling the video.

Before you send it, play the whole file back once on headphones. A fan, a notification, a chair
or a page turn means record it again. That is faster than asking for it to be fixed later.
"""
        dst = OUT / f"{tag}.md"
        dst.write_text(sheet)
        made.append((tag, len(sheet), dst))

    print(f"wrote {len(made)} sheets to {OUT}")
    for tag, n, dst in made:
        print(f"  {tag}  {n:>6} chars  {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
