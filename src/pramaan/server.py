"""Pramaan operator console server. One command, fully offline.

    .venv/bin/python -m pramaan.server         ->  http://127.0.0.1:8770

Two audio sources, both through the SAME live pipeline chunk by chunk in real time:
the laptop microphone, or a bundled sample whose true origin is always displayed.
"""
import asyncio, glob, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from pramaan.config import SR, HOP_S, MIN_COMMIT_S
from pramaan.stream import CallSession
from pramaan.channels import GRID, apply_channel, UNAVAILABLE
from pramaan.ledger import Ledger

UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")
SAMPLES = os.path.join(ROOT, "data", "samples")
app = FastAPI(title="Pramaan")
SESSIONS = {}
_FE = None


def frontend():
    global _FE
    if _FE is None:
        from pramaan.frontend import Frontend
        _FE = Frontend()
    return _FE


@app.get("/")
def index():
    return HTMLResponse(open(os.path.join(UI, "index.html"), encoding="utf-8").read())


@app.get("/api/results")
def results():
    p = os.path.join(ROOT, "eval", "results.json")
    return JSONResponse(json.load(open(p)) if os.path.exists(p) else {"error": "no results yet"})


@app.get("/api/latency")
def latency():
    p = os.path.join(ROOT, "eval", "results", "latency.json")
    return JSONResponse(json.load(open(p)) if os.path.exists(p) else {})


@app.get("/api/samples")
def samples():
    out = []
    for p in sorted(glob.glob(os.path.join(SAMPLES, "*.wav"))):
        meta = os.path.splitext(p)[0] + ".json"
        m = json.load(open(meta, encoding="utf-8")) if os.path.exists(meta) else {}
        out.append(dict(file=os.path.basename(p), **m))
    return JSONResponse(dict(samples=out, conditions=GRID, unavailable=UNAVAILABLE,
                             hop_s=HOP_S, min_commit_s=MIN_COMMIT_S))


@app.get("/api/sample/{name}")
def sample_audio(name: str):
    return FileResponse(os.path.join(SAMPLES, os.path.basename(name)))


@app.get("/api/about")
def about():
    """Everything the console would otherwise have to hardcode about this build.

    The operator surface never shows any of this; the About panel does, and it reads it
    from here so that no version string in the UI can drift from the running process.
    """
    from pramaan.config import (SSL_MODEL, SSL_LAYER, DEVICE, DTYPE, MAX_CONTEXT_S,
                                STABILITY_WINDOW, STABILITY_TOL, CHALLENGE_AFTER_S,
                                CHALLENGE_DEADLINE_S)
    from pramaan.model import load_bundle
    from pramaan import challenge as chal
    info = dict(model=SSL_MODEL, layer=SSL_LAYER, device=DEVICE, dtype=DTYPE,
                sample_rate=SR, hop_s=HOP_S, min_commit_s=MIN_COMMIT_S,
                max_context_s=MAX_CONTEXT_S, stability_window=STABILITY_WINDOW,
                stability_tol=STABILITY_TOL, challenge_after_s=CHALLENGE_AFTER_S,
                challenge_deadline_s=CHALLENGE_DEADLINE_S,
                challenge_space=chal.space_size("hindi"),
                conditions=GRID, unavailable=UNAVAILABLE)
    try:
        B = load_bundle(os.path.join(ROOT, "eval", "results", "model.pkl"))
        rp = os.path.join(ROOT, "eval", "results.json")
        ship = (json.load(open(rp)).get("ship") or {}) if os.path.exists(rp) else {}
        info.update(n_trainable=ship.get("n_trainable"),
                    generators=B.get("generators", []),
                    band_scope=B.get("band_scope"),
                    fallback_channel=B.get("fallback_channel"),
                    band_by_channel=sorted((B.get("band_by_channel") or {}).keys()))
    except Exception as e:
        info["bundle_error"] = f"{type(e).__name__}: {e}"
    return JSONResponse(info)


@app.get("/api/runs")
def runs():
    """Every call this machine has on record, newest first.

    The audit view needs a call list; without one a compliance officer can only ever see
    the call that happens to be in memory. Live sessions are flagged so the view can say
    which chain is still growing.
    """
    out = []
    for run_id, s in SESSIONS.items():
        out.append(dict(run_id=run_id, live=not getattr(s, "closed", False), blocks=len(s.ledger.blocks),
                        caller=(s.caller or {}).get("name"), action=s.action or {},
                        transaction=s.transaction, channel=s.channel,
                        opened_ts=s.ledger.blocks[0]["ts"] if s.ledger.blocks else None))
    seen = {r["run_id"] for r in out}
    for p in glob.glob(os.path.join(ROOT, "runs", "call-*.json")):
        run_id = os.path.splitext(os.path.basename(p))[0]
        if run_id in seen:
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
            blocks = d.get("ledger", {}).get("blocks", [])
            out.append(dict(run_id=run_id, live=False, blocks=len(blocks),
                            caller=(d.get("caller") or {}).get("name"),
                            action=d.get("action") or {},
                            transaction=d.get("transaction"),
                            channel=(blocks[0]["data"].get("channel") if blocks else None),
                            opened_ts=blocks[0]["ts"] if blocks else None))
        except Exception:
            continue
    out.sort(key=lambda r: (r["opened_ts"] or 0), reverse=True)
    return JSONResponse(dict(runs=out))


