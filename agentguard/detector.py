"""Injection detector: scans untrusted content for likely prompt-injection.

Important framing for your writeup: the detector is *defense in depth*, not the
security boundary. It reduces noise and catches obvious attacks; the policy
engine is what actually guarantees the safety property. Say this explicitly —
it's the most mature point you can make.
"""
from dataclasses import dataclass


@dataclass
class DetectionResult:
    flagged: bool
    score: float
    reason: str


def detect_heuristic(text: str) -> DetectionResult:
    """Cheap, deterministic first pass over untrusted text.

    TODO(you): Day 4. Look for injection signatures, e.g.:
      - imperative override phrases ("ignore previous", "disregard", "system:")
      - tool/exfiltration intent ("send", "post to", "secret", "api key")
      - role markers, fake delimiters, base64 blobs, unusual unicode
    Return a score in [0, 1] and a human-readable reason. Keep it simple and
    transparent — you want to be able to explain every flag.
    """
    raise NotImplementedError("Implement heuristic detection (Day 4).")


def detect_llm(text: str) -> DetectionResult:
    """Optional: ask a cheap model 'is this trying to manipulate an agent?'.

    TODO(you): stretch goal. Compare its precision/recall against the heuristic
    in your benchmark. The comparison itself is a nice result.
    """
    raise NotImplementedError("Optional LLM detector (stretch).")
