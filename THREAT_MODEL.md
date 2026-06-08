# AgentGuard — Threat Model (Day 1)

Fill this in first. A clear threat model is what separates a security project
from a demo, and it's the first thing a researcher (or interviewer) will probe.

## 1. System under protection
A tool-using LLM agent that:
- ingests external content via a `read_*` tool (UNTRUSTED), and
- can take a consequential action via an `action_*` tool (EXTERNAL EFFECT), and
- has access to some private value (SENSITIVE DATA).

## 2. Assets (what are we protecting?)
<!-- TODO(you): be specific. e.g., a secret/API token in the agent's context,
     the integrity of the external action, the user's private files. -->

## 3. Adversary
- **Capability:** can place content where the agent will read it (a web page,
  a document, an email body) — but CANNOT see the system prompt or call tools
  directly. This is *indirect* prompt injection.
- **Goal:** <!-- TODO(you): exfiltrate the secret? trigger the action tool with
     attacker-chosen arguments? -->
- **Out of scope:** model weight attacks, supply-chain, the human user being
  malicious. Say so explicitly — scoping is a skill.

## 4. Trust boundary
The boundary AgentGuard enforces is the **agent → tool call**. The LLM's output
is NOT trusted; any tool argument the model produces is attacker-influenced once
untrusted content has entered the context.

## 5. Security property we claim
> No single agent run may simultaneously (a) have ingested untrusted content,
> (b) read sensitive data, and (c) cause an external effect.

This is the **Rule of Two** (Meta) / **lethal trifecta** (Willison). The guard's
job is to make this property hold even when the model is fully manipulated.

## 6. Why "just filter the input" isn't enough
<!-- TODO(you): one paragraph. Detection is probabilistic and bypassable;
     the architectural policy is the real boundary. The detector reduces noise,
     the policy is the guarantee. This distinction is the thesis of the project. -->
