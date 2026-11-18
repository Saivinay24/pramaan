"""The Warrant: the authorization check, and the "and Prevention" half of the PS title.

A legitimate disclosed voice agent, a bank's own IVR or an insurer's outbound bot, is
synthetic on purpose. Detecting it as synthetic is correct and useless. The question that
matters for a high-value action is whether it is AUTHORIZED, which is a different question
from whether it is synthetic, and it is the question the passive detector cannot answer.

The reframe is not ours and the deck says so: C2PA AI Disclosure, STIR/SHAKEN attestation
levels, SASV fusion, MerkleSpeech.

THE LOAD-BEARING RULE, enforced by the assert in apply() and not merely documented:

    A WARRANT MAY ONLY EVER LOWER RISK, NEVER RAISE IT.

Ported from the parent repo's src/kempelen/warrant.py, which carries the same assert. The
rule exists because every audio-provenance signal available in 2026 is forgeable in BOTH
directions, and the literature has got worse since AudioMarkBench, not better:

  AudioMarkBench, NeurIPS 2024            all three SOTA schemes fail under removal and
                                          forgery attack
  SoK, arXiv 2503.19176                   bit recovery below 0.6 under pitch shift for every
                                          scheme tested, AudioSeal included
  Learning to Evade, arXiv 2606.22310     learned removal at high perceptual quality
  How Fragile Is Your Watermark,
  arXiv 2608.16566                        training-free structural removal
  The Watermark Shortcut, arXiv 2606.23335  a watermark can be STAMPED ONTO A GENUINE
                                          RECORDING. This is the forgery direction, not the
                                          removal direction, and it is the one that decides
                                          the sign of this rule.

Read those two directions against the rule:

  removal  an attacker strips a warrant off audio that had one. Under the monotone rule the
           audio loses a discount it would have had. The risk score is unchanged or higher,
           which is the safe direction.
  forgery  an attacker stamps a warrant onto audio that never had one. Under the monotone
           rule the best that buys them is a LOWER risk on a call, and lower risk still does
           not clear a high-value action, because the device factor is mandatory and does not
           consult this module at all.

A forgeable signal that could RAISE risk is a weapon handed to the attacker: forge an invalid
warrant onto a genuine customer and get them blocked. A forgeable signal that can only LOWER
risk costs an attacker nothing to forge and gains them nothing they did not already have.
That asymmetry is the entire design, and it is why the rule is stated as monotone rather than
as "we trust watermarks".

WHAT THIS MODULE DELIBERATELY DOES NOT DO. It does not embed or detect an audio watermark.
The parent repo's version loads AudioSeal to recover a payload from the signal itself; that
is a torch model and a new dependency in a pinned py3.14 stack, so it is not ported here. The
token path below is what Pramaan ships, the docs say so, and nothing outward claims a
watermark detector runs in this repo.
"""

NONE = "none"
PRESENT_VALID = "attested"
PRESENT_INVALID = "invalid"

# How much a valid warrant may lower risk. A fraction, never a jump to zero: an attested
# agent is still an agent, and the operator still sees a synthetic verdict.
MAX_RISK_REDUCTION = 0.5

# The registry of agents allowed to disclose themselves. The payload is an INDEX INTO A
# REGISTRY, never a secret and never a credential. An unregistered code is PRESENT_INVALID,
# which under the monotone rule costs the caller nothing beyond losing the discount.
AGENT_REGISTRY = {
    "bank-ivr-01": 0xA31C,
    "insurer-bot-07": 0x5E42,
    "telecom-support-agent": 0x1F90,
}


class WarrantCheck:
    __slots__ = ("status", "detail", "agent_id")

    def __init__(self, status, detail, agent_id=None):
        self.status = status
        self.detail = detail
        self.agent_id = agent_id

    def to_dict(self):
        return dict(status=self.status, detail=self.detail, agent_id=self.agent_id)


def check(attestation):
    """`attestation` is whatever the channel carried, or None.

    A real deployment plugs a STIR/SHAKEN attestation level or a C2PA manifest in here. For
    the demo it is a signed token. Absent is the normal case: almost every genuine human call
    carries no attestation at all, which is exactly why absence is never penalised.
    """
    if not attestation:
        return WarrantCheck(NONE, "no attestation on this channel")
    agent = attestation.get("agent_id")
    if attestation.get("valid") is True and agent in AGENT_REGISTRY:
        return WarrantCheck(PRESENT_VALID, f"disclosed AI agent {agent}, signature verified",
                            agent_id=agent)
    if attestation.get("valid") is True:
        return WarrantCheck(PRESENT_INVALID,
                            f"attestation verified but {agent!r} is in no registry. "
                            f"No discount, and no penalty either.")
    return WarrantCheck(PRESENT_INVALID, "attestation present but did not verify")


def apply(p_clone, warrant_status):
    """Adjust calibrated risk given a warrant. MONOTONE GUARANTEE: never increases p.

    A valid warrant lowers the ACTIONABLE risk while the synthetic verdict itself stands
    unchanged. Invalid or absent changes nothing: a missing warrant is not evidence of an
    attack, it is the ordinary state of a human phone call.
    """
    p = float(p_clone)
    adjusted = p * (1.0 - MAX_RISK_REDUCTION) if warrant_status == PRESENT_VALID else p
    assert adjusted <= p + 1e-9, "INVARIANT VIOLATED: a warrant raised risk"
    return adjusted
