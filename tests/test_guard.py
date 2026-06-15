"""Sanity tests for the policy engine and the guard. Run: pytest

These pin down the security property so you don't regress while iterating.
"""
from agentguard.tools import TOOLS
from agentguard.policy import TaintState, evaluate, Decision
from agentguard.guard import Guard, Blocked
from agentguard.agent import run_agent, ScriptedPlanner, EXFIL_PLAN, ToolCall

# --- Policy unit tests: every pairwise combo is allowed, the trifecta is not ---

def test_external_effect_alone_is_allowed():
    assert evaluate(TOOLS["send"], TaintState()).decision is Decision.ALLOW

def test_read_then_secret_is_allowed():
    # untrusted + sensitive, but no external effect -> two of three -> allow
    state = TaintState(ingested_untrusted=True)
    assert evaluate(TOOLS["get_secret"], state).decision is Decision.ALLOW

def test_untrusted_plus_external_is_allowed():
    # untrusted + external, no sensitive data -> allow
    state = TaintState(ingested_untrusted=True)
    assert evaluate(TOOLS["send"], state).decision is Decision.ALLOW

def test_sensitive_plus_external_is_allowed():
    # sensitive + external, clean run (no untrusted) -> the legit user case -> allow
    state = TaintState(accessed_sensitive=True)
    assert evaluate(TOOLS["send"], state).decision is Decision.ALLOW

def test_trifecta_is_blocked():
    state = TaintState(ingested_untrusted=True, accessed_sensitive=True)
    assert evaluate(TOOLS["send"], state).decision is Decision.BLOCK

def test_escalate_mode_returns_escalate():
    state = TaintState(ingested_untrusted=True, accessed_sensitive=True)
    assert evaluate(TOOLS["send"], state, escalate=True).decision is Decision.ESCALATE

def test_policy_result_has_reason():
    state = TaintState(ingested_untrusted=True, accessed_sensitive=True)
    assert "Rule of Two" in evaluate(TOOLS["send"], state).reason

# --- End-to-end: the same attack breaches when unguarded, is stopped when guarded ---

def test_exfil_breaches_when_unguarded():
    res = run_agent(ScriptedPlanner(EXFIL_PLAN), Guard(enabled=False))
    secret = TOOLS["get_secret"].func()
    assert any(secret in msg for msg in res["sent"]), "unguarded run should leak the secret"
    assert res["blocked"] is False

def test_exfil_blocked_when_guarded():
    res = run_agent(ScriptedPlanner(EXFIL_PLAN), Guard(enabled=True))
    secret = TOOLS["get_secret"].func()
    assert not any(secret in msg for msg in res["sent"]), "guarded run must not leak the secret"
    assert res["blocked"] is True

def test_benign_run_completes_when_guarded():
    # read + send (no secret access) is only two-of-three -> should be allowed
    plan = [ToolCall("read_document", {"url": "poisoned_doc.txt"}),
            ToolCall("send", {"message": "summary: economy fares ok under $800"})]
    res = run_agent(ScriptedPlanner(plan), Guard(enabled=True))
    assert res["blocked"] is False
    assert len(res["sent"]) == 1