"""One monitored call: audio in as a growing prefix, a decision out every hop.

Everything the operator sees comes from here: the calibrated running risk score, the
Gate's state, the challenge lifecycle, the out-of-band approval, and the hash-chained
ledger that records all of it.
"""
import json, os, random, time, uuid
import numpy as np

from .config import (SR, HOP_S, MAX_CONTEXT_S, MIN_COMMIT_S, CHALLENGE_AFTER_S,
                     CHALLENGE_DEADLINE_S)
from .model import load_bundle
from .gate import Gate, DEFER, SYNTHETIC, HUMAN
from .ledger import Ledger
from . import challenge as chal
from . import warrant as wrt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL = os.path.join(ROOT, "eval", "results", "model.pkl")
RUNS = os.path.join(ROOT, "runs")

# verification ladder states
HELD, CLEARED, BLOCKED = "HELD", "CLEARED", "BLOCKED"


class CallSession:
    def __init__(self, frontend, run_id=None, language="hindi", caller=None, action=None,
                 channel="clean", seed=None, attestation=None):
        B = load_bundle(MODEL)
        self.head, self.cals = B["head"], B["calibrators"]
        # The commit band is per channel. Genuine speech scores higher the harder the codec
        # squeezes it (eval/experiments.py, streaming.band_by_channel), so one band across
        # all seven lines either cries wolf on a 6.3 kbps call or goes deaf on a clean one.
        # A channel the bundle has no band for falls back to the most degrading condition
        # measured, never to clean.
        by_channel = B.get("band_by_channel") or {}
        fallback = B.get("fallback_channel") or "clean"
        self.band_channel = channel if channel in by_channel else fallback
        self.band = by_channel.get(self.band_channel) or B["band"]
        self.band_derived_for = self.band_channel if by_channel else "clean"
        self.prefixes = sorted(self.cals)
        self.generators = B.get("generators", [])
        self.fe = frontend
        self.gate = Gate()
        self.run_id = run_id or f"call-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:5]}"
        self.buf = np.zeros(0, np.float32)
        self.trace = []
        self.language = language
        self.channel = channel
        self.caller = caller or {}
        self.action = action or {}
        self.ledger = Ledger(self.run_id)
        self.rng = random.Random(seed)
        self.transaction = HELD
        self.challenge = None
        self._challenge_mark = None
        self._defer_since = None
        self.oob = None
        self.callback = None
        self.closed = False
        self.acoustic = None
        # The authorization layer. A disclosed voice agent is synthetic on purpose, so the
        # question for a high-value action is whether it is authorized, not whether it is
        # synthetic. `attestation` is None on every demo call and on every ordinary human
        # call, and warrant.apply() is the identity function in that case, by construction.
        # The rule it enforces with an assert is that a warrant may only ever LOWER risk,
        # which is what makes a forgeable signal safe to consult at all.
        self.warrant = wrt.check(attestation)
        self.latency_ms = []
        os.makedirs(RUNS, exist_ok=True)
        self.ledger.append("call_opened", caller=self.caller, action=self.action,
                           channel=channel, band_derived_for=self.band_channel,
                           language=language, model_generators=self.generators)

    # ------------------------------------------------------------- helpers
    @property
    def elapsed_s(self):
        return len(self.buf) / SR

    def _nearest(self, d, t):
        return d[min(d, key=lambda k: abs(float(k) - t))]

    def _score(self, wav):
        t0 = time.perf_counter()
        emb = self.fe.embed(wav)
        raw = float(self.head.decision_function(emb[None])[0])
        dur = min(len(wav) / SR, max(self.prefixes))
        p = float(self._nearest(self.cals, dur).predict_proba([raw])[0])
        self.latency_ms.append((time.perf_counter() - t0) * 1000)
        return raw, p

    # ------------------------------------------------------------- audio in
    def push(self, chunk):
        self.buf = np.concatenate([self.buf, np.asarray(chunk, np.float32)])
        t = self.elapsed_s
        if int(t / HOP_S) <= len(self.trace) or t < 0.5:
            return None
        return self.step()

    def step(self):
        t = self.elapsed_s
        window = self.buf[-int(MAX_CONTEXT_S * SR):]
        raw, p = self._score(window)
        p_passive = p
        p = wrt.apply(p, self.warrant.status)      # monotone: never raises p
        band = self._nearest(self.band, min(t, max(self.prefixes)))
        d = self.gate.update(p, t, band["tau_clone"], band["tau_human"])
        rec = d.to_dict()
        rec.update(run_id=self.run_id, t=round(t, 2), raw=raw, tau_clone=band["tau_clone"],
                   tau_human=band["tau_human"], band_channel=self.band_channel,
                   latency_ms=round(self.latency_ms[-1], 1),
                   min_commit_s=MIN_COMMIT_S, transaction=self.transaction, event=None,
                   p_passive=round(p_passive, 4), warrant=self.warrant.to_dict())

        if d.committed and len(self.trace) and not self.trace[-1]["committed"]:
            self.ledger.append("gate_committed", state=d.state, p=round(p, 4), t=round(t, 2),
                               reason=d.reason)
            rec["event"] = "committed"
            if d.state == SYNTHETIC:
                self._set_transaction(BLOCKED, "passive detector committed SYNTHETIC")
            elif d.state == HUMAN:
                # Policy: a passive acoustic pass never clears a high-value action on its
                # own. Voice is one factor; the registered device is the last one.
                self.acoustic = "passed"
                self.ledger.append("acoustic_pass", note="fraud hold lifted; out-of-band approval still required")
        elif len(self.trace) % 4 == 0:
            self.ledger.append("score", p=round(p, 4), t=round(t, 2), state=d.state)

        # challenge lifecycle: ask instead of shrugging
        if d.state == DEFER and not d.committed and t >= MIN_COMMIT_S:
            self._defer_since = self._defer_since if self._defer_since is not None else t
            if self.challenge is None and (t - self._defer_since) >= CHALLENGE_AFTER_S:
                self.issue_challenge(t)
                rec["event"] = "challenge_issued"
        else:
            self._defer_since = None
        if self.challenge and self.challenge.state == "ISSUED":
            resp_s = (len(self.buf) - self._challenge_mark) / SR
            if resp_s >= MIN_COMMIT_S + 0.5:
                self.answer_challenge(t)
                rec["event"] = "challenge_answered"
            elif t > self.challenge.deadline_s:
                self.challenge.state = "TIMEOUT"
                self.ledger.append("challenge_timeout", challenge_id=self.challenge.challenge_id)
                rec["event"] = "challenge_timeout"
        rec["challenge"] = self.challenge.to_dict() if self.challenge else None
        rec["oob"] = self.oob
        rec["callback"] = self.callback
        rec["acoustic"] = self.acoustic
        rec["transaction"] = self.transaction
        rec["ledger_head"] = self.ledger.blocks[-1]["hash"][:16]
        rec["ledger_len"] = len(self.ledger.blocks)
        self.trace.append(rec)
        return rec

    # ------------------------------------------------------------- prevention
    def _set_transaction(self, state, why):
        if self.transaction != state:
            self.transaction = state
            self.ledger.append("transaction_" + state.lower(), why=why)

    def issue_challenge(self, t=None):
        t = self.elapsed_s if t is None else t
        self.challenge = chal.draw(self.language, now_s=t, deadline_s=CHALLENGE_DEADLINE_S, rng=self.rng)
        self._challenge_mark = len(self.buf)
        self.ledger.append("challenge_issued", challenge_id=self.challenge.challenge_id,
                           text=self.challenge.text, space=chal.space_size(self.language))
        return self.challenge

    def answer_challenge(self, t=None):
        c = self.challenge
        resp = self.buf[self._challenge_mark:]
        raw, p = self._score(resp)
        c.p_response = p
        band = self._nearest(self.band, min(len(resp) / SR, max(self.prefixes)))
        if p >= band["tau_clone"]:
            c.verdict = SYNTHETIC; self._set_transaction(BLOCKED, "challenge response scored synthetic")
        elif p <= band["tau_human"]:
            c.verdict = HUMAN; self.acoustic = "passed"
        else:
            c.verdict = "ESCALATE"
        c.state = "ANSWERED"
        self.ledger.append("challenge_answered", challenge_id=c.challenge_id, p_response=round(p, 4),
                           verdict=c.verdict)
        return c

    def send_oob(self, device="registered device"):
        code = f"{self.rng.randrange(10**6):06d}"
        self.oob = dict(state="PENDING", code=code, device=device, sent_at=round(self.elapsed_s, 2))
        self.ledger.append("oob_sent", device=device, code_digest=chal.hashlib.sha256(code.encode()).hexdigest()[:16])
        return self.oob

    def resolve_oob(self, approved: bool):
        if not self.oob:
            return None
        self.oob["state"] = "APPROVED" if approved else "DENIED"
        self.ledger.append("oob_resolved", state=self.oob["state"])
        self._set_transaction(CLEARED if approved else BLOCKED,
                              "out-of-band approval " + self.oob["state"].lower())
        return self.oob

    def request_callback(self, note=None):
        """Step 4: verify out of band on the number already on file.

        It deliberately does not move the transaction. A callback is a step the operator
        takes, not a verdict, and the ledger records it as such so the audit trail shows
        what was tried before the decision.
        """
        self.callback = dict(state="REQUESTED", at_s=round(self.elapsed_s, 2),
                             note=note or "callback on the number on record")
        self.ledger.append("callback_requested", note=self.callback["note"],
                           t=self.callback["at_s"])
        return self.callback

    def operator(self, decision):
        self._set_transaction(BLOCKED if decision == "block" else CLEARED, f"operator: {decision}")
        return self.transaction

    def save(self):
        p = os.path.join(RUNS, f"{self.run_id}.json")
        json.dump(dict(run_id=self.run_id, caller=self.caller, action=self.action,
                       transaction=self.transaction, trace=self.trace,
                       ledger=self.ledger.to_dict(),
                       median_latency_ms=float(np.median(self.latency_ms)) if self.latency_ms else None),
                  open(p, "w"), indent=1, ensure_ascii=False)
        return p
