"""01 · Prompt Chaining — each step's output feeds the next prompt.

    pip install anthropic; export ANTHROPIC_API_KEY=sk-ant-...
    python 01-prompt-chaining/prompt_chaining.py
"""

import anthropic

client = anthropic.Anthropic()
def ask(p): return client.messages.create(model="claude-opus-4-8", max_tokens=4096, messages=[{"role": "user", "content": p}]).content[0].text

steps = ["Write a numbered outline of the steps for: {}",
         "Write a how-to technical doc (Markdown) from this outline:\n{}",
         "Copy edit this document, keeping its structure and commands:\n{}"]
text = "how to build and train a GPT-3-style LLM from scratch"
for step in steps:
    text = ask(step.format(text)); print(text, "\n")
