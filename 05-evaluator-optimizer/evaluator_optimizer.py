"""05 · Evaluator-Optimizer — the simplest version.

Two roles in a feedback loop: the optimizer writes a candidate, the evaluator
judges it against criteria and returns feedback, the optimizer revises. Repeat
until the evaluator says PASS or we hit the round limit.

    [optimizer writes] → [evaluator judges] → PASS? → done
          ▲                                      │
          └──────────── feedback ────────────────┘

Run it (pass a brief, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 05-evaluator-optimizer/evaluator_optimizer.py
    python 05-evaluator-optimizer/evaluator_optimizer.py "a budget travel backpack"
"""

import os
import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = "a reusable water bottle that filters tap water as you drink"

# Loop config: how many rounds to allow, and what "good" means.
MAX_ROUNDS = 4
CRITERIA = (
    "1) at most 8 words; "
    "2) names a concrete user benefit; "
    "3) contains no clichés like 'game-changer', 'next-level', or 'revolutionary'."
)


def ask(prompt: str, max_tokens: int = 256) -> str:
    """Call the provider with one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def optimize(brief: str, previous: str | None, feedback: str | None) -> str:
    """Generate (or revise) a tagline for the brief."""
    if previous is None:
        prompt = f"Write a product tagline.\n\nBrief: {brief}\n\nReturn only the tagline."
    else:
        prompt = (
            f"Brief: {brief}\n\n"
            f"Your previous tagline: {previous}\n\n"
            f"An editor's feedback: {feedback}\n\n"
            "Write an improved tagline addressing the feedback. Return only the tagline."
        )
    return ask(prompt).strip().strip('"')


def evaluate(brief: str, tagline: str) -> tuple[bool, str]:
    """Judge the tagline against CRITERIA. Returns (passed, feedback)."""
    verdict = ask(
        "You are a strict tagline editor. Judge this tagline against the criteria.\n\n"
        f"Brief: {brief}\n"
        f"Criteria: {CRITERIA}\n"
        f'Tagline: "{tagline}"\n\n'
        "Respond on a single line as either:\n"
        "  PASS\n"
        "  FAIL: <one sentence of specific, actionable feedback>"
    ).strip()
    passed = verdict.upper().startswith("PASS")
    feedback = "" if passed else verdict.split(":", 1)[-1].strip()
    return passed, feedback


def run(brief: str) -> str:
    """Loop: optimize, evaluate, repeat until PASS or MAX_ROUNDS."""
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
    brief = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Brief: {brief}\n")
    final = run(brief)
    print("--- final tagline ---")
    print(final)
