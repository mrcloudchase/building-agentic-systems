"""02 · Routing — the simplest version.

Routing classifies an input, then sends it to a handler specialized for that
category. One call picks the label; a second call answers using that label's
prompt. The routes are fixed in code, which makes this a workflow, not an agent
— only *which* route runs is decided at runtime.

    message → [classify] → one of the routes → [specialized reply]

To change the routes — add, remove, or retune a category — you edit ROUTES.

Run it (pass any message, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 02-routing/routing.py
    python 02-routing/routing.py "The app crashes when I upload a photo"
"""

import os
import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = "I was double-charged for my subscription this month — can I get a refund?"

# Each route is a category → a specialized system prompt. Separate handlers mean
# you can tune one without affecting the others.
ROUTES = {
    "billing": "You are a billing specialist. Be precise about charges, refunds, "
    "and payment methods. Answer in under 4 sentences.",
    "technical": "You are a support engineer. Give clear, step-by-step "
    "troubleshooting. Answer in under 5 sentences.",
    "general": "You are a friendly support agent. Answer warmly in under 3 sentences.",
}


def ask(prompt: str, system: str | None = None) -> str:
    """Call the provider with one prompt (and optional system) and return text."""
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    msg = client.messages.create(**kwargs)
    return msg.content[0].text


def route(routes: dict, message: str) -> str:
    """Classify the message into one of the routes, then dispatch to it."""
    labels = ", ".join(routes)
    category = ask(
        f"Classify this message into one of: {labels}. "
        f"Reply with only the label.\n\nMessage: {message}"
    ).strip().lower()
    if category not in routes:
        category = next(iter(routes))  # fallback to the first route

    print(f"[routed to: {category}]")
    return ask(message, system=routes[category])


if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Message: {message}\n")
    print(route(ROUTES, message))
