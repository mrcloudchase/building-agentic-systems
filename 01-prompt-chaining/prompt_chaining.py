"""01 · Prompt Chaining — a fixed sequence of LLM calls with a gate.

We turn a topic into polished marketing copy in three steps:

    generate draft  →  GATE (length check)  →  polish

The "gate" is plain Python that decides whether the chain continues. If the
draft is too long, we stop early rather than spend a call polishing it.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 01-prompt-chaining/prompt_chaining.py
"""

import os

import anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def complete(prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
    """Send a single prompt and return Claude's text response.

    The "augmented LLM call" reduced to a function we can compose into a chain.
    """
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return "".join(b.text for b in response.content if b.type == "text")


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
