"""The policy engine: Rule-of-Two / lethal-trifecta enforcement.

This is the heart of the project and the part you implement. The guard maintains
a `TaintState` for the current agent run and asks the policy whether the next
tool call is allowed.
"""
from dataclasses import dataclass
from enum import Enum
from .tools import Tool


class Decision(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"   # e.g., require human confirmation


@dataclass
class TaintState:
    """Tracks which of the three dangerous properties the run has accumulated."""
    ingested_untrusted: bool = False
    accessed_sensitive: bool = False
    # external_effect is evaluated per-call, not accumulated

    def update_after(self, tool: Tool) -> None:
        if tool.reads_untrusted:
            self.ingested_untrusted = True
        if tool.sensitive_data:
            self.accessed_sensitive = True


def evaluate(tool: Tool, state: TaintState) -> Decision:
    """Decide whether `tool` may run given what the run has done so far.

    The security property (see THREAT_MODEL.md):
        never allow untrusted-input AND sensitive-data AND external-effect
        within the same run.

    TODO(you): implement the Rule of Two.
      - Count how many of the three properties WOULD be true if this call ran:
            untrusted = state.ingested_untrusted or tool.reads_untrusted
            sensitive = state.accessed_sensitive or tool.sensitive_data
            external  = tool.external_effect
      - If all three -> Decision.BLOCK (or ESCALATE for human review).
      - Otherwise -> Decision.ALLOW.
      - Stretch: make this configurable (block vs escalate), and log *why*.
    """
    raise NotImplementedError("Implement the Rule of Two here (Day 3).")
