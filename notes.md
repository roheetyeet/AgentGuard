# AgentGuard — Study Notes
> Resources, concepts, and tools for the project. Written with help of Claude

---

## Part 1: Resources

### Start here (read in this order)

| What | Why | Link |
|------|-----|------|
| OWASP Top 10 for LLM Applications 2025 | The industry-standard threat taxonomy for LLM apps. LLM01 (Prompt Injection) is the core attack your project defends against. This is the first thing anyone in AI security references. | https://genai.owasp.org/llm-top-10/ |
| Simon Willison's blog | He coined the term "prompt injection" and is the best ongoing tracker of real-world attacks. Read his posts on the "lethal trifecta" — it's the conceptual backbone of AgentGuard's policy engine. | https://simonwillison.net |
| Meta "Agents Rule of Two" | The defense framework your policy.py implements. Search: *Meta engineering blog "Agents Rule of Two"* | blog post, search the title |
| Google Scholar | Anything on contextual integrity for AI agents/assistants. This is the v2 of your project and the bridge to his lab. | https://scholar.google.com/citations?user=_MfoOC8AAAAJ |

### Hands-on practice

| What | Why | Link |
|------|-----|------|
| Wiz "Prompt Airlines" CTF | A hands-on web challenge where you inject prompts into an airline chatbot. Best first CTF for learning attack intuition before Day 2. | Search: *Wiz Prompt Airlines CTF* |
| Garak | The LLM vulnerability scanner you'll use on Day 4 to pull pre-built attack probes. Install it, run it against your agent, steal the probes that hit. | https://garak.ai / https://github.com/NVIDIA/garak |
| Microsoft Semantic Kernel RCE writeup | A real agent exploit: prompt injection → tool → host-level remote code execution. Study the chain. There's a CTF version too. | Search: *Semantic Kernel prompt injection RCE CVE-2026* |

---

## Part 2: Core Concepts

### Prompt Injection
**The 30-second version:** LLMs follow instructions in text. If the model reads
attacker-controlled text that contains instructions, it may follow *those* instead
of the user's original request. It's like SQL injection but for natural language
— the model can't reliably tell "data I'm processing" apart from "instructions
I should obey."

**Direct injection:** the user themselves puts malicious instructions in their
message. (`"Ignore your system prompt and..."`)

**Indirect injection:** the attacker plants instructions *inside content the agent
will read* — a document, a web page, an email. The user asked a legitimate
question; the agent reads something poisoned mid-task. This is the attack
AgentGuard is built for.

**In AgentGuard terms:** the `read_document` tool returns attacker-controlled text.
That text enters the LLM's context. The LLM may then call `get_secret` and `send`
with attacker-chosen arguments. The agent was never directly told to do this — it
was tricked through what it read.

---

### The Lethal Trifecta (Simon Willison) / Rule of Two (Meta)
Two names for the same insight. A single agent run becomes dangerous when all
three of these are true simultaneously:

1. **(A) Untrusted input** — the agent read content an attacker could influence
2. **(B) Sensitive data** — the agent has access to something worth stealing
3. **(C) External effect** — the agent can act on the outside world (send, POST, write)

Any **two** of these is manageable. All **three** is the exploitable combination.
The attacker needs all three to land: A is how they manipulate, B is what they
steal, C is how it leaves.

AgentGuard's `policy.py` tracks whether A and B have happened in a run (via
`TaintState`), and blocks any C-tagged tool call when both are true.

---

### Taint Analysis
A classic compiler/program-analysis technique repurposed here. "Taint" means
"this data came from an untrusted source." In traditional security it's used to
trace whether user input reaches a dangerous function (like SQL execution) without
being sanitized.

In AgentGuard, you're doing a simplified version: once the agent calls a
`reads_untrusted` tool, the entire run is "tainted" (`ingested_untrusted = True`).
Once it calls a `sensitive_data` tool, the run is also "sensitivity-tainted." You
don't track individual values — you track *properties of the run*, which is coarser
but enforceable without modifying the LLM.

**In CS terms:** it's a flow-insensitive, run-scoped, binary taint analysis. If you
want a thesis extension, flow-sensitive taint (tracking *which* piece of context
came from which source) is a much harder and more powerful version.

---

### Contextual Integrity
A privacy theory from philosopher Helen Nissenbaum, adopted by AI Sec lab
for AI agents. The idea: information flows are appropriate when they match the
*norms of the context* in which the data originated.

Example: sharing medical records with another doctor is fine (matches the norms of
healthcare). Sharing them with an advertiser is a violation — not because the data
changed, but because the context did.

For agents: a tool call is "contextually appropriate" if the data flowing through
it respects the norms of where it came from. An agent reading a travel policy and
then sending your API key to a stranger violates contextual integrity — the travel
doc context doesn't permit that flow.

This is AgentGuard's v2 direction. Instead of three binary flags, the policy
reasons about whether each tool call respects the norms of the data's origin
context. Much richer, much harder — which is why it's a research problem.

---

### Defense in Depth
A security design principle: don't rely on a single layer. Stack multiple defenses
so that bypassing one doesn't compromise the system.

