"""03 · Parallelization — the simplest version.

Run several LLM calls at the same time, then combine the results. The article
describes two shapes, both shown here:

  * SECTIONING — split a task into independent parts, run them in parallel.
  * VOTING     — run the SAME task several times, then combine the answers.

    input ─┬─→ [call] ─┐
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


# --- SECTIONING: independent subtasks, run concurrently --------------------
# Three different questions about one idea — none depends on the others, so we
# fire them all at once and collect the answers.

idea = "a subscription box that mails a new houseplant every month"
sections = {
    "market": f"In 2 sentences, estimate market demand for: {idea}",
    "feasibility": f"In 2 sentences, assess how hard this is to build: {idea}",
    "competition": f"In 2 sentences, describe the competition for: {idea}",
}

with ThreadPoolExecutor() as pool:
    # pool.map keeps order, so we can zip the answers back to their labels.
    results = dict(zip(sections, pool.map(ask, sections.values())))

print("=== SECTIONING ===")
for name, text in results.items():
    print(f"## {name}\n{text}\n")


# --- VOTING: the same task several times, then combine ----------------------
# Run one yes/no judgment three times and require unanimity — a single objection
# blocks publication.

text = "Our new release is faster and more reliable than ever. Try it today!"
vote_prompt = (
    "Is this text safe to publish on a company blog? Answer only SAFE or UNSAFE."
    f"\n\n{text}"
)

with ThreadPoolExecutor() as pool:
    votes = list(pool.map(lambda _: ask(vote_prompt), range(3)))

safe = all(v.strip().upper().startswith("SAFE") for v in votes)

print("=== VOTING ===")
print(f"votes: {votes}")
print(f"decision: {'PUBLISH' if safe else 'BLOCK'}")
