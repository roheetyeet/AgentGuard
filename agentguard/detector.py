"""Injection detector: scans untrusted content for likely prompt-injection.

Framing for writeup: the detector catches obvious attacks and produces 
useful signal, but it is probabilistic and evadable. 
The policy engine is the guarantee; the detector
just reduces noise and gives the audit log something to say.
"""
from dataclasses import dataclass
import re

@dataclass
class DetectionResult:
    flagged: bool
    score: float          # 0.0 (clean) .. 1.0 (very suspicious)
    reason: str

_OVERRIDE_PATTERNS = [
    r"ignore (all |the |your )?(previous|prior|above)",
    r"disregard (all |the |your )?(previous|prior|above)",
    r"forget (everything|all|your instructions)",
    r"new instructions?:",
    r"system\s*:",
    r"you are now",
    r"act as",
]
_EXFIL_PATTERNS = [
    r"\bsend\b", r"\bforward\b", r"\bemail\b", r"\bpost\b", r"\bupload\b",
    r"\bexfiltrate\b", r"secret", r"api[_\s-]?key", r"password", r"token",
    r"credential",
]
_OBFUSCATION_PATTERNS = [
    r"[A-Za-z0-9+/]{40,}={0,2}",      # long base64-ish blob
    r"\\x[0-9a-fA-F]{2}",             # hex escapes
    r"&#x?[0-9a-fA-F]+;",             # html/numeric entities
]

def _scan(text: str, patterns) -> list[str]:
    hits = []
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            hits.append(p)
    return hits

def detect_heuristic(text: str) -> DetectionResult:
    """Cheap, deterministic first pass over untrusted text.

    Scoring: override phrases are the strongest single signal of injection;
    exfiltration vocabulary and obfuscation each add weight. Cap at 1.0.
    The threshold for `flagged` is intentionally low (0.3) because this layer
    is advisory — false positives here are cheap, since the policy is what
    actually enforces safety.
    """
    override = _scan(text, _OVERRIDE_PATTERNS)
    exfil = _scan(text, _EXFIL_PATTERNS)
    obfus = _scan(text, _OBFUSCATION_PATTERNS)

    score = 0.0
    score += 0.6 if override else 0.0
    score += min(0.3, 0.1 * len(exfil))
    score += 0.3 if obfus else 0.0
    score = min(1.0, score)

    reasons = []
    if override:
        reasons.append(f"instruction-override phrasing ({len(override)})")
    if exfil:
        reasons.append(f"exfiltration vocabulary ({len(exfil)})")
    if obfus:
        reasons.append("possible obfuscation/encoding")
    reason = "; ".join(reasons) if reasons else "no injection signatures found"

    return DetectionResult(flagged=score >= 0.3, score=round(score, 2), reason=reason)

def detect_llm(text: str) -> DetectionResult:
    """Optional: ask a cheap model whether text manipulates an agent.

    Left unimplemented on purpose. A benchmark result is to compare this
    model-based detector's precision/recall against the heuristic above.
    """
    raise NotImplementedError("Optional LLM detector (stretch goal).")
