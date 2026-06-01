"""01 · Prompt Chaining — the simplest version.

Prompt chaining means: call the model, then call it again with the previous
answer fed into the next prompt. The order of steps is fixed in code, which is
what makes it a workflow rather than an agent.

Here we write a how-to technical doc in three chained calls:

    topic → [1: outline] → [2: write the doc] → [3: copy edit] → final doc

Each step also shows the model an exact Markdown template, so every run produces
the same shape of output instead of a different layout each time.

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
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# Format templates. Showing the model the exact Markdown shape we want keeps the
# output consistent from run to run (this is a tiny "few-shot" format example).

OUTLINE_FORMAT = """\
# How to <Topic>

## Prerequisites
- <prerequisite>

## Steps
1. <step title>
2. <step title>
3. <step title>
"""

DOC_FORMAT = """\
# How to <Topic>

> <one-sentence summary of what the reader will accomplish>

## Prerequisites
- <prerequisite>

## Steps

### 1. <step title>
<one or two sentences explaining the step.>

```bash
<command, if any>
```

### 2. <step title>
<...>

## Verification
- <how to confirm it worked>
"""


topic = "how to build and train a GPT-3-style large language model from scratch"

# Step 1: turn the topic into a numbered outline, in a fixed Markdown format.
outline = ask(
    f"List the steps as a numbered outline for: {topic}\n\n"
    f"Use exactly this Markdown format:\n\n{OUTLINE_FORMAT}"
)

# Step 2: expand that outline into a full how-to doc, in a fixed Markdown format.
# This is the chain — step 1's output is the input to step 2.
doc = ask(
    "Write a clear how-to technical document from this outline. For each step, "
    "add a one-line explanation and any shell commands.\n\n"
    f"Use exactly this Markdown format:\n\n{DOC_FORMAT}\n\n"
    f"Outline:\n{outline}"
)

# Step 3: copy edit the doc — step 2's output is the input to step 3.
final = ask(
    "Copy edit this technical document: fix grammar, spelling, and awkward "
    "phrasing, and make terminology consistent. Keep the Markdown structure and "
    "every command unchanged. Return only the edited document.\n\n"
    f"{doc}"
)

print("=== STEP 1: outline ===")
print(outline)
print("\n=== STEP 2: how-to doc ===")
print(doc)
print("\n=== STEP 3: copy-edited final doc ===")
print(final)
