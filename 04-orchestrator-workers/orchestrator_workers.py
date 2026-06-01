"""04 · Orchestrator-Workers — the model splits the task, workers do each part, then synthesize.

    pip install anthropic; export ANTHROPIC_API_KEY=sk-ant-...
    python 04-orchestrator-workers/orchestrator_workers.py
"""

import json
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()
def ask(p): return client.messages.create(model="claude-opus-4-8", max_tokens=4096, messages=[{"role": "user", "content": p}]).content[0].text

request = "Assess the market opportunity for an AI meal-planning app for busy families."
plan = ask(f"Break this into 3-5 research angles. Reply with ONLY a JSON array of strings.\n\n{request}")
angles = json.loads(plan[plan.index("["):plan.rindex("]") + 1])  # subtasks chosen at runtime
def work(angle): return f"## {angle}\n" + ask(f"Research this angle of the request '{request}': {angle}")
with ThreadPoolExecutor() as pool:
    sections = list(pool.map(work, angles))
print(ask(f"Combine these into one market brief for '{request}':\n\n" + "\n\n".join(sections)))
