"""04 · Orchestrator-Workers — dynamically split work, delegate, synthesize.

Unlike parallelization (where WE fix the subtasks), here the ORCHESTRATOR
decides the subtasks at runtime based on the input:

    topic → [orchestrator picks subtopics] → [worker per subtopic] → [synthesize]

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 04-orchestrator-workers/orchestrator_workers.py
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor

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


def orchestrate(topic: str) -> list[str]:
    """The orchestrator decides how to break the task down.

    We ask for a JSON array of subtopics so the plan is structured and
    inspectable. The number and content of subtopics is the model's call — we
    don't know it in advance.
    """
    raw = complete(
        f"You are planning a short research brief on: {topic}\n\n"
        "List 3 focused subtopics that together would make a well-rounded brief. "
        'Respond with ONLY a JSON array of strings, e.g. ["a", "b", "c"].',
        max_tokens=256,
    )
    try:
        subtopics = json.loads(raw)
        if isinstance(subtopics, list) and subtopics:
            return [str(s) for s in subtopics]
    except json.JSONDecodeError:
        pass
    # Fallback so the demo still runs if parsing fails.
    return [topic]


def work(topic: str, subtopic: str) -> tuple[str, str]:
    """A worker researches one subtopic. Returns (subtopic, findings)."""
    findings = complete(
        f"Write a concise, factual paragraph (3-4 sentences) about '{subtopic}' "
        f"in the context of '{topic}'."
    )
    return subtopic, findings


def synthesize(topic: str, sections: dict[str, str]) -> str:
    """The orchestrator combines the workers' outputs into one brief."""
    body = "\n\n".join(f"### {sub}\n{text}" for sub, text in sections.items())
    return complete(
        f"Combine these researched sections into a single coherent research brief "
        f"on '{topic}'. Add a one-sentence intro and a one-sentence conclusion. "
        f"Keep the section content intact.\n\n{body}",
        max_tokens=1200,
    )


def run(topic: str) -> str:
    print("Phase 1 — orchestrate (decide subtopics)")
    subtopics = orchestrate(topic)
    for s in subtopics:
        print(f"  • {s}")

    print("\nPhase 2 — workers (research each subtopic in parallel)")
    with ThreadPoolExecutor(max_workers=len(subtopics)) as pool:
        sections = dict(pool.map(lambda s: work(topic, s), subtopics))
    print(f"  {len(sections)} sections researched.")

    print("\nPhase 3 — synthesize")
    return synthesize(topic, sections)


if __name__ == "__main__":
    topic = "the impact of urban green roofs on city heat"
    print(f"Topic: {topic}\n")
    brief = run(topic)
    print("\n--- research brief ---")
    print(brief)
