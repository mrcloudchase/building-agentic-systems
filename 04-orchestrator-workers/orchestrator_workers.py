"""04 · Orchestrator-Workers — the simplest version.

An orchestrator LLM decides, at runtime, how to break a task into subtasks; a
worker handles each subtask; the orchestrator then combines the results.

The key difference from parallelization (03): the subtasks are NOT fixed in
code. The orchestrator chooses them based on the input, so a different task
produces a different set of subtasks.

    task → [orchestrator picks subtasks] → [worker per subtask] → [synthesize]

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 04-orchestrator-workers/orchestrator_workers.py
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")


def ask(prompt: str, max_tokens: int = 2048) -> str:
    """Send one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


task = "Write a short briefing on whether a small startup should build its own LLM."

# Step 1 — ORCHESTRATE: the model decides the subtasks. We don't hard-code them;
# they come back as a JSON list chosen for this specific task.
plan = ask(
    f"Break this task into 3-4 focused subtasks.\n\nTask: {task}\n\n"
    'Reply with ONLY a JSON array of short subtask strings, e.g. ["a", "b"].'
)
# Slice from the first '[' to the last ']' so stray prose or code fences around
# the JSON don't break parsing.
subtasks = json.loads(plan[plan.index("[") : plan.rindex("]") + 1])

print("Orchestrator chose these subtasks:")
for s in subtasks:
    print(f"  • {s}")


# Step 2 — WORKERS: one worker handles each subtask (run in parallel).
def work(subtask: str) -> str:
    return ask(f"Write a concise paragraph covering this subtask of '{task}':\n{subtask}")


with ThreadPoolExecutor() as pool:
    sections = list(pool.map(work, subtasks))

# Step 3 — SYNTHESIZE: the orchestrator combines the workers' outputs.
combined = "\n\n".join(f"## {s}\n{text}" for s, text in zip(subtasks, sections))
briefing = ask(
    f"Combine these sections into one coherent briefing on '{task}'. "
    f"Add a one-sentence intro and conclusion; keep the content.\n\n{combined}",
    max_tokens=4096,
)

print("\n=== briefing ===")
print(briefing)
