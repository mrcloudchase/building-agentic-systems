"""05 · Evaluator-Optimizer — generate, critique, revise, repeat.

One role writes a tagline; another judges it against explicit criteria and
returns feedback. The loop runs until the evaluator says PASS or we hit the
round limit.

    [optimizer writes] → [evaluator judges] → PASS? → done
          ▲                                      │
          └──────────── feedback ────────────────┘

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 05-evaluator-optimizer/evaluator_optimizer.py
"""

import os

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


MAX_ROUNDS = 4

CRITERIA = (
    "1) at most 8 words; "
    "2) names a concrete user benefit; "
    "3) contains no clichés like 'game-changer', 'next-level', or 'revolutionary'."
)


def optimize(brief: str, previous: str | None, feedback: str | None) -> str:
    """The optimizer writes (or revises) a tagline."""
    if previous is None:
        prompt = f"Write a product tagline.\n\nBrief: {brief}\n\nReturn only the tagline."
    else:
        prompt = (
            f"Brief: {brief}\n\n"
            f"Your previous tagline: {previous}\n\n"
            f"An editor's feedback: {feedback}\n\n"
            "Write an improved tagline addressing the feedback. Return only the tagline."
        )
    return complete(prompt, max_tokens=64).strip().strip('"')


def evaluate(brief: str, tagline: str) -> tuple[bool, str]:
    """The evaluator judges the tagline. Returns (passed, feedback)."""
    verdict = complete(
        f"You are a strict tagline editor. Judge this tagline against the criteria.\n\n"
        f"Brief: {brief}\n"
        f"Criteria: {CRITERIA}\n"
        f'Tagline: "{tagline}"\n\n'
        "Respond on a single line as either:\n"
        "  PASS\n"
        "  FAIL: <one sentence of specific, actionable feedback>",
        max_tokens=128,
    ).strip()

    passed = verdict.upper().startswith("PASS")
    feedback = "" if passed else verdict.split(":", 1)[-1].strip()
    return passed, feedback


def run(brief: str) -> str:
    tagline: str | None = None
    feedback: str | None = None

    for round_num in range(1, MAX_ROUNDS + 1):
        tagline = optimize(brief, tagline, feedback)
        print(f"Round {round_num} — optimizer: {tagline!r}")

        passed, feedback = evaluate(brief, tagline)
        if passed:
            print(f"Round {round_num} — evaluator: PASS\n")
            return tagline
        print(f"Round {round_num} — evaluator: FAIL — {feedback}\n")

    print("Hit the round limit; returning best effort.\n")
    return tagline or ""


if __name__ == "__main__":
    brief = "a reusable water bottle that filters tap water as you drink"
    print(f"Brief: {brief}\n")
    final = run(brief)
    print("--- final tagline ---")
    print(final)
