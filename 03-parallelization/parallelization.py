"""03 · Parallelization — the simplest version.

Run several LLM calls at the same time, then combine the results. Two shapes:

  * SECTIONING — split a task into independent parts, run them in parallel.
  * VOTING     — run the SAME task several times, then combine the answers.

Business use case: contract review. Sectioning reviews the contract on several
independent concerns at once; voting runs a high-risk check several times and
escalates to legal if any reviewer objects.

Run it (pass a contract excerpt, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 03-parallelization/parallelization.py
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# The default input — a contract excerpt with an auto-renewal trap, a tight
# liability cap, a jury-trial waiver, and unilateral price changes, so each
# reviewer finds something different.
DEFAULT_INPUT = (
    "This Agreement renews automatically for successive 12-month terms unless "
    "Customer gives written notice at least 90 days before renewal. Vendor's "
    "total liability is limited to the fees paid in the month before any claim. "
    "Customer waives any right to a jury trial. Vendor may change pricing at any "
    "time on 15 days' notice."
)

# Sectioning concerns, defined as data — one independent review each.
ASPECTS = ["payment & renewal terms", "liability & risk", "missing standard clauses"]


def ask(prompt: str) -> str:
    """Call the provider with one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def section(aspects: list[str], text: str) -> dict[str, str]:
    """SECTIONING: review the contract for each aspect, all in parallel."""
    prompts = [f"Review this contract for {a} only. Be brief.\n\n{text}" for a in aspects]
    with ThreadPoolExecutor() as pool:
        reviews = pool.map(ask, prompts)  # keeps order
    return dict(zip(aspects, reviews))


def vote(prompt: str, n: int = 3) -> list[str]:
    """VOTING: run the same prompt n times in parallel."""
    with ThreadPoolExecutor() as pool:
        return list(pool.map(lambda _: ask(prompt), range(n)))


if __name__ == "__main__":
    contract = " ".join(sys.argv[1:]) or DEFAULT_INPUT

    print("=== SECTIONING (review concerns in parallel) ===")
    for aspect, review in section(ASPECTS, contract).items():
        print(f"## {aspect}\n{review}\n")

    print("=== VOTING (high-risk check x3) ===")
    votes = vote(
        "Does this contract contain any clause that is high-risk or non-standard "
        f"and needs legal review? Answer only YES or NO.\n\n{contract}"
    )
    flagged = any(v.strip().upper().startswith("YES") for v in votes)
    print(f"votes: {votes}")
    print(f"decision: {'ESCALATE TO LEGAL' if flagged else 'looks standard'}")
