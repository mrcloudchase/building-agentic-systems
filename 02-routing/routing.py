"""02 · Routing — the simplest version.

Routing classifies an input, then sends it to a handler specialized for that
category. One call picks the label; a second call answers using that label's
prompt. The routes are fixed in code, which makes this a workflow, not an agent
— only *which* route runs is decided at runtime.

    email → [classify] → one of the routes → [specialized reply]

Business use case: triage a shared inbox — classify each incoming email and hand
it to the team best suited to handle it. To change the routes — add, remove, or
retune a category — you edit ROUTES.

Run it (pass an email, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 02-routing/routing.py
    python 02-routing/routing.py "The export button returns a 500 error."
"""

import os
import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = (
    "Hi, we're a 50-person company evaluating tools like yours. Could we set up a "
    "demo and talk about enterprise pricing?"
)

# Each route is a category → a specialized system prompt. Separate handlers mean
# you can tune one without affecting the others.
ROUTES = {
    "sales": "You are a sales rep. Reply enthusiastically and propose a concrete "
    "next step such as a demo or a call. Answer in under 4 sentences.",
    "billing": "You are a billing specialist. Be precise about charges, refunds, "
    "and invoices. Answer in under 4 sentences.",
    "technical": "You are a support engineer. Give clear, step-by-step "
    "troubleshooting. Answer in under 5 sentences.",
    "careers": "You are a recruiter. Thank the applicant and point them to the "
    "next step in the hiring process. Answer in under 3 sentences.",
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
        f"Classify this email into one of: {labels}. "
        f"Reply with only the label.\n\nEmail: {message}"
    ).strip().lower()
    if category not in routes:
        category = next(iter(routes))  # fallback to the first route

    print(f"[routed to: {category}]")
    return ask(message, system=routes[category])


if __name__ == "__main__":
    email = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Email: {email}\n")
    print(route(ROUTES, email))
