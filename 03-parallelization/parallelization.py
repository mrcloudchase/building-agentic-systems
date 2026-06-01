"""03 · Parallelization — run calls at once: sectioning (independent parts) + voting (same task xN).

    pip install anthropic; export ANTHROPIC_API_KEY=sk-ant-...
    python 03-parallelization/parallelization.py
"""

import anthropic
from concurrent.futures import ThreadPoolExecutor

client = anthropic.Anthropic()
def ask(p): return client.messages.create(model="claude-opus-4-8", max_tokens=1024, messages=[{"role": "user", "content": p}]).content[0].text

contract = "Auto-renews for 12-month terms unless 90 days' notice. Liability capped at one month's fees. Customer waives jury trial. Vendor may change pricing on 15 days' notice."
aspects = ["payment & renewal", "liability & risk", "missing standard clauses"]
with ThreadPoolExecutor() as pool:
    reviews = list(pool.map(ask, [f"Review this contract for {a}:\n{contract}" for a in aspects]))  # SECTIONING
    votes = list(pool.map(lambda _: ask(f"Does this contract have a high-risk clause needing legal review? Reply YES or NO:\n{contract}"), range(3)))  # VOTING
for a, r in zip(aspects, reviews): print(f"## {a}\n{r}\n")
print("decision:", "ESCALATE TO LEGAL" if any("YES" in v.upper() for v in votes) else "looks standard")
