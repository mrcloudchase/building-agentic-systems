"""04 · Orchestrator-Workers — the simplest version.

An orchestrator LLM decides, at runtime, how to break a task into subtasks; a
worker handles each subtask; the orchestrator then combines the results.

The subtasks are NOT fixed in code — the orchestrator chooses them based on the
input, so this works for *any* request, not one hard-coded task.

    request → [orchestrator: pick research angles] → [worker per angle] → [synthesize] → brief

Business use case: an automated market / due-diligence research brief. The
relevant angles (market size, competitors, regulation, risks...) depend on the
request, so the orchestrator picks them at runtime.

Run it (pass a request, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 04-orchestrator-workers/orchestrator_workers.py
    python 04-orchestrator-workers/orchestrator_workers.py "Diligence on a B2B payroll startup"
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = (
    "Assess the market opportunity for an AI-powered meal-planning app for busy "
    "families."
)


def ask(prompt: str, max_tokens: int = 2048) -> str:
    """Call the provider with one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def orchestrate(request: str) -> list[str]:
    """Decompose: the model picks the research angles, chosen at runtime."""
    plan = ask(
        "You are a research lead planning a market/due-diligence brief. Break "
        f"this request into 3-5 focused research angles.\n\nRequest: {request}\n\n"
        "Reply with ONLY a JSON array of short angle titles."
    )
    # Slice from the first '[' to the last ']' so stray prose or code fences
    # around the JSON don't break parsing.
    return json.loads(plan[plan.index("[") : plan.rindex("]") + 1])


def work(request: str, angle: str) -> str:
    """Delegate: a worker researches one angle of the brief."""
    return ask(
        "You are a research analyst contributing one section of a brief.\n"
        f"Overall request: {request}\n"
        f"Your research angle: {angle}\n\n"
        "Write a concise, factual paragraph (3-4 sentences) on this angle."
    )


def synthesize(request: str, angles: list[str], results: list[str]) -> str:
    """Combine the workers' sections into one coherent brief."""
    combined = "\n\n".join(f"## {a}\n{r}" for a, r in zip(angles, results))
    return ask(
        "Combine these researched sections into one coherent market/due-diligence "
        f"brief for: {request}. Add a one-line executive summary at the top.\n\n"
        f"{combined}",
        max_tokens=4096,
    )


def run(request: str) -> str:
    """The whole pattern, reusable for any request."""
    angles = orchestrate(request)
    print("Orchestrator chose these research angles:")
    for a in angles:
        print(f"  • {a}")

    with ThreadPoolExecutor() as pool:
        results = list(pool.map(lambda a: work(request, a), angles))

    return synthesize(request, angles, results)


if __name__ == "__main__":
    # Use a request passed on the command line, or fall back to a default.
    request = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Request: {request}\n")
    brief = run(request)
    print("\n=== brief ===")
    print(brief)
