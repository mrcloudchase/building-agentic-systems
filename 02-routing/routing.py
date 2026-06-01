"""02 · Routing — classify the input, then hand it to a specialized handler.

A support-triage workflow:

    message → [router classifies] → billing | technical | general handler

The router is constrained to return exactly one valid label, so the routing
decision is clean. Each handler has its own focused system prompt.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 02-routing/routing.py
"""

import os

import anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def complete(prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
    """Send a single prompt and return Claude's text response."""
    kwargs: dict = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system is not None:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return "".join(b.text for b in response.content if b.type == "text")


# Each route has a system prompt tuned for that category. This is the payoff of
# routing: focused prompts that can be improved independently.
HANDLERS = {
    "billing": "You are a billing specialist. Be precise about charges, refunds, "
    "and payment methods. Keep answers under 4 sentences.",
    "technical": "You are a senior technical support engineer. Give clear, "
    "step-by-step troubleshooting. Keep answers under 5 sentences.",
    "general": "You are a friendly support generalist. Answer warmly and "
    "concisely in under 3 sentences.",
}


def route(message: str) -> str:
    """Classify the message into one of the handler categories.

    We instruct the model to reply with ONLY the label, then defensively
    normalize and validate it so a stray word can't break routing.
    """
    raw = complete(
        "Classify the customer message into exactly one category. "
        "Reply with only the lowercase category word, nothing else.\n"
        "Categories: billing, technical, general\n\n"
        f"Message: {message}",
        max_tokens=16,
    )
    label = raw.strip().lower()
    if label not in HANDLERS:
        # Fall back to 'general' if the model returned something unexpected.
        label = "general"
    return label


def handle(message: str) -> str:
    """Route the message, then answer it with the chosen handler."""
    category = route(message)
    print(f"  [router] → {category}")
    return complete(message, system=HANDLERS[category])


if __name__ == "__main__":
    messages = [
        "I was charged twice for my subscription this month — can I get a refund?",
        "The app crashes every time I try to upload a photo. How do I fix it?",
        "What are your support hours?",
    ]

    for msg in messages:
        print(f"\nMessage: {msg}")
        answer = handle(msg)
        print(f"  [answer] {answer}")
