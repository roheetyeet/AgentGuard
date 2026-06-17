```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██╗     ██╗     ███╗   ███╗    ███████╗███████╗ ██████╗                   ║
║    ██║     ██║     ████╗ ████║    ██╔════╝██╔════╝██╔════╝                   ║
║    ██║     ██║     ██╔████╔██║    ███████╗█████╗  ██║                        ║
║    ██║     ██║     ██║╚██╔╝██║    ╚════██║██╔══╝  ██║                        ║
║    ███████╗███████╗██║ ╚═╝ ██║    ███████║███████╗╚██████╗                   ║
║    ╚══════╝╚══════╝╚═╝     ╚═╝    ╚══════╝╚══════╝ ╚═════╝                   ║
║                                                                              ║
║              LLM Security: From Vulnerability to Defense                     ║
║                                                                              ║
║   A 10-project series addressing every OWASP Top 10 for LLM Applications.    ║
║   Each repo is a standalone tool. All compose into a unified runtime.        ║
║                                                                              ║
║   01 ► AgentGuard          [ Prompt Injection          ] ◄ YOU ARE HERE      ║
║   02 ► ContextShield       [ Sensitive Info Disclosure ]                     ║
║   03 ► ChainVerify         [ Supply Chain              ]                     ║
║   04 ► PoisonProbe         [ Data & Model Poisoning    ]                     ║
║   05 ► SinkGuard           [ Improper Output Handling  ]                     ║
║   06 ► CapAudit            [ Excessive Agency          ]                     ║
║   07 ► PromptCanary        [ System Prompt Leakage     ]                     ║
║   08 ► RAGShield           [ Vector & Embedding        ]                     ║
║   09 ► GroundCheck         [ Misinformation            ]                     ║
║   10 ► TokenGov            [ Unbounded Consumption     ]                     ║
║                                                                              ║
║   Root project & full architecture → github.com/roheetyeet/llm-sec           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> **OWASP LLM01 — Prompt Injection** | Part of the LLM Sec series.
> See the [root project](https://github.com/roheetyeet/llm-sec) for the full
> architecture, how these tools compose, and the roadmap.

# AgentGuard

A content-blind security guard that sits between an LLM agent and its tools and
enforces the **Rule of Two** (Meta) / **lethal trifecta** (Willison): no single
agent run may simultaneously (a) ingest untrusted content, (b) access sensitive
data, and (c) cause an external effect. Any two are fine; all three is the
exploitable combination, so the guard blocks the call that would complete it.

The guard reasons only about *which of the three properties a run has
accumulated*, never about tool arguments or text, which is what makes it
robust to prompt injection regardless of how a payload is encoded.

## What's implemented

- `agentguard/policy.py` — the Rule-of-Two engine (`evaluate` -> `PolicyResult`)
- `agentguard/guard.py` — the interceptor: policy check before execution, then
  defense-in-depth detection on untrusted output, then taint update
- `agentguard/detector.py` — transparent heuristic injection scanner (advisory)
- `agentguard/agent.py` — `ScriptedPlanner` (deterministic, default) and an
  optional `LLMPlanner` (real Anthropic model)
- `attacks/`, `benchmarks/`, `tests/` — the attack, the comparison table, tests

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
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # rich + pytest; both optional for core
cp .env.example .env                    # only needed for the live LLM planner

python -m attacks.indirect_injection    # before/after: leak, then blocked
python -m benchmarks.run_benchmark       # guarded vs unguarded table
pytest                                   # 10 tests (or: python -m pytest)
```

Everything except the optional live LLM mode runs **offline and deterministically**, no API key required, because the artifact under evaluation is the guard, not the model.

## The four runnable claims

1. Unguarded, the scripted exfiltration attack leaks the secret.
2. Guarded, the identical attack is blocked at the `send` call.
3. A benign read-then-send task is **not** blocked (the guard isn't over-broad).
4. The policy decision is content-blind: it never inspects the message text.

## Limitations / what's next

- Run-scoped, flow-*insensitive* taint (binary flags, not per-value tracking).
- Single agent. The research direction is multi-agent taint propagation and
  replacing binary flags with contextual-integrity-style policies (cf. Conseca,
  HotOS '25; Ghalebikesabi et al., CCS '24). See `docs/writeup_template.md`.
