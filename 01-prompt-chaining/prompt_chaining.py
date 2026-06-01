"""01 · Prompt Chaining — the simplest version.

Prompt chaining means: call the model, then call it again with the previous
answer fed into the next prompt. Here the chain is just *data* (a list of steps)
and the engine is a small loop that feeds each step's output into the next.

    ticket → [extract facts] → [draft reply] → [polish to brand voice] → reply

Business use case: turn a raw customer support ticket into a polished, on-brand
reply. To change the chain — add, remove, or reorder steps — you edit STEPS.

Run it (pass a ticket, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 01-prompt-chaining/prompt_chaining.py
    python 01-prompt-chaining/prompt_chaining.py "My invoice looks wrong this month."
"""

import os
import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = (
    "Hi — I ordered a blender (order #12345) two weeks ago and it still hasn't "
    "arrived. Tracking hasn't updated in 5 days. I'm frustrated; can you tell me "
    "where it is or just refund me?"
)

# The chain, defined as data. "{input}" is filled with the previous step's
# output (or the initial input, for the first step).
STEPS = [
    {
        "name": "extract",
        "prompt": "Extract the customer's core issue and the key facts (order "
        "numbers, dates, what they want) from this support ticket as a short "
        "bullet list.\n\nTicket: {input}",
    },
    {
        "name": "draft",
        "prompt": "Write a helpful first-draft support reply that addresses each "
        "of these points and proposes a concrete next step.\n\n{input}",
    },
    {
        "name": "polish",
        "prompt": "Rewrite this reply in a warm, professional brand voice. Keep "
        "it concise, apologize once if appropriate, and sign off as 'The Acme "
        "Support Team'.\n\n{input}",
    },
]


def ask(prompt: str, max_tokens: int = 1024) -> str:
    """Call the provider with one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def run(steps: list[dict], text: str) -> str:
    """Loop the steps, feeding each step's output into the next."""
    for step in steps:
        text = ask(step["prompt"].format(input=text), step.get("max_tokens", 1024))
        print(f"=== {step['name']} ===")
        print(f"{text}\n")
    return text


if __name__ == "__main__":
    ticket = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Ticket: {ticket}\n")
    run(STEPS, ticket)
