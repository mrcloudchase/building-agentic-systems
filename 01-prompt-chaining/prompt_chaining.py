"""01 · Prompt Chaining — the simplest version.

Prompt chaining means: call the model, then call it again with the previous
answer fed into the next prompt. Here the chain is just *data* — a list of steps
— and the engine is a small loop that feeds each step's output into the next.

    topic → [step 1] → [step 2] → [step 3] → result

To change the chain — add, remove, or reorder steps — you edit STEPS. The loop
never changes. This example turns a topic into a polished how-to doc:
outline → write the doc → copy edit.

Run it (pass any topic, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 01-prompt-chaining/prompt_chaining.py
    python 01-prompt-chaining/prompt_chaining.py "how to deploy a Django app to AWS"
"""

import os
import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")


def ask(prompt: str, max_tokens: int = 4096) -> str:
    """Send one prompt, return Claude's text. One link in the chain."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# The chain, defined as data. Each step is one LLM call; "{input}" is filled with
# the previous step's output (or the topic, for the first step). `max_tokens`
# lets the long doc-writing steps have more room than the short outline.
STEPS = [
    {
        "name": "outline",
        "prompt": "Write a short numbered outline of the steps for: {input}",
        "max_tokens": 1024,
    },
    {
        "name": "write",
        "prompt": (
            "Write a complete how-to technical document from this outline. Use "
            "Markdown: a one-line summary, a '## Prerequisites' list, numbered "
            "'## Steps' each with a sentence and any shell commands in fenced "
            "code blocks, and a '## Verification' section.\n\n{input}"
        ),
        "max_tokens": 16000,
    },
    {
        "name": "copy edit",
        "prompt": (
            "Copy edit this document: fix grammar and awkward phrasing and make "
            "terminology consistent. Keep the Markdown structure and every "
            "command unchanged. Return only the edited document.\n\n{input}"
        ),
        "max_tokens": 16000,
    },
]


def run(topic: str) -> str:
    """Run the chain: loop the steps, feeding each output into the next."""
    text = topic
    for step in STEPS:
        prompt = step["prompt"].format(input=text)
        text = ask(prompt, max_tokens=step.get("max_tokens", 4096))
        print(f"=== {step['name']} ===")
        print(f"{text}\n")
    return text


if __name__ == "__main__":
    # Use a topic passed on the command line, or fall back to a default.
    topic = " ".join(sys.argv[1:]) or (
        "how to build and train a GPT-3-style large language model from scratch"
    )
    print(f"Topic: {topic}\n")
    run(topic)
