# AgentGuard

A security proxy that sits between an LLM agent and its tools, inspects every
tool call, and enforces policy to stop prompt-injection-driven tool misuse.

It is a *networking* artifact (an interceptor on the agent↔tool channel) and an
*AI-security* artifact (taint tracking + injection detection + policy
enforcement) at the same time.

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
combination.

## Architecture

```
        ┌─────────┐   wants to call tool   ┌─────────┐   allow?   ┌────────┐
  LLM ─►│  agent  │ ─────────────────────► │  guard  │ ─────────► │  tool  │
        └─────────┘                        └─────────┘            └────────┘
                                              │  ▲
                                  policy.py ──┘  └── detector.py
                                  (Rule of Two)    (injection scan)
```

- `agentguard/agent.py`   — minimal tool-using agent loop (the subject under test)
- `agentguard/tools.py`   — tools, each tagged with security metadata
- `agentguard/guard.py`   — the interceptor: allow / block / escalate
- `agentguard/policy.py`  — Rule-of-Two / taint-tracking decision logic  ← your work
- `agentguard/detector.py`— injection detection on untrusted inputs        ← your work
- `agentguard/logging_utils.py` — structured logging of every decision
- `attacks/`              — the prompt-injection payloads you build (the "before")
- `benchmarks/`           — runs attacks against guarded vs unguarded, prints results
- `tests/`                — pytest sanity checks

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then put your API key in .env
python -m attacks.indirect_injection   # see the unguarded agent get hijacked
python -m benchmarks.run_benchmark      # guarded vs unguarded comparison
```

## Build plan (one week)

- **Day 1** — read `THREAT_MODEL.md`, fill in the asset/attacker sections, skim code.
- **Day 2** — make `attacks/indirect_injection.py` actually hijack the agent.
- **Day 3** — implement the TODOs in `policy.py` + `guard.py` so the attack is blocked.
- **Day 4** — implement `detector.py`, wire in a few Garak probes, fill `benchmarks/`.
- **Day 5** — fill `docs/writeup_template.md`, record a demo, push public.

See the TODOs marked `# TODO(you):` throughout the code.
