"""03 · Parallelization — run LLM calls concurrently, then aggregate.

Two flavors, both shown here with a thread pool to fan out the API calls:

  * SECTIONING — split into independent subtasks, run in parallel, combine.
  * VOTING     — run the same task several times, then apply a decision rule.

Run it:
    python 03-parallelization/parallelization.py
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from shared import complete  # noqa: E402


# --- Flavor 1: SECTIONING ---------------------------------------------------
# Three independent analyses of one product idea, each a focused subtask.

SECTIONS = {
    "market size": "Estimate the market size and demand. 2 sentences.",
    "technical feasibility": "Assess how hard this is to build. 2 sentences.",
    "competition": "Describe the competitive landscape. 2 sentences.",
}


def analyze_section(idea: str, dimension: str, instruction: str) -> tuple[str, str]:
    """Run one focused subtask. Returns (dimension, result)."""
    result = complete(f"Product idea: {idea}\n\nTask: {instruction}")
    return dimension, result


def sectioning(idea: str) -> str:
    """Fan out the independent sections in parallel, then assemble a report."""
    with ThreadPoolExecutor(max_workers=len(SECTIONS)) as pool:
        futures = [
            pool.submit(analyze_section, idea, dim, instr)
            for dim, instr in SECTIONS.items()
        ]
        results = dict(f.result() for f in futures)

    return "\n".join(f"## {dim}\n{results[dim]}" for dim in SECTIONS)


# --- Flavor 2: VOTING -------------------------------------------------------
# Ask the same yes/no question several times; flag if ANY reviewer objects.

NUM_VOTERS = 3


def one_vote(text: str) -> bool:
    """One independent safety review. Returns True if SAFE to publish."""
    verdict = complete(
        "You are a content reviewer. Is the following text safe to publish on a "
        "professional company blog? Answer with only SAFE or UNSAFE.\n\n"
        f"Text: {text}",
        max_tokens=8,
    )
    return verdict.strip().upper().startswith("SAFE")


def voting(text: str) -> bool:
    """Run several independent reviews in parallel.

    Decision rule: publish only if EVERY reviewer says SAFE. This makes the
    system conservative — a single objection blocks publication.
    """
    with ThreadPoolExecutor(max_workers=NUM_VOTERS) as pool:
        votes = list(pool.map(lambda _: one_vote(text), range(NUM_VOTERS)))

    print(f"  votes (True=safe): {votes}")
    return all(votes)


if __name__ == "__main__":
    print("=== SECTIONING ===")
    idea = "a subscription box that mails a new houseplant every month"
    print(f"Idea: {idea}\n")
    print(sectioning(idea))

    print("\n=== VOTING ===")
    text = "Our new release is faster and more reliable than ever. Try it today!"
    print(f"Text: {text}")
    safe = voting(text)
    print(f"  decision: {'PUBLISH' if safe else 'BLOCK'}")
