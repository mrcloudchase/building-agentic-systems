"""03 · Parallelization — the simplest version.

Run several LLM calls at the same time, then combine the results. Two shapes:

  * SECTIONING — split a task into independent parts, run them in parallel.
  * VOTING     — run the SAME task several times, then combine the answers.

Here we review one code snippet: sectioning checks different concerns at once;
voting runs the same vulnerability check several times.

Run it (pass a code snippet, or use the default):
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

# The default input — a snippet with a SQL-injection hole, an inefficient loop,
# and unclear names, so each sectioning reviewer finds something different.
DEFAULT_INPUT = '''def get_user(db, user_id):
    q = "SELECT * FROM users WHERE id = '" + user_id + "'"
    rows = db.execute(q)
    result = []
    for r in rows:
        result = result + [r]
    return result'''

# Sectioning concerns, defined as data — one independent review each.
ASPECTS = ["security", "performance", "readability"]


def ask(prompt: str) -> str:
    """Call the provider with one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def section(aspects: list[str], code: str) -> dict[str, str]:
    """SECTIONING: review the code for each aspect, all in parallel."""
    prompts = [f"Review this code for {a} issues only. Be brief.\n\n{code}" for a in aspects]
    with ThreadPoolExecutor() as pool:
        reviews = pool.map(ask, prompts)  # keeps order
    return dict(zip(aspects, reviews))


def vote(prompt: str, n: int = 3) -> list[str]:
    """VOTING: run the same prompt n times in parallel."""
    with ThreadPoolExecutor() as pool:
        return list(pool.map(lambda _: ask(prompt), range(n)))


if __name__ == "__main__":
    code = " ".join(sys.argv[1:]) or DEFAULT_INPUT

    print("=== SECTIONING (different concerns in parallel) ===")
    for aspect, review in section(ASPECTS, code).items():
        print(f"## {aspect}\n{review}\n")

    print("=== VOTING (same vulnerability check x3) ===")
    votes = vote(
        f"Does this code contain a security vulnerability? Answer only YES or NO.\n\n{code}"
    )
    flagged = any(v.strip().upper().startswith("YES") for v in votes)
    print(f"votes: {votes}")
    print(f"decision: {'FLAG FOR REVIEW' if flagged else 'looks clean'}")