In AgentGuard:
- **Detector** (`detector.py`) — scans untrusted text for injection signatures.
  First line of defense. Probabilistic. Can be evaded.
- **Policy** (`policy.py`) — enforces the trifecta rule at the action level.
  Does *not* look at content at all — only at what tools are being called and
  what the run has already done. Much harder to evade because it's structural,
  not content-based.

The detector reduces noise; the policy is the guarantee. If the detector misses
a cleverly encoded payload, the policy still blocks the action.

---

### Red-teaming
Originally a military term for a team that actively tries to break/attack a
system to expose weaknesses before real adversaries do. In AI security: you
deliberately try to make the model/agent do something it shouldn't.

In AgentGuard you are both the red team (building the attack in `attacks/`) and
the blue team (building the guard). This is the ideal project structure for a
portfolio — you show you understand both sides.

---

## Part 3: Tools & Libraries

### Garak
**What:** An open-source LLM vulnerability scanner, originally created by Prof.
Leon Derczynski and now developed and maintained by NVIDIA. Short for
"Generative AI Red-teaming & Assessment Kit."

**What it does:** You point it at an LLM or agent endpoint. It runs hundreds of
pre-built *probes* (attack inputs) across categories like prompt injection, data
leakage, hallucination, jailbreaks, and encoding-based evasion. It then runs
*detectors* on the outputs to check whether the attack succeeded.

**How you use it in this project (Day 4):** Install it, point it at your agent,
pull the probes from `garak/probes/promptinject` that actually hit, add them to
your `benchmarks/` attack list. This gives you a real, diverse attack corpus
instead of just hand-written payloads.

```bash
pip install garak
python -m garak --target_type openai --target_name gpt-4o --probes promptinject
```

**In AgentGuard terms:** Garak is your attacker's toolkit. It stress-tests your
guard with attack variants you didn't think of yourself.

---

### MCP (Model Context Protocol)
**What:** An open protocol (from Anthropic, now widely adopted) that standardizes
how AI agents communicate with external tools and data sources. Think of it like
HTTP — a common language so agents and tools from different providers can
interoperate.

**Why it matters here:** In AgentGuard v0, you directly intercept Python function
calls. In v1/v2 (and in the real world), tools are separate services and the
agent communicates with them over MCP. Your guard would sit as a *proxy* on that
network channel — inspecting MCP messages, not just Python calls. That's the
"networking" angle of this project: it becomes an actual network security problem
(inspect, filter, forward or drop traffic).

**Docs:** https://modelcontextprotocol.io

---

### OWASP
**What:** Open Web Application Security Project. A non-profit that produces
open, community-driven security standards. Most famous for the "OWASP Top 10"
for web apps (you may have seen things like SQL Injection, XSS listed there).
They now have a version for LLM Applications.

**The LLM Top 10 (2025):** A ranked list of the ten most critical security risks
for applications built on LLMs. LLM01 is Prompt Injection — your project. LLM06
(Excessive Agency) and LLM02 (Sensitive Information Disclosure) are also directly
relevant.

**Why it matters:** This is the reference document the industry, regulators, and
researchers all point to. If you can say "AgentGuard defends against LLM01, LLM02,
and LLM06" in your writeup, you've anchored your work in the standard taxonomy.

---

### Anthropic SDK (Tool Use / Function Calling)
**What:** The Python library for calling Claude (and Claude's tool-use feature).
Tool use is how agents call functions: the LLM outputs a structured "I want to
call function X with arguments Y" block, and your code executes it.

**In AgentGuard:** `agent.py`'s `_llm_step` function calls the SDK and parses the
response for tool-use blocks. This is where you wire up the actual LLM. The SDK
docs have a clear "tool use" section — read that before Day 2.

```python
from anthropic import Anthropic
client = Anthropic()
# Pass tools=[...] and parse resp.content for type=="tool_use" blocks
```

---

### Rich
**What:** A Python library for pretty terminal output — colored text, tables,
progress bars, syntax highlighting.

**In AgentGuard:** Used in `benchmarks/run_benchmark.py` to print the results
table (guarded vs. unguarded, attacks caught/missed). Purely cosmetic, but it
makes the demo look professional and is easy to screenshot for your writeup.

---

### pytest
**What:** The standard Python testing framework. You write test functions that
start with `test_`, run `pytest`, it finds and runs them all.

**In AgentGuard:** `tests/test_guard.py` has three tests that pin down the security
property. They fail on purpose until you implement `policy.py`. Once you do,
running `pytest` going green is a satisfying checkpoint — and it means you haven't
accidentally broken the invariant while iterating.

---

### python-dotenv
**What:** A small library that reads a `.env` file and loads the key-value pairs
as environment variables. Standard way to keep API keys out of code.

**In AgentGuard:** Your Anthropic API key lives in `.env` (which is gitignored).
Call `load_dotenv()` at the top of your script and then `os.environ["ANTHROPIC_API_KEY"]`
works. Never hardcode keys — `.env` + `python-dotenv` is the correct pattern.