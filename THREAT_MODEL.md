# AgentGuard — Threat Model

## 1. System under protection
A tool-using LLM agent that:
- ingests external content via a `read_*` tool (UNTRUSTED), and
- can take a consequential action via an `action_*` tool (EXTERNAL EFFECT), and
- has access to some private value (SENSITIVE DATA).

## 2. Assets (what are we protecting?)
AgentGuard aims to protect data confidentiality of the agent, as well as the integrity of the actions it can take--untrusted input cannot cause sensitive data to go out, and unauthorized external actions must not occur for any single run of the model.

## 3. Adversary
- **Capability:** can place content where the agent will read it (a web page,
  a document, an email body) — but CANNOT see the system prompt or call tools
  directly. This is indirect prompt injection.
- **Goal:** Would executing the call make the FORBIDDEN pattern - untrusted IN -> sensitive processing -> external OUT - in this run?
- **Out of scope:** model weight attacks, supply-chain, the human user being
  malicious(The user is trusted in this model, defending against malicious users is an authorization/least-privilege problem to be addressed seperately)

## 4. Trust boundary
The boundary AgentGuard enforces is the **agent → tool call**. The LLM's output
is NOT trusted; any tool argument the model produces is attacker-influenced once
untrusted content has entered the context.

## 5. Security property claim
> No single agent run may simultaneously(in a single run) (a) have ingested untrusted content,
> (b) read sensitive data, and (c) cause an external effect.

**Rule of Two** (Meta) / **lethal trifecta** (Willison). The guard's job is to make this property holds even when the model is fully manipulated.

## 6. Why "just filter the input" isn't enough
An attackers goal is not to get the text into the context but rather cause a harmful action as a result. Thus, blocking the action(AgentGuard policy) is a guarentee whereas blocking the text input is a 'maybe'. Why is it a maybe? Full coverage is not guarenteed, context can be extremely large to parse and check, might need extremely robust checks. If the detector is a classifier, gradient based perturbations can generate payloads that score low-risk and mean something meaningful to the model nontheless. 