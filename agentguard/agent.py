"""The agent loop and its interchangeable "planners"

A *planner* decides the next tool call given the conversation so far
  - ScriptedPlanner: deterministic, offline. It emits a fixed sequence of
    tool calls — exactly what a successfully-injected LLM would produce. This is
    the default for tests, benchmarks, and the reproducible demo, because the
    artifact under evaluation is the GUARD, not the model.
  - LLMPlanner: drives the loop with a real Anthropic model. Optional; needs an
    API key.

Either way, the agent NEVER executes a tool directly — every call goes through
Guard.run_tool, the single choke point.
"""
from dataclasses import dataclass
from .tools import TOOLS
from .guard import Guard, Blocked
from typing import Optional, Protocol

@dataclass
class ToolCall:
    name: str
    input: dict

class Planner(Protocol):
    def next_call(self, transcript: list[dict]) -> Optional[ToolCall]:
        ...

class ScriptedPlanner:
    def __init__(self, calls: list[ToolCall]):
        self._calls = list(calls)
        self._i = 0
    def next_call(self, transcript: list[dict]) -> Optional[ToolCall]:
        if self._i >= len(self._calls):
            return None
        call = self._calls[self._i]
        self._i += 1
        return call
    
def run_agent(planner: Planner, guard: Guard, max_steps: int = 6) -> dict:
    """Drive the planner/guard loop and return a structured trace.

    Returns:
        {
          "steps": [ {name, input, status, detail}, ... ],
          "sent": [ messages that reached the external `send` tool ],
          "blocked": bool,   # whether the guard blocked at least one call
        }
    """
    transcript: list[dict] = []
    steps: list[dict] = []
    sent: list[str] = []
    blocked = False
    last_secret = None
    for _ in range(max_steps):
        call = planner.next_call(transcript)
        if call is None:
            break
        if call.name not in TOOLS:
            steps.append({"name": call.name, "input": call.input,
                          "status": "unknown_tool", "detail": ""})
            continue
        
        tool = TOOLS[call.name]
        # Let a scripted plan reference a secret captured earlier in the run.
        args = dict(call.input)
        if "message" in args and last_secret and "{secret}" in str(args["message"]):
            args["message"] = args["message"].replace("{secret}", last_secret)

        try:
            result = guard.run_tool(tool, **args)
            status, detail = "ok", result
            if tool.sensitive_data:
                last_secret = result
            if tool.external_effect:
                sent.append(args.get("message", ""))
        except Blocked as e:
            blocked = True
            status, detail = "blocked", str(e)
            result = f"BLOCKED: {e}"

        steps.append({"name": call.name, "input": args, "status": status, "detail": detail})
        transcript.append({"role": "tool", "name": call.name, "content": str(result)})    

    return {"steps": steps, "sent": sent, "blocked": blocked}


def _llm_step(messages, tool_specs):
    """Return (assistant_text, tool_call_or_None).

    TODO: wire this with the Anthropic SDK:
        from anthropic import Anthropic
        client = Anthropic()
        resp = client.messages.create(
            model="claude-...", max_tokens=1024,
            messages=messages, tools=tool_specs)
        # parse resp.content for a tool_use block; return its name+input
    """
    raise NotImplementedError("Wire up LLM provider here")
