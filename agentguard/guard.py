"""The guard: the interceptor between the agent and tool execution.

The agent never calls a tool directly — it calls `Guard.run_tool`, which is the
single choke point where policy, detection, and logging all apply.
"""
from .tools import Tool
from .policy import TaintState, evaluate, Decision
from .detector import detect_heuristic
from .logging_utils import log_tool_call


class Blocked(Exception):
    """Raised when the guard refuses a tool call."""


class Guard:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled          # flip off to get the "unguarded" baseline
        self.state = TaintState()

    def run_tool(self, tool: Tool, **kwargs) -> str:
        if not self.enabled:
            # Unguarded baseline: execute blindly. This is your "before".
            self.state.update_after(tool)
            return tool.func(**kwargs)

        # 1) Policy check BEFORE executing.
        decision = evaluate(tool, self.state)
        log_tool_call(tool.name, kwargs, decision.value)
        if decision is Decision.BLOCK:
            raise Blocked(f"Policy blocked '{tool.name}' (Rule of Two).")
        # TODO(you): handle Decision.ESCALATE (e.g., prompt for confirmation).

        # 2) Execute.
        result = tool.func(**kwargs)

        # 3) If the output is untrusted, scan it before it re-enters the context.
        if tool.reads_untrusted:
            det = detect_heuristic(result)
            log_tool_call(tool.name, kwargs, "scanned", det.reason)
            # TODO(you): decide what to do on a hit — strip, wrap, warn, or block.

        # 4) Update taint AFTER a successful read.
        self.state.update_after(tool)
        return result
