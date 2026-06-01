"""01 · Prompt Chaining — a fixed sequence of LLM calls with a gate.

We turn a topic into polished marketing copy in three steps:

    generate draft  →  GATE (length check)  →  polish

The "gate" is plain Python that decides whether the chain continues. If the
draft is too long, we stop early rather than spend a call polishing it.

Run it:
    python 01-prompt-chaining/prompt_chaining.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from shared import complete  # noqa: E402

MAX_DRAFT_WORDS = 80  # the gate's threshold


def step_generate(topic: str) -> str:
    """Step 1: produce a first-draft blurb from the topic."""
    return complete(
        f"Write a short marketing blurb (3-4 sentences) for: {topic}. "
        "Plain prose, no headings."
    )


def gate_length_ok(draft: str) -> bool:
    """The gate: a programmatic check between steps.

    Returns True if the draft is within budget. A real gate might check for
    required sections, banned words, or call another LLM to score quality.
    """
    word_count = len(draft.split())
    print(f"  [gate] draft is {word_count} words (limit {MAX_DRAFT_WORDS})")
    return word_count <= MAX_DRAFT_WORDS


def step_polish(draft: str) -> str:
    """Step 3: refine the approved draft into punchy final copy."""
    return complete(
        "Rewrite this marketing blurb to be punchier and more vivid, keeping it "
        f"roughly the same length:\n\n{draft}"
    )


def run_chain(topic: str) -> str | None:
    """Run the full chain. Returns None if the gate stops it."""
    print("Step 1 — generate draft")
    draft = step_generate(topic)
    print(f"  {draft}\n")

    print("Step 2 — gate")
    if not gate_length_ok(draft):
        print("  [gate] FAILED — stopping the chain early.\n")
        return None
    print("  [gate] passed.\n")

    print("Step 3 — polish")
    final = step_polish(draft)
    print(f"  {final}\n")
    return final


if __name__ == "__main__":
    topic = "a noise-cancelling travel mug that keeps coffee hot for 6 hours"
    print(f"Topic: {topic}\n")

    result = run_chain(topic)

    print("--- result ---")
    print(result if result is not None else "(chain halted at the gate)")
