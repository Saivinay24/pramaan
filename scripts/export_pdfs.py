#!/usr/bin/env python3
"""Every shipped PDF, from the markdown and the deck that fill_numbers.py and build_deck.py wrote.

Two paths, both headless, both matching how the PDFs already in the repo were made:

  docs/*.md   -> HTML -> Chrome print-to-PDF   (the shipped files carry Skia/PDF, HeadlessChrome)
  ppt/*.pptx  -> LibreOffice Impress PDF export (the shipped deck carries LibreOffice as producer)

Run it after scripts/fill_numbers.py and `make deck`, so no number reaches a rehearsal in
markdown while the PDF a judge is handed still says the old one.

  python3 scripts/export_pdfs.py            # every doc, then the deck
  python3 scripts/export_pdfs.py docs/QA_PREP.md

Needs the `markdown` package (pip install markdown), Google Chrome, and soffice.
"""
import html as htmlmod
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SOFFICE = "/opt/homebrew/bin/soffice"
DECK = os.path.join(ROOT, "ppt", "Pramaan_SIH2026_Idea.pptx")

# The markdown that is handed out as a PDF. The rest of docs/ has no PDF export.
DOCS = ["SPEAKER_S1", "SPEAKER_S2", "SPEAKER_S3", "SPEAKER_S4", "SPEAKER_S5",
        "SPEAKER_S6", "TEAM_GUIDE", "QA_PREP", "PRESENTATION_SCRIPT"]

CSS = """
@page { size: letter; margin: 0.47in; }
html { font-size: 16px; }
body {
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 16px; line-height: 1.65; color: #24292e; margin: 0; padding: 0;
  -webkit-print-color-adjust: exact;
}
h1 { font-size: 2.25em; font-weight: 700; margin: 0.6em 0 0.5em; line-height: 1.25; }
h2 { font-size: 1.75em; font-weight: 700; margin: 1.4em 0 0.5em; line-height: 1.25; }
h3 { font-size: 1.35em; font-weight: 700; margin: 1.2em 0 0.4em; }
h4, h5, h6 { font-size: 1.1em; font-weight: 700; margin: 1em 0 0.4em; }
p { margin: 0 0 1em; }
ul, ol { margin: 0 0 1em; padding-left: 1.8em; }
li { margin: 0.25em 0; }
blockquote { margin: 0 0 1em; padding: 0 1em; border-left: 3px solid #dfe2e5; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.9em;
       background: #f6f8fa; padding: 0.15em 0.35em; border-radius: 3px; }
pre { background: none; padding: 0.2em 0; overflow: visible; page-break-inside: avoid; }
/* 11px keeps the widest ASCII diagram line in TEAM_GUIDE.md, 102 characters, inside the
   text column. Anything larger clips the right-hand end of the line off the page. */
pre code { background: none; padding: 0; font-size: 11px; line-height: 1.45;
           white-space: pre; }
table { border-collapse: collapse; width: 100%; margin: 0 0 1.2em; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #dfe2e5; padding: 0.5em 0.75em; vertical-align: top;
         text-align: left; }
th { font-weight: 700; text-align: center; }
hr { border: 0; border-top: 1px solid #e1e4e8; margin: 1.5em 0; }
a { color: #24292e; text-decoration: none; }
h1, h2, h3, h4 { page-break-after: avoid; }
img { max-width: 100%; }
"""

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>{title}</title><style>{css}</style></head><body>{body}</body></html>"""


def md_to_pdf(md_path, workdir):
    import markdown

    title = os.path.splitext(os.path.basename(md_path))[0]
    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
    body = markdown.markdown(
        open(md_path, encoding="utf-8").read(),
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    html_path = os.path.join(workdir, title + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(TPL.format(title=htmlmod.escape(title), css=CSS, body=body))
    before = os.path.getmtime(pdf_path) if os.path.exists(pdf_path) else 0
    r = subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         "--print-to-pdf=" + pdf_path, "--virtual-time-budget=5000",
         "file://" + html_path],
        capture_output=True, text=True)
    if not os.path.exists(pdf_path) or os.path.getmtime(pdf_path) == before:
        sys.exit(f"chrome did not write {pdf_path}\n{r.stdout}\n{r.stderr}")
    return pdf_path


def deck_to_pdf():
    r = subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir",
         os.path.dirname(DECK), DECK], capture_output=True, text=True)
    pdf = os.path.splitext(DECK)[0] + ".pdf"
    if not os.path.exists(pdf):
        sys.exit(f"soffice did not write {pdf}\n{r.stdout}\n{r.stderr}")
    return pdf


def main():
    try:
        import markdown  # noqa: F401
    except ImportError:
        sys.exit("needs the markdown package: pip install markdown")
    for exe, what in ((CHROME, "Google Chrome"), (SOFFICE, "soffice")):
        if not os.path.exists(exe):
            sys.exit(f"{what} not found at {exe}")

    targets = sys.argv[1:] or [os.path.join(ROOT, "docs", n + ".md") for n in DOCS]
    with tempfile.TemporaryDirectory() as workdir:
        for md in targets:
            print("wrote", md_to_pdf(os.path.abspath(md), workdir))
    if not sys.argv[1:]:
        print("wrote", deck_to_pdf())


if __name__ == "__main__":
    main()
