"""Tamper-evident audit ledger: a SHA-256 hash chain of every decision on a call.

Every event on a monitored call (score update, gate commit, challenge issued, out-of-band
approval, operator action) is appended as a block whose hash covers the previous block's
hash. Editing or deleting any past event breaks every hash after it. This is the
"blockchain" half of the theme done honestly: an append-only, verifiable chain that a bank
can anchor to its own ledger or a public chain later, not a token.
"""
import hashlib, json, time


def _digest(prev_hash, block):
    body = json.dumps(block, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((prev_hash + body).encode("utf-8")).hexdigest()


class Ledger:
    GENESIS = "0" * 64

    def __init__(self, run_id):
        self.run_id = run_id
        self.blocks = []

    def append(self, event, **data):
        prev = self.blocks[-1]["hash"] if self.blocks else self.GENESIS
        block = dict(index=len(self.blocks), run_id=self.run_id, ts=time.time(),
                     event=event, data=data, prev_hash=prev)
        block["hash"] = _digest(prev, {k: v for k, v in block.items() if k != "hash"})
        self.blocks.append(block)
        return block

    @staticmethod
    def verify(blocks):
        prev = Ledger.GENESIS
        for i, b in enumerate(blocks):
            body = {k: v for k, v in b.items() if k != "hash"}
            if b["index"] != i or b["prev_hash"] != prev or _digest(prev, body) != b["hash"]:
                return dict(valid=False, broken_at=i)
            prev = b["hash"]
        return dict(valid=True, length=len(blocks), head=prev)

    def to_dict(self):
        return dict(run_id=self.run_id, blocks=self.blocks, head=self.blocks[-1]["hash"] if self.blocks else self.GENESIS)
