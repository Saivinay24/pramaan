#!/usr/bin/env python3
"""Architecture diagram for slide 3, drawn as a diagram rather than plotted.

The previous version used matplotlib, which is a plotting library: boxes landed where their
coordinates put them, arrows crossed, and the five checks descended a staircase that read
backwards. This lays the picture out on a real grid with CSS and renders it through Chrome, so
alignment, type and spacing behave.

Every number is read from eval/results.json, so the drawing cannot drift from the results.

    python3 scripts/render_diagram.py        ->  ppt/assets/architecture.png
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ppt" / "assets" / "architecture.png"
WORK = ROOT / "ppt" / "assets" / "_diagram"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

W, H, SCALE = 1600, 955, 2          # 2x for a crisp slide placement

R = json.loads((ROOT / "eval" / "results.json").read_text())
SHIP = R["ship"]
N_TRAIN = f'{SHIP["n_trainable"]:,}'
MIN_COMMIT = R["streaming"]["min_commit_s"]
FPR = f'{R["streaming"]["fpr_budget"] * 100:.0f}%'
bc = SHIP["band_by_channel"]["clean"]["4.0"]
bw = SHIP["band_by_channel"]["g723_1_6k3"]["4.0"]
BAND_CLEAN = f'[{bc["tau_human"]:.3f}, {bc["tau_clone"]:.3f}]'
BAND_WORST = f'[{bw["tau_human"]:.3f}, {bw["tau_clone"]:.3f}]'

CHECKS = [
    ("1", "Voice check", "scores the live line<br>every half second"),
    ("2", "Live challenge", "a phrase in the caller's<br>own language to repeat"),
    ("3", "Device approval", "pushed to the claimed<br>person's own phone"),
    ("4", "Callback", "on the number already<br>on record"),
    ("5", "Decision", "cleared or blocked,<br>either way recorded"),
]

HTML = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
  :root {{
    --ink:#11161d; --muted:#5b6673; --line:#c9d2dd; --soft:#eef2f7;
    --accent:#1f5fd0; --accent-soft:#e8f0fd; --green:#0f7b5f; --green-soft:#e6f4ef;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ width:{W}px; height:{H}px; background:#fff; color:var(--ink);
         font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;
         padding:46px 50px; display:flex; flex-direction:column; gap:30px; }}

  .pipe {{ flex:1.25; display:grid; grid-template-columns:1fr 132px 1.35fr 132px 1.35fr 132px 1fr; align-items:stretch; }}
  .node {{ border:2px solid var(--line); border-radius:14px; padding:20px 22px; background:#fff;
           display:flex; flex-direction:column; gap:10px; justify-content:center; }}
  .node.lead {{ border-color:var(--accent); background:var(--accent-soft); }}
  .node.end  {{ border-color:var(--green);  background:var(--green-soft); }}
  .node h3 {{ font-size:27px; letter-spacing:-.01em; }}
  .node .q {{ font-size:17.5px; color:var(--muted); font-style:italic; }}
  .node ul {{ list-style:none; display:flex; flex-direction:column; gap:7px; }}
  .node li {{ font-size:17.5px; color:var(--ink); padding-left:11px; position:relative; line-height:1.34; }}
  .node li:before {{ content:""; position:absolute; left:0; top:7px; width:4px; height:4px;
                     border-radius:50%; background:var(--line); }}

  .arrow {{ display:flex; flex-direction:column; align-items:center; justify-content:center; gap:5px; }}
  .arrow .lbl {{ font-size:13.5px; color:var(--muted); white-space:nowrap;
                 text-align:center; line-height:1.2; }}
  .arrow svg {{ display:block; }}

  .band {{ display:flex; align-items:center; gap:14px; border-left:4px solid var(--accent);
           background:var(--soft); border-radius:0 12px 12px 0; padding:17px 22px; }}
  .band .t {{ font-size:18.5px; font-weight:600; white-space:nowrap; }}
  .band .d {{ font-size:17px; color:var(--muted); }}
  .band code {{ font-family:ui-monospace,Menlo,monospace; font-size:16.5px; color:var(--ink); }}

  .checkwrap {{ flex:1; display:flex; flex-direction:column; }}
  .checks {{ flex:1; display:grid; grid-template-columns:repeat(5,1fr); gap:15px; }}
  .chk {{ border:2px solid var(--line); border-radius:14px; padding:18px 18px; background:#fff;
          display:flex; flex-direction:column; gap:6px; }}
  .chk.first {{ border-color:var(--accent); background:var(--accent-soft); }}
  .chk.last  {{ border-color:var(--green);  background:var(--green-soft); }}
  .chk .n {{ width:31px; height:31px; border-radius:50%; background:var(--ink); color:#fff;
             font-size:16px; font-weight:700; display:flex; align-items:center; justify-content:center; }}
  .chk .t {{ font-size:20px; font-weight:650; }}
  .chk .d {{ font-size:16.5px; color:var(--muted); line-height:1.36; }}

  .rowhead {{ display:flex; align-items:baseline; gap:12px; }}
  .rowhead h2 {{ font-size:22px; letter-spacing:.01em; }}
  .rowhead span {{ font-size:17px; color:var(--muted); }}

  .ledger {{ display:flex; align-items:center; gap:14px; border:2px dashed var(--line);
             border-radius:14px; padding:17px 22px; }}
  .ledger .t {{ font-size:18.5px; font-weight:650; white-space:nowrap; }}
  .ledger .d {{ font-size:17px; color:var(--muted); }}
</style></head><body>

  <div class="pipe">
    <div class="node">
      <h3>Live call</h3>
      <div class="q">what arrives</div>
      <ul><li>PSTN, VoIP or mobile</li><li>7 codecs, packet loss</li><li>Hindi, Tamil, Telugu</li></ul>
    </div>
    {{ARROW1}}
    <div class="node lead">
      <h3>Listener</h3>
      <div class="q">is this voice synthetic?</div>
      <ul><li>Frozen 300M multilingual model</li>
          <li>{N_TRAIN} trained parameters</li>
          <li>Calibrated, so 0.8 means 8 in 10</li></ul>
    </div>
    {{ARROW2}}
    <div class="node">
      <h3>Gate</h3>
      <div class="q">do I know enough yet?</div>
      <ul><li>First verdict at {MIN_COMMIT} s</li>
          <li>Never inside the unsure zone</li>
          <li>Stable for 3 updates, then commits</li></ul>
    </div>
    {{ARROW3}}
    <div class="node end">
      <h3>Action</h3>
      <div class="q">what happens to the money</div>
      <ul><li>Held until verified</li><li>Never released by voice alone</li></ul>
    </div>
  </div>

  <div class="band">
    <div class="t">The unsure zone is measured, never typed</div>
    <div class="d">Derived per phone line from real speech at a {FPR} false-alarm budget:
      <code>{BAND_CLEAN}</code> on a clean line, <code>{BAND_WORST}</code> on G.723.1 at 6.3 kbps.</div>
  </div>

  <div class="checkwrap">
    <div class="rowhead" style="margin-bottom:15px">
      <h2>Five checks before money moves</h2>
      <span>each one needs less from the detector than the one before it</span>
    </div>
    <div class="checks">{{CHECKS}}</div>
  </div>

  <div class="ledger">
    <div class="t">Tamper-evident record</div>
    <div class="d">Every score, verdict, challenge and approval is a block in a SHA-256 chain.
      Alter any past block and every block after it stops verifying.</div>
  </div>

</body></html>"""


