"""05 · Evaluator-Optimizer — the simplest version.

Two roles in a feedback loop: the optimizer writes a candidate, the evaluator
judges it against criteria and returns feedback, the optimizer revises. Repeat
until the evaluator says PASS or we hit the round limit.

    [write copy] → [compliance review] → PASS? → done
          ▲                                 │
          └────────── feedback ─────────────┘

Business use case: compliant marketing copy. The copy must meet a compliance +
quality rubric (required disclaimer, no prohibited claims, length, clear CTA);
the loop revises until it passes.

Run it (pass an offer, or use the default):
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 05-evaluator-optimizer/evaluator_optimizer.py
    python 05-evaluator-optimizer/evaluator_optimizer.py "a no-fee checking account"
"""

import os
import sys

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

DEFAULT_INPUT = "a high-yield savings account offering 4.5% APY"

# Loop config: how many rounds to allow, and what "compliant" means.
MAX_ROUNDS = 4
CRITERIA = (
    "1) under 30 words; "
    "2) includes the exact disclaimer 'APY is variable and subject to change.'; "
    "3) makes no guaranteed-return, 'risk-free', or 'best' claims; "
    "4) ends with a clear call to action."
)


def ask(prompt: str, max_tokens: int = 256) -> str:
    """Call the provider with one prompt and return the text."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def optimize(offer: str, previous: str | None, feedback: str | None) -> str:
    """Generate (or revise) the marketing copy for the offer."""
    if previous is None:
        prompt = f"Write a short marketing blurb for this offer.\n\nOffer: {offer}\n\nReturn only the blurb."
    else:
        prompt = (
            f"Offer: {offer}\n\n"
            f"Your previous blurb: {previous}\n\n"
            f"A compliance reviewer's feedback: {feedback}\n\n"
            "Rewrite the blurb to address the feedback. Return only the blurb."
        )
    return ask(prompt).strip().strip('"')


def evaluate(offer: str, copy: str) -> tuple[bool, str]:
    """Judge the copy against CRITERIA. Returns (passed, feedback)."""
    verdict = ask(
        "You are a strict marketing-compliance reviewer. Judge this copy against "
        "the criteria.\n\n"
        f"Offer: {offer}\n"
        f"Criteria: {CRITERIA}\n"
        f'Copy: "{copy}"\n\n'
        "Respond on a single line as either:\n"
        "  PASS\n"
        "  FAIL: <one sentence of specific, actionable feedback>"
    ).strip()
    passed = verdict.upper().startswith("PASS")
    feedback = "" if passed else verdict.split(":", 1)[-1].strip()
    return passed, feedback


def run(offer: str) -> str:
    """Loop: optimize, evaluate, repeat until PASS or MAX_ROUNDS."""
    copy: str | None = None
    feedback: str | None = None

    for round_num in range(1, MAX_ROUNDS + 1):
        copy = optimize(offer, copy, feedback)
        print(f"Round {round_num} — copywriter: {copy!r}")

        passed, feedback = evaluate(offer, copy)
        if passed:
            print(f"Round {round_num} — compliance: PASS\n")
            return copy
        print(f"Round {round_num} — compliance: FAIL — {feedback}\n")

    print("Hit the round limit; returning best effort.\n")
    return copy or ""


if __name__ == "__main__":
    offer = " ".join(sys.argv[1:]) or DEFAULT_INPUT
    print(f"Offer: {offer}\n")
    final = run(offer)
    print("--- final copy ---")
    print(final)
