"""01 · Prompt Chaining — a fixed sequence of LLM calls, each feeding the next.

Prompt chaining decomposes a task into a sequence of steps where *each LLM call
processes the output of the previous one*. The order of steps is fixed in code —
that's what makes it a workflow, not an agent.

This mirrors the article's example ("generate marketing copy, then translate
it") extended to three links. Each step produces a genuinely different artifact
and hands it to the next:

    brief → [1: write copy] → [2: translate] → [3: shorten to a post] → output

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 01-prompt-chaining/prompt_chaining.py
"""

import os

import anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def complete(prompt: str, max_tokens: int = 1024) -> str:
    """Send one prompt and return Claude's text — a single link in the chain."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


# --- Each step is one LLM call that transforms the previous step's output ---


def write_copy(brief: str) -> str:
    """Step 1: product brief → English marketing blurb."""
    return complete(
        "Write a vivid 2-3 sentence marketing blurb for this product. "
        f"Return only the blurb.\n\nProduct: {brief}"
    )


def translate(blurb: str) -> str:
    """Step 2: English blurb → Spanish (takes step 1's output)."""
    return complete(
        "Translate this marketing blurb into natural, fluent Spanish. "
        f"Return only the translation.\n\n{blurb}"
    )


def shorten_to_post(spanish_blurb: str) -> str:
    """Step 3: Spanish blurb → short social post (takes step 2's output)."""
    return complete(
        "Rewrite this as a social media post under 200 characters, ending with "
        f"two relevant hashtags. Return only the post.\n\n{spanish_blurb}"
    )


def run_chain(brief: str) -> str:
    """Run the chain. The output of each step is the input to the next."""
    print("Step 1 — write copy (brief → English blurb)")
    blurb = write_copy(brief)
    print(f"  {blurb}\n")

    print("Step 2 — translate (English blurb → Spanish)")
    spanish = translate(blurb)
    print(f"  {spanish}\n")

    print("Step 3 — shorten (Spanish blurb → social post)")
    post = shorten_to_post(spanish)
    print(f"  {post}\n")

    return post


if __name__ == "__main__":
    brief = "a noise-cancelling travel mug that keeps coffee hot for 6 hours"
    print(f"Brief: {brief}\n")
    result = run_chain(brief)
    print("--- final output ---")
    print(result)
