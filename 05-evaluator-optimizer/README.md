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

[`evaluator_optimizer.py`](./evaluator_optimizer.py) writes marketing copy for a
financial offer that must satisfy a compliance + quality rubric (under 30 words,
includes the required APY disclaimer, makes no prohibited claims, ends with a
clear CTA):

- The **optimizer** (copywriter) writes the blurb, and on later rounds revises it
  using the feedback.
- The **evaluator** (compliance reviewer) returns a structured verdict — `PASS`,
  or `FAIL` plus one line of specific feedback.
- The loop runs until `PASS` or `MAX_ROUNDS`.

You'll see the copy converge on the rubric as the reviewer's notes get folded in
(the missing disclaimer is the usual first failure). It runs on any offer:

```bash
python 05-evaluator-optimizer/evaluator_optimizer.py "a no-fee checking account"
# no argument → default: a 4.5% APY savings account
```

➡️ **Next:** [06 · Autonomous Agent](../06-autonomous-agent/) — hand the control
flow to the model itself.