def arrow(label):
    return (f'<div class="arrow"><span class="lbl">{label}</span>'
            f'<svg width="64" height="12" viewBox="0 0 64 12">'
            f'<line x1="0" y1="6" x2="54" y2="6" stroke="#c9d2dd" stroke-width="1.6"/>'
            f'<path d="M54 1.5 L62 6 L54 10.5 Z" fill="#c9d2dd"/></svg></div>')


def main():
    checks = "".join(
        f'<div class="chk {"first" if i == 0 else "last" if i == len(CHECKS) - 1 else ""}">'
        f'<div class="n">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>'
        for i, (n, t, d) in enumerate(CHECKS))

    html = (HTML.replace("{ARROW1}", arrow("16 kHz audio"))
                .replace("{ARROW2}", arrow("score every 0.5 s"))
                .replace("{ARROW3}", arrow("commit or defer"))
                .replace("{CHECKS}", checks))

    WORK.mkdir(parents=True, exist_ok=True)
    page = WORK / "architecture.html"
    page.write_text(html)

    if not Path(CHROME).exists():
        sys.exit("Google Chrome not found; cannot render the diagram")
    subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        f"--screenshot={OUT}", f"--window-size={W},{H}",
        f"--force-device-scale-factor={SCALE}", "--default-background-color=FFFFFFFF",
        page.as_uri(),
    ], capture_output=True, text=True, check=False)

    if not OUT.exists():
        sys.exit("render produced no file")
    print(f"wrote {OUT.relative_to(ROOT)}  ({W * SCALE}x{H * SCALE})")


if __name__ == "__main__":
    main()
