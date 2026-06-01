"""Shared helpers used across every pattern example.

Keeping the boilerplate here lets each example file focus on the *pattern*
being taught rather than on client setup. Two things live in this module:

  * ``MODEL`` — the Claude model every example uses.
  * ``complete()`` — a one-line "prompt in, text out" wrapper around the
    Messages API, used by the workflow patterns (01–05) where tool use isn't
    the point.

The augmented-LLM (00) and autonomous-agent (06) examples deliberately call the
SDK directly instead of using ``complete()``, because the whole point of those
examples is the tool-use loop.
"""

import os

import anthropic

# Every example defaults to the most capable Claude model. For high-volume or
# latency-sensitive experimentation you can drop this to "claude-sonnet-4-6" or
# "claude-haiku-4-5" — the patterns are identical regardless of model.
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# Reads ANTHROPIC_API_KEY from the environment. Set it before running:
#   export ANTHROPIC_API_KEY="sk-ant-..."
client = anthropic.Anthropic()


def complete(prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
    """Send a single prompt and return Claude's text response.

    This is intentionally minimal: one user turn, no conversation history, no
    tools. It's the "augmented LLM call" reduced to its simplest form so the
    workflow examples can compose it like a function.
    """
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    # response.content is a list of blocks; for a plain prompt we just want the
    # text. Concatenate any text blocks and return them.
    return "".join(block.text for block in response.content if block.type == "text")
