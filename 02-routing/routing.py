"""02 · Routing — classify the input, then dispatch to a specialized handler.

    pip install anthropic; export ANTHROPIC_API_KEY=sk-ant-...
    python 02-routing/routing.py
"""

import anthropic

client = anthropic.Anthropic()
def ask(p, system="You are a helpful assistant."): return client.messages.create(model="claude-opus-4-8", max_tokens=1024, system=system, messages=[{"role": "user", "content": p}]).content[0].text

routes = {"sales": "You are a sales rep.", "billing": "You are a billing specialist.",
          "technical": "You are a support engineer.", "careers": "You are a recruiter."}
email = "Could we set up a demo and talk about enterprise pricing?"
category = ask(f"Classify into one of {', '.join(routes)} — reply with one word:\n{email}").strip().lower()
print(f"[{category}]", ask(email, routes.get(category, "You are a helpful assistant.")))