@app.get("/api/ledger/{run_id}")
def ledger(run_id: str):
    s = SESSIONS.get(run_id)
    if s:
        L = s.ledger.to_dict(); L["verify"] = Ledger.verify(L["blocks"]); return JSONResponse(L)
    p = os.path.join(ROOT, "runs", f"{run_id}.json")
    if os.path.exists(p):
        L = json.load(open(p))["ledger"]; L["verify"] = Ledger.verify(L["blocks"]); return JSONResponse(L)
    return JSONResponse({"error": "unknown run"}, status_code=404)


@app.post("/api/ledger/verify")
async def ledger_verify(payload: dict):
    return JSONResponse(Ledger.verify(payload.get("blocks", [])))


@app.post("/api/call/{run_id}/action")
async def call_action(run_id: str, payload: dict):
    s = SESSIONS.get(run_id)
    if not s:
        return JSONResponse({"error": "unknown run"}, status_code=404)
    a = payload.get("action")
    if a == "challenge":
        r = s.issue_challenge().to_dict()
    elif a == "oob_send":
        r = s.send_oob(payload.get("device", "registered device"))
    elif a == "oob_resolve":
        r = s.resolve_oob(bool(payload.get("approved")))
    elif a == "callback":
        # Step 4 of the ladder. It does not decide the transaction; it records that the
        # operator chose to verify out of band on the number already on file, which is
        # the step a bank takes when the device push is not answered.
        r = dict(callback=s.request_callback(payload.get("note")))
    elif a in ("block", "clear"):
        r = dict(transaction=s.operator(a))
    else:
        return JSONResponse({"error": "unknown action"}, status_code=400)
    return JSONResponse(dict(result=r, transaction=s.transaction, ledger_len=len(s.ledger.blocks),
                             ledger_head=s.ledger.blocks[-1]["hash"][:16]))


def _start_msg(sess, mode, source, cond, duration=None):
    return {"type": "start", "run_id": sess.run_id, "mode": mode, "source": source,
            "condition": cond, "duration_s": duration, "min_commit_s": MIN_COMMIT_S,
            "hop_s": HOP_S, "generators": sess.generators}


@app.websocket("/ws/file")
async def ws_file(ws: WebSocket):
    await ws.accept()
    sess = None
    try:
        req = json.loads(await ws.receive_text())
        import soundfile as sf
        path = os.path.join(SAMPLES, os.path.basename(req["file"]))
        wav, sr = sf.read(path, dtype="float32")
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        cond = req.get("condition", "clean")
        if cond != "clean":
            wav = apply_channel(wav, cond, sr=SR)
        sess = CallSession(frontend(), language=req.get("language", "hindi"), caller=req.get("caller"),
                           action=req.get("action"), channel=cond, seed=req.get("seed"))
        SESSIONS[sess.run_id] = sess
        await ws.send_json(_start_msg(sess, "bundled sample through the live pipeline",
                                      os.path.basename(path), cond, round(len(wav) / SR, 2)))
        hop = int(HOP_S * SR)
        loop = asyncio.get_event_loop()
        for i in range(0, len(wav), hop):
            await asyncio.sleep(HOP_S)
            rec = await loop.run_in_executor(None, sess.push, wav[i:i + hop])
            if rec:
                await ws.send_json({"type": "update", **rec})
        sess.closed = True
        await ws.send_json({"type": "end", "trace_file": sess.save(), "transaction": sess.transaction})
        # keep the socket open so the operator can still act on the call
        while True:
            msg = await ws.receive_text()
            if msg == "close":
                break
    except WebSocketDisconnect:
        if sess:
            sess.closed = True
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "detail": f"{type(e).__name__}: {e}"})
        except Exception:
            pass


@app.websocket("/ws/mic")
async def ws_mic(ws: WebSocket):
    await ws.accept()
    sess = None
    try:
        req = json.loads(await ws.receive_text())
        cond = req.get("condition", "clean")
        sess = CallSession(frontend(), language=req.get("language", "hindi"), caller=req.get("caller"),
                           action=req.get("action"), channel=cond, seed=req.get("seed"))
        SESSIONS[sess.run_id] = sess
        await ws.send_json(_start_msg(sess, "live microphone", "microphone", cond))
        loop = asyncio.get_event_loop()
        pending = np.zeros(0, np.float32)
        while True:
            data = await ws.receive_bytes()
            x = np.frombuffer(data, dtype=np.float32)
            if cond != "clean":
                pending = np.concatenate([pending, x])
                if len(pending) < int(HOP_S * SR):
                    continue
                x, pending = apply_channel(pending, cond, sr=SR), np.zeros(0, np.float32)
            rec = await loop.run_in_executor(None, sess.push, x)
            if rec:
                await ws.send_json({"type": "update", **rec})
    except WebSocketDisconnect:
        if sess:
            sess.closed = True
            sess.save()
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "detail": f"{type(e).__name__}: {e}"})
        except Exception:
            pass


if os.path.isdir(UI):
    app.mount("/static", StaticFiles(directory=UI), name="static")

if __name__ == "__main__":
    import uvicorn
    frontend()
    uvicorn.run(app, host="127.0.0.1", port=8770, log_level="warning")
