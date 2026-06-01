"""04 · Orchestrator-Workers — the simplest version.

An orchestrator LLM decides, at runtime, how to break a task into subtasks; a
worker handles each subtask; the orchestrator then combines the results.

The key difference from parallelization (03): the subtasks are NOT fixed in
code. The orchestrator chooses them based on the input, so a different feature
produces a different plan.

    feature request → [orchestrator plans subtasks] → [worker details each] → [synthesize plan]

This is one structured pass — decompose, delegate, synthesize. There's no acting
on a real codebase and no test feedback; a full coding agent (pattern 06) wraps
this kind of plan-and-delegate move inside a loop that runs tools and adapts.

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


feature = (
    "Add rate limiting to a public REST API so each API key is capped at "
    "100 requests per minute."
)

# Step 1 — ORCHESTRATE: break the feature into implementation subtasks. This IS
# the plan. We don't hard-code the subtasks; how many and which ones depend on
# the feature.
plan = ask(
    "You are a tech lead. Break this feature into 3-5 concrete implementation "
    f"subtasks.\n\nFeature: {feature}\n\n"
    "Reply with ONLY a JSON array of short subtask titles."
)
# Slice from the first '[' to the last ']' so stray prose or code fences around
# the JSON don't break parsing.
subtasks = json.loads(plan[plan.index("[") : plan.rindex("]") + 1])

print("Orchestrator's plan (subtasks):")
for t in subtasks:
    print(f"  • {t}")


# Step 2 — WORKERS: one worker fleshes out each subtask (run in parallel).
def work(subtask: str) -> str:
    return ask(
        f"Feature: {feature}\nSubtask: {subtask}\n\n"
        "Explain how to implement this subtask in 3-4 sentences, with a short "
        "code sketch if helpful."
    )


with ThreadPoolExecutor() as pool:
    details = list(pool.map(work, subtasks))

# Step 3 — SYNTHESIZE: combine the workers' output into one ordered plan.
sections = "\n\n".join(f"## {t}\n{d}" for t, d in zip(subtasks, details))
final = ask(
    f"Combine these worked-out subtasks into a single, ordered implementation "
    f"plan for: {feature}. Add a one-line summary at the top and order the steps "
    f"sensibly.\n\n{sections}",
    max_tokens=4096,
)

print("\n=== implementation plan ===")
print(final)
