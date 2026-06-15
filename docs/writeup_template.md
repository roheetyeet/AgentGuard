# AgentGuard: stopping indirect prompt injection at the tool boundary

## 1. The problem

## 2. Threat model

## 3. The attack (the "before")

## 4. The defense

## 5. Results

## 6. Limitations & what's next  ← the pitch
- Single-agent only so far. The interesting case is **multi-agent**: enforcing
  these properties on agent-to-agent messages, where taint must propagate across
  agents and collusion becomes possible.
- The policy is coarse (binary tags). A richer model is **contextual integrity**:
  judging tool calls against the *norms* of the data's original context, not just
  three boolean flags.
- Both of these are exactly the direction the UMass AI Security Lab's multi-agent
  safety work is pushing.
```
```
