"""02 · Routing — the simplest version.

Routing classifies an input, then sends it to a handler specialized for that
category. A first call picks the label; a second call answers using the prompt
for that label. The set of routes is fixed in code, which makes this a workflow,
not an agent — only *which* path runs is decided at runtime.

    message → [classify] → billing | technical | general → [specialized reply]

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 02-routing/routing.py
"""

import os

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")


def ask(prompt: str, system: str | None = None) -> str:
    """Send one prompt (with an optional system prompt) and return the text."""
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    msg = client.messages.create(**kwargs)
    return msg.content[0].text


# Each route is a category → a specialized system prompt. Because the handlers
# are separate, you can tune one without affecting the others.
ROUTES = {
    "billing": "You are a billing specialist. Be precise about charges, refunds, "
    "and payment methods. Answer in under 4 sentences.",
    "technical": "You are a support engineer. Give clear, step-by-step "
    "troubleshooting. Answer in under 5 sentences.",
    "general": "You are a friendly support agent. Answer warmly in under 3 sentences.",
}


def handle(message: str) -> str:
    # Step 1: classify the message into one of the route labels.
    category = ask(
        "Classify this support message into one word — billing, technical, or "
        f"general. Reply with only the word.\n\nMessage: {message}"
    ).strip().lower()
    if category not in ROUTES:
        category = "general"  # fallback if the model returns something unexpected

    # Step 2: dispatch to the specialized handler for that category.
    print(f"  [routed to: {category}]")
    return ask(message, system=ROUTES[category])


messages = [
    "I was double-charged for my subscription this month — can I get a refund?",
    "The app crashes every time I try to upload a photo.",
    "What are your support hours?",
]

for message in messages:
    print(f"\nMessage: {message}")
    print(f"  {handle(message)}")
