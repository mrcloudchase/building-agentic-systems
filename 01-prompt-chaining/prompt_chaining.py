"""01 · Prompt Chaining — the simplest version.

Prompt chaining means: call the model, then call it again with the previous
answer fed into the next prompt. The order of steps is fixed in code, which is
what makes it a workflow rather than an agent.

Here we write a how-to technical doc in two chained calls:

    topic → [1: outline the steps] → [2: write the doc from the outline] → doc

The whole pattern is the handoff: `outline` (step 1's output) is pasted into
step 2's prompt.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 01-prompt-chaining/prompt_chaining.py
"""

import os

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")


def ask(prompt: str) -> str:
    """Send one prompt, return Claude's text. A single link in the chain."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


topic = "how to build and train a GPT-3-style large language model from scratch"

# Step 1: turn the topic into a numbered outline of the procedure.
outline = ask(f"List the steps as a short numbered outline for: {topic}")

# Step 2: expand that outline into a full how-to doc.
# This is the chain — step 1's output is the input to step 2.
doc = ask(
    "Write a clear how-to technical document from this outline. For each step, "
    "add a one-line explanation and any shell commands.\n\n"
    f"Outline:\n{outline}"
)

print("=== STEP 1: outline ===")
print(outline)
print("\n=== STEP 2: how-to doc ===")
print(doc)
