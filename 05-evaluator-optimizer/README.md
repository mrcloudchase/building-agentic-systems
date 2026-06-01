# 05 · Evaluator-Optimizer

> One LLM generates, another critiques, and they loop until it's good enough.

## What it is

Two roles work in a feedback loop. The **optimizer** produces a candidate; the
**evaluator** judges it against criteria and returns specific feedback; the
optimizer revises; repeat until the evaluator is satisfied (or you hit a retry
limit):

```
            ┌──────────────────────────────────┐
            ▼                                   │
task → [optimizer] → draft → [evaluator] → PASS? ─ no, here's feedback
                                   │
                                   yes → output
```

It's a **workflow**: the two-role loop is fixed, even though the number of
iterations varies. Splitting generation from evaluation works because it's easier
to *critique* a concrete draft than to produce a perfect one in one shot — same
reason a writer benefits from an editor.

## When to use it

Reach for evaluator-optimizer when you can articulate **clear evaluation
criteria** and **iteration measurably improves quality** — especially when a
human giving the same kind of feedback would help. Always cap the iterations
(a max-rounds limit plus the evaluator's PASS) so the loop has a guaranteed
terminal state and can't burn unbounded tokens.

If a single pass is good enough, don't add the loop — it costs extra calls.

**Examples from the article:** literary translation, where an evaluator can catch
nuances the first pass missed; multi-round research that needs several cycles of
searching and refining before the answer is complete.

## Example

[`evaluator_optimizer.py`](./evaluator_optimizer.py) writes compliant marketing
copy: generate, check against a rubric, revise — looping until it passes (or 4
rounds):

```python
copy = feedback = ""
for _ in range(4):
    copy = ask(f"Write marketing copy for: {offer}.\nIt must satisfy: {criteria}.\nPrevious attempt: {copy}\nReviewer feedback: {feedback}\nReturn only the copy.")
    verdict = ask(f"Judge this copy against [{criteria}]. Reply 'PASS' or 'FAIL: <one-line fix>'.\nCopy: {copy}")
    if verdict.strip().upper().startswith("PASS"): break
    feedback = verdict
```

The `criteria` includes a required disclaimer and banned claims, so the missing
disclaimer is usually the first failure the reviewer catches. Run it:

```bash
python 05-evaluator-optimizer/evaluator_optimizer.py
```

➡️ **Next:** [06 · Autonomous Agent](../06-autonomous-agent/) — hand the control
flow to the model itself.
