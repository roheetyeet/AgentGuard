"""Structured JSON logging of every tool call and guard decision.

Good logs make your demo and your benchmark trivial to produce, and they're
exactly the audit trail a real deployment needs. Don't skip this.
"""
import json
import os
import time

LOG_DIR = "logs"

def log_event(event: dict) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    event = {"ts": time.time(), **event}
    with open(os.path.join(LOG_DIR, "events.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def log_tool_call(tool_name: str, args: dict, decision: str, reason: str = "") -> None:
    log_event({
        "type": "tool_call",
        "tool": tool_name,
        "args": args,
        "decision": decision,
        "reason": reason,
    })
