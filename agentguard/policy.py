"""The policy engine: Rule-of-Two / lethal-trifecta enforcement.

The guard maintains a `TaintState` for the
current agent run and asks the policy whether the next tool call is allowed.

Security property (see THREAT_MODEL.md):
    No single agent run may simultaneously (a) have ingested untrusted content,
    (b) have accessed sensitive data, and (c) cause an external effect.

The policy is *content-blind*: it never inspects tool arguments or text. It
reasons only about which of the three properties the run has accumulated and
which the candidate call would add. That is what makes it perform well against prompt
injection regardless of how cleverly a payload is encoded.
"""
from dataclasses import dataclass
from enum import Enum
from .tools import Tool

class Decision(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"   # requires human confirmation instead of hard-blocking

@dataclass
class PolicyResult:
    """A decision plus a human-readable rationale (for logging / auditing)."""
    decision: "Decision"
    reason: str

@dataclass
class TaintState:
    """Tracks which dangerous properties the run has accumulated so far.

    `external_effect` is intentionally NOT accumulated: an external effect is
    only dangerous in combination with the current run's prior taint, so it
    is evaluated per-call rather than remembered.
    """
    ingested_untrusted: bool = False
    accessed_sensitive: bool = False

    def update_after(self, tool: Tool) -> None:
        """Fold a successfully-executed tool's taint into the run state."""
        if tool.reads_untrusted:
            self.ingested_untrusted = True
        if tool.sensitive_data:
            self.accessed_sensitive = True

def evaluate(tool: Tool, state: TaintState, escalate: bool = False) -> "PolicyResult":
    """Decide whether `tool` may run given what the run has done so far.

    Compute the three properties as they would stand if this call ran,
    combining the run's accumulated taint with the candidate tool's own tags:
        untrusted = state.ingested_untrusted OR tool.reads_untrusted
        sensitive = state.accessed_sensitive OR tool.sensitive_data
        external  = tool.external_effect
    If all three hold, the call would complete the forbidden trifecta -> deny.
    Otherwise (two or fewer) -> allow.

    `escalate=True` returns ESCALATE instead of BLOCK, modelling a deployment
    that asks a human to confirm rather than hard-failing.
    """
    untrusted = state.ingested_untrusted or tool.reads_untrusted
    sensitive = state.accessed_sensitive or tool.sensitive_data
    external = tool.external_effect

    if untrusted and sensitive and external:
        verdict = Decision.ESCALATE if escalate else Decision.BLOCK
        return PolicyResult(
            verdict,
            (f"Rule of Two violated: this '{tool.name}' call would combine "
             f"untrusted input + sensitive data + external effect in one run."),
        )

    # Safe: report which (at most two) properties, for the log.
    active = [name for name, on in
              (("untrusted", untrusted), ("sensitive", sensitive), ("external", external)) if on]
    summary = ", ".join(active) if active else "no risky properties"
    return PolicyResult(Decision.ALLOW, f"Allowed ({summary}; at most two of three).")
