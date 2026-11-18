"""The Gate: sequential commit-or-defer on a calibrated, streaming risk score.

Three conditions must all hold before it commits:
  1. at least MIN_COMMIT_S of real audio (never tile-padded: short prefixes repeated to
     fill a window manufacture most of the apparent early-decision advantage);
  2. the calibrated probability is outside the undecidable band [tau_human, tau_clone];
  3. it has been stable across the last STABILITY_WINDOW updates.
A gate that says "not yet" survives a moment that a gate shouting FAKE at a customer does not.
"""
from collections import deque
from dataclasses import dataclass, asdict
from .config import MIN_COMMIT_S, STABILITY_WINDOW, STABILITY_TOL

DEFER = "DEFER"
SYNTHETIC = "SYNTHETIC"
HUMAN = "HUMAN"


@dataclass
class Decision:
    state: str
    p: float
    elapsed_s: float
    committed: bool
    reason: str
    stable: bool

    def to_dict(self):
        return asdict(self)


class Gate:
    def __init__(self, min_commit_s=MIN_COMMIT_S, window=STABILITY_WINDOW, tol=STABILITY_TOL):
        self.min_commit_s = min_commit_s
        self.window = window
        self.tol = tol
        self.history = deque(maxlen=window)
        self.committed = None

    def reset(self):
        self.history.clear()
        self.committed = None

    def update(self, p, elapsed_s, tau_clone, tau_human):
        p = float(p)
        self.history.append(p)
        stable = len(self.history) == self.window and (max(self.history) - min(self.history)) <= self.tol
        if self.committed is not None:
            return Decision(self.committed, p, elapsed_s, True, "committed; the gate does not flip-flop", stable)
        if elapsed_s < self.min_commit_s:
            return Decision(DEFER, p, elapsed_s, False,
                            f"{elapsed_s:.1f}s of audio; no decision below {self.min_commit_s:.1f}s", stable)
        if not stable:
            return Decision(DEFER, p, elapsed_s, False,
                            f"score not yet settled across {self.window} updates", stable)
        if p >= tau_clone:
            self.committed = SYNTHETIC
            return Decision(SYNTHETIC, p, elapsed_s, True,
                            f"P(synthetic) {p:.3f} held above {tau_clone:.3f} for {self.window} updates", stable)
        if p <= tau_human:
            self.committed = HUMAN
            return Decision(HUMAN, p, elapsed_s, True,
                            f"P(synthetic) {p:.3f} held below {tau_human:.3f} for {self.window} updates", stable)
        return Decision(DEFER, p, elapsed_s, False,
                        f"P(synthetic) {p:.3f} inside the undecidable band [{tau_human:.3f}, {tau_clone:.3f}]", stable)
