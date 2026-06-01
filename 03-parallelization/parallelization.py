"""03 · Parallelization — the simplest version.

Run several LLM calls at the same time, then combine the results. The article
describes two shapes, both shown here on a code-review task:

  * SECTIONING — split a task into independent parts, run them in parallel.
                 (Review the snippet for security, performance, readability.)
  * VOTING     — run the SAME task several times, then combine the answers.
                 (Ask "is there a vulnerability?" three times; flag if any say yes.)

    code ─┬─→ [call] ─┐
          ├─→ [call] ─┼─→ aggregate → output
          └─→ [call] ─┘

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 03-parallelization/parallelization.py
"""

import os
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")


def ask(prompt: str) -> str:
    """Send one prompt and return the text. We run many of these at once."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# The snippet under review — it has a SQL-injection hole (security), builds a
# list inefficiently (performance), and uses unclear names (readability), so the
# three independent reviewers each have something different to find.
CODE = '''def get_user(db, user_id):
    q = "SELECT * FROM users WHERE id = '" + user_id + "'"
    rows = db.execute(q)
    result = []
    for r in rows:
        result = result + [r]
    return result'''


# --- SECTIONING: independent reviews, run concurrently ---------------------
# Each reviewer looks at the same code but for a different concern. The reviews
# don't depend on each other, so we run them all at once.

reviews = {
    "security": f"Review this code for SECURITY issues only. Be brief.\n\n{CODE}",
    "performance": f"Review this code for PERFORMANCE issues only. Be brief.\n\n{CODE}",
    "readability": f"Review this code for READABILITY issues only. Be brief.\n\n{CODE}",
}

with ThreadPoolExecutor() as pool:
    # pool.map keeps order, so we can zip the answers back to their labels.
    results = dict(zip(reviews, pool.map(ask, reviews.values())))

print("=== SECTIONING (review for different concerns in parallel) ===")
for concern, review in results.items():
    print(f"## {concern}\n{review}\n")


# --- VOTING: the same check several times, then combine --------------------
# Ask the vulnerability question three times and flag the code if ANY reviewer
# says yes — a conservative rule that errs toward catching problems.

vote_prompt = f"Does this code contain a security vulnerability? Answer only YES or NO.\n\n{CODE}"

with ThreadPoolExecutor() as pool:
    votes = list(pool.map(lambda _: ask(vote_prompt), range(3)))

flagged = any(v.strip().upper().startswith("YES") for v in votes)

print("=== VOTING (same vulnerability check x3) ===")
print(f"votes: {votes}")
print(f"decision: {'FLAG FOR REVIEW' if flagged else 'looks clean'}")
