"""Sanity tests for the policy engine. Run: pytest

These pin down the security property so you don't regress while iterating.
They will fail until you implement policy.evaluate (Day 3) — that's expected.
"""
import pytest
from agentguard.tools import TOOLS
from agentguard.policy import TaintState, evaluate, Decision


def test_external_effect_alone_is_allowed():
    # send() with no untrusted/sensitive history -> allowed
    assert evaluate(TOOLS["send"], TaintState()) is Decision.ALLOW


def test_trifecta_is_blocked():
    # already read untrusted + sensitive, now trying an external effect -> block
    state = TaintState(ingested_untrusted=True, accessed_sensitive=True)
    assert evaluate(TOOLS["send"], state) in (Decision.BLOCK, Decision.ESCALATE)


def test_two_of_three_is_allowed():
    # untrusted + sensitive but NO external effect (reading secret) -> allow
    state = TaintState(ingested_untrusted=True)
    assert evaluate(TOOLS["get_secret"], state) is Decision.ALLOW
