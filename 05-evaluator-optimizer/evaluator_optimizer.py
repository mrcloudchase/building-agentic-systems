"""05 · Evaluator-Optimizer — generate, critique against criteria, revise until it passes.

    pip install anthropic; export ANTHROPIC_API_KEY=sk-ant-...
    python 05-evaluator-optimizer/evaluator_optimizer.py
"""

import anthropic

client = anthropic.Anthropic()
def ask(p): return client.messages.create(model="claude-opus-4-8", max_tokens=512, messages=[{"role": "user", "content": p}]).content[0].text

offer = "a high-yield savings account offering 4.5% APY"
criteria = "under 30 words; includes 'APY is variable and subject to change.'; no 'risk-free' or guaranteed-return claims; clear call to action"
copy = feedback = ""
for _ in range(4):
    copy = ask(f"Write marketing copy for: {offer}.\nIt must satisfy: {criteria}.\nPrevious attempt: {copy}\nReviewer feedback: {feedback}\nReturn only the copy.")
    verdict = ask(f"Judge this copy against [{criteria}]. Reply 'PASS' or 'FAIL: <one-line fix>'.\nCopy: {copy}")
    print(f"{copy!r} -> {verdict}")
    if verdict.strip().upper().startswith("PASS"): break
    feedback = verdict
