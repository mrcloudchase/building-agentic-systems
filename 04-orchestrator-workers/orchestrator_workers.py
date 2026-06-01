"""04 · Orchestrator-Workers — the simplest version.

An orchestrator LLM decides, at runtime, how to break a task into subtasks; a
worker handles each subtask; the orchestrator then combines the results.

The key difference from parallelization (03): the subtasks are NOT fixed in
code. The orchestrator chooses them based on the input — so this works for *any*
prompt, not one hard-coded task.

    prompt → [orchestrator: split into subtasks] → [worker per subtask] → [synthesize] → result

This is one structured pass — decompose, delegate, synthesize. There's no acting
on the world and no feedback loop; a full agent (pattern 06) wraps this kind of
plan-and-delegate move inside a loop that runs tools and adapts.

Run it (pass any prompt, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 04-orchestrator-workers/orchestrator_workers.py
    python 04-orchestrator-workers/orchestrator_workers.py "Plan a 3-day trip to Tokyo"
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = "Write a practical guide to starting a podcast."


def ask(prompt: str, max_tokens: int = 2048) -> str:
    """Send one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def orchestrate(task: str) -> list[str]:
    """Decompose: the model splits the task into subtasks, chosen at runtime."""
    plan = ask(
        "Break this task into 3-5 focused subtasks that together accomplish it.\n\n"
        f"Task: {task}\n\n"
        "Reply with ONLY a JSON array of short subtask strings."
    )
    # Slice from the first '[' to the last ']' so stray prose or code fences
    # around the JSON don't break parsing.
    return json.loads(plan[plan.index("[") : plan.rindex("]") + 1])


def work(task: str, subtask: str) -> str:
    """Delegate: a worker completes one subtask of the larger task."""
    return ask(
        "You are completing one part of a larger task.\n"
        f"Overall task: {task}\n"
        f"Your subtask: {subtask}\n\n"
        "Complete only your subtask. Be concise."
    )


def synthesize(task: str, subtasks: list[str], results: list[str]) -> str:
    """Combine the workers' outputs into one cohesive result."""
    combined = "\n\n".join(f"## {s}\n{r}" for s, r in zip(subtasks, results))
    return ask(
        f"Combine these completed subtasks into one cohesive result for the task: "
        f"{task}\n\n{combined}",
        max_tokens=4096,
    )


def run(task: str) -> str:
    """The whole pattern, reusable for any prompt."""
    subtasks = orchestrate(task)
    print("Orchestrator split the task into:")
    for s in subtasks:
        print(f"  • {s}")

    with ThreadPoolExecutor() as pool:
        results = list(pool.map(lambda s: work(task, s), subtasks))

    return synthesize(task, subtasks, results)


if __name__ == "__main__":
    # Use a prompt passed on the command line, or fall back to a default.
    task = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Task: {task}\n")
    result = run(task)
    print("\n=== result ===")
    print(result)
