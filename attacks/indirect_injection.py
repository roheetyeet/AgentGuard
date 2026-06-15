"""Demonstrate the indirect prompt-injection breach, then the guard stopping it.

Run:  python -m attacks.indirect_injection

Shows the "before" (unguarded agent leaks the secret) and the "after" (the same
scripted attack is blocked by the Rule-of-Two policy).
"""
from agentguard.agent import run_agent, ScriptedPlanner, EXFIL_PLAN
from agentguard.guard import Guard
from agentguard.tools import TOOLS

def _report(label: str, res: dict) -> None:
    secret = TOOLS["get_secret"].func()
    leaked = any(secret in m for m in res["sent"])
    print(f"\n=== {label} ===")
    for s in res["steps"]:
        print(f"  {s['status']:>8}  {s['name']}({s['input']})")
    print(f"  --> secret leaked: {leaked}")

def main():
    _report("UNGUARDED (before)", run_agent(ScriptedPlanner(EXFIL_PLAN), Guard(enabled=False)))
    _report("GUARDED (after)", run_agent(ScriptedPlanner(EXFIL_PLAN), Guard(enabled=True)))

if __name__ == "__main__":
    main()
