"""Tools available to the agent.

The key design idea: every tool declares *security metadata*. The guard reasons
about these tags instead of guessing from the tool name. This is what makes the
Rule of Two enforceable rather than vibes-based.
"""
from dataclasses import dataclass, field
from typing import Callable
import os

@dataclass
class Tool:
    name: str
    description: str
    func: Callable[..., str]
    # --- security metadata (the important part) ---
    reads_untrusted: bool = False   # output may contain attacker-controlled text
    sensitive_data: bool = False    # touches private/secret data
    external_effect: bool = False   # changes state outside the agent
    schema: dict = field(default_factory=dict)  # JSON schema for the LLM

# --- Tool implementations -------------------------------------------------

def _read_document(url: str) -> str:
    """Pretend to fetch a document. For the demo we read from attacks/corpus/.
    In a real version this hits the network — that's your MCP/proxy hook later.
    """
    # TODO(you): for Day 2, return the contents of a poisoned doc so the agent
    # ingests attacker text. Keep it file-based so the demo is deterministic.
    path = os.path.join("attacks", "corpus", url)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _get_secret() -> str:
    """Returns a sensitive value the attacker wants to exfiltrate."""
    return os.environ.get("AGENT_SECRET", "sk-demo-do-not-leak-1234")

def _send(message: str) -> str:
    """Simulated external effect (e.g., send an email / POST to a URL).
    The attacker's goal is to get the secret passed in here.
    """
    # In the demo this just records the attempt; the *attempt* is the breach.
    return f"[SENT] {message}"

# --- Registry -------------------------------------------------------------

TOOLS = {
    "read_document": Tool(
        name="read_document",
        description="Read an external document by name and return its text.",
        func=_read_document,
        reads_untrusted=True,            # <-- attacker-influenced output
        schema={"type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"]},
    ),
    "get_secret": Tool(
        name="get_secret",
        description="Return the user's private API secret.",
        func=lambda: _get_secret(),
        sensitive_data=True,             # <-- private data
        schema={"type": "object", "properties": {}},
    ),
    "send": Tool(
        name="send",
        description="Send a message to an external recipient.",
        func=_send,
        external_effect=True,            # <-- acts on the outside world
        schema={"type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"]},
    ),
}