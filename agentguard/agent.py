"""Minimal tool-using agent loop.

The LLM call is isolated in `_llm_step` so the security logic stays the star and
you can swap providers. Default is the Anthropic SDK; change it freely.
"""
import json
from .tools import TOOLS
from .guard import Guard, Blocked


def _llm_step(messages, tool_specs):
    """Return (assistant_text, tool_call_or_None).

    TODO(you): wire this to your provider. With the Anthropic SDK:
        from anthropic import Anthropic
        client = Anthropic()
        resp = client.messages.create(
            model="claude-...", max_tokens=1024,
            messages=messages, tools=tool_specs)
        # parse resp.content for a tool_use block; return its name+input
    Keep it boring — the interesting part is the guard, not the plumbing.
    """
    raise NotImplementedError("Wire up your LLM provider here (Day 2).")


def run_agent(user_request: str, guard: Guard, max_steps: int = 6) -> str:
    """Run the agent until it stops calling tools or hits max_steps."""
    tool_specs = [{"name": t.name, "description": t.description,
                   "input_schema": t.schema} for t in TOOLS.values()]
    messages = [{"role": "user", "content": user_request}]

    for _ in range(max_steps):
        text, call = _llm_step(messages, tool_specs)
        if call is None:
            return text
        tool = TOOLS[call["name"]]
        try:
            result = guard.run_tool(tool, **call.get("input", {}))
        except Blocked as e:
            result = f"BLOCKED: {e}"
        messages.append({"role": "assistant", "content": json.dumps(call)})
        messages.append({"role": "user",
                         "content": f"Tool result: {result}"})
    return "[max steps reached]"
