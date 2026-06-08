# AgentGuard: stopping indirect prompt injection at the tool boundary

> Day-5 writeup template. Fill each section in your own words. This doc doubles
> as your pitch — the "Limitations / Next" section is what you show Bagdasaryan.

## 1. The problem (3–4 sentences)
What indirect prompt injection is, and why tool-using agents make it dangerous.

## 2. Threat model
Pull the sharpened version from THREAT_MODEL.md. One paragraph + the property.

## 3. The attack (the "before")
Show the poisoned document and the unguarded transcript where the agent leaks
the secret. One screenshot/transcript.

## 4. The defense
Explain the two layers and why their roles differ:
- **Policy (the boundary):** Rule-of-Two taint tracking — the actual guarantee.
- **Detector (defense in depth):** reduces noise, not a guarantee.

## 5. Results
Your benchmark table: attacks × {unguarded, guarded}. Note detector
precision/recall and any false positives. Be honest about misses.

## 6. Limitations & what's next  ← the pitch
- Single-agent only so far. The interesting case is **multi-agent**: enforcing
  these properties on agent-to-agent messages, where taint must propagate across
  agents and collusion becomes possible.
- The policy is coarse (binary tags). A richer model is **contextual integrity**:
  judging tool calls against the *norms* of the data's original context, not just
  three boolean flags.
- Both of these are exactly the direction the UMass AI Security Lab's multi-agent
  safety work is pushing. That's the thesis-shaped question you'd want to explore.
```
```
