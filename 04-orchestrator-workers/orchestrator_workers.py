"""04 · Orchestrator-Workers — the simplest version.

An orchestrator LLM decides, at runtime, how to break a task into subtasks; a
worker handles each subtask; the orchestrator then combines the results.

The key difference from parallelization (03): the subtasks are NOT fixed in
code. The orchestrator chooses them based on the input, so a different question
produces a different set of sub-questions.

    question → [orchestrator splits into sub-questions] → [worker answers each] → [synthesize]

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


question = (
    "What would it take for a startup to train a GPT-3-scale language model "
    "from scratch today?"
)

# Step 1 — ORCHESTRATE: the model splits the question into sub-questions. We
# don't hard-code them; how many and which ones depend on this question.
plan = ask(
    "Break this question into 3-4 focused sub-questions that, answered together, "
    f"would fully address it.\n\nQuestion: {question}\n\n"
    'Reply with ONLY a JSON array of sub-question strings.'
)
# Slice from the first '[' to the last ']' so stray prose or code fences around
# the JSON don't break parsing.
subquestions = json.loads(plan[plan.index("[") : plan.rindex("]") + 1])

print("Orchestrator split the question into:")
for q in subquestions:
    print(f"  • {q}")


# Step 2 — WORKERS: one worker answers each sub-question (run in parallel).
def work(subquestion: str) -> str:
    return ask(f"Answer this sub-question concisely in 3-4 sentences:\n{subquestion}")


with ThreadPoolExecutor() as pool:
    answers = list(pool.map(work, subquestions))

# Step 3 — SYNTHESIZE: the orchestrator integrates the answers into one response.
research = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in zip(subquestions, answers))
final = ask(
    "Using these researched sub-answers, write a clear, integrated answer to the "
    f"original question: {question}\n\n{research}",
    max_tokens=4096,
)

print("\n=== integrated answer ===")
print(final)
