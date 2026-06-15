"""The guard: the interceptor between the agent and tool execution.

The agent never calls a tool directly — it calls `Guard.run_tool`, the point where
policy, detection, and logging all apply. The order matters:
the policy check happens BEFORE the tool runs, so a blocked call never executes.
"""
from .tools import Tool
from .policy import TaintState, evaluate, Decision
from .detector import detect_heuristic
from .logging_utils import log_tool_call

class Blocked(Exception):
    """Raised when the guard refuses a tool call."""

class Guard:
    def __init__(self, enabled: bool = True, escalate: bool = False):
        self.enabled = enabled        # flip off to get the "unguarded" baseline
        self.escalate = escalate      # ESCALATE instead of BLOCK on a violation
        self.state = TaintState()

    def run_tool(self, tool: Tool, **kwargs) -> str:
        if not self.enabled:
            # Unguarded baseline: execute blindly. This is the "before".
            self.state.update_after(tool)
            return tool.func(**kwargs)

        # 1) Policy check BEFORE executing. Content-blind; cannot be injected.
        result = evaluate(tool, self.state, escalate=self.escalate)
        log_tool_call(tool.name, kwargs, result.decision.value, result.reason)
        if result.decision is Decision.BLOCK:
            raise Blocked(result.reason)
        if result.decision is Decision.ESCALATE:
            # In a real deployment this would prompt a human. For a reproducible
            # demo escalation is treated as a block (deny-by-default on no human).
            raise Blocked(f"[escalated, no approver] {result.reason}")

        # 2) Execute
        out = tool.func(**kwargs)

        # 3) Defense in depth: scan untrusted output before it re-enters context.
        if tool.reads_untrusted:
            det = detect_heuristic(out)
            log_tool_call(tool.name, kwargs, "scanned",
                          f"detector score={det.score} ({det.reason})")

        # 4) Update run taint AFTER a successful read/access.
        self.state.update_after(tool)
        return out
