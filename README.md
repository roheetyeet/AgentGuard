# AgentGuard

A security proxy between an LLM agent and its tools that inspects every
tool call and enforces a policy to stop prompt-injection-driven tool misuse.

## The core idea

Modern agents are dangerous when a single request combines three things:

1. **Untrusted input** — the agent reads attacker-influenced content (a web
   page, a document, an email).
2. **Sensitive data** — the agent can access private/secret data.
3. **External effect** — the agent can act on the outside world (send, write,
   call an API).

Any two of these is usually fine. All three is the "lethal trifecta" / a
violation of the **Rule of Two**, and it's where indirect prompt injection turns
into real damage. AgentGuard tracks these properties as *taint* on the agent's
context and on each tool, and refuses tool calls that would complete the unsafe
combination. (Check references under `THREAT_MODEL.md`)

## Architecture

```
        ┌─────────┐   wants to call tool   ┌─────────┐   allow?   ┌────────┐
  LLM ─►│  agent  │ ─────────────────────► │  guard  │ ─────────► │  tool  │
        └─────────┘                        └─────────┘            └────────┘
                                              │  ▲
                                  policy.py ──┘  └── detector.py
                                  (Rule of Two)    (injection scan)
```

- `agentguard/agent.py`   — the subject under test
- `agentguard/tools.py`   — tools, each with security metadata
- `agentguard/guard.py`   — allow / block / escalate
- `agentguard/policy.py`  — Rule-of-Two / taint-tracking decision logic
- `agentguard/detector.py`— injection detection on untrusted inputs
- `agentguard/logging_utils.py` — log decisions
- `attacks/`              — the prompt-injection payloads
- `benchmarks/`           — run attacks against guarded vs unguarded, print result
- `tests/`                — pytest checks

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then put your API key in .env
python -m attacks.indirect_injection   # see the unguarded agent get hijacked
python -m benchmarks.run_benchmark      # guarded vs unguarded comparison
```

## Build plan (one week)

- **Day 1** — read `THREAT_MODEL.md`, fill in the asset/attacker sections
- **Day 2** — make `attacks/indirect_injection.py` actually hijack the agent.
- **Day 3** — implement the TODOs in `policy.py` + `guard.py` so the attack is blocked.
- **Day 4** — implement `detector.py`, learn about and implement Garak probes, fill `benchmarks/`.
- **Day 5** — fill `docs/writeup_template.md`, record a demo, push public.
