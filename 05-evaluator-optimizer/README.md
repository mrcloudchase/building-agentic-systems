# 05 · Evaluator-Optimizer

> One LLM generates, another critiques, and they loop until it's good enough.

## What it is

Two LLM roles work in a feedback loop:

- the **optimizer** (generator) produces a candidate response, and
- the **evaluator** judges it against criteria and returns specific feedback.

The optimizer revises using that feedback, the evaluator judges again, and the
loop repeats until the evaluator is satisfied (or you hit a retry limit):

```
            ┌──────────────────────────────────┐
            ▼                                   │
task → [optimizer] → draft → [evaluator] → PASS? ─ no, here's feedback
                                   │
                                   yes → output
```

It's a **workflow**: the two-role loop is fixed, even though the number of
iterations varies.

## Why split generation from evaluation?

The same reason a writer benefits from an editor: it's easier to *critique* a
concrete draft than to produce a perfect one in one shot. Separating the roles
lets the evaluator hold a clear standard and point at specific gaps, while the
optimizer focuses on addressing them. The article notes this works best when

- you have **clear evaluation criteria**, and
- **iterative refinement measurably helps** — especially when a human giving the
  same kind of feedback would improve the result.

## What the example does

[`evaluator_optimizer.py`](./evaluator_optimizer.py) writes a product tagline
that must satisfy explicit constraints (short, mentions a benefit, no clichés).

- The **optimizer** writes a tagline (and revises it on later rounds using the
  feedback).
- The **evaluator** returns a structured verdict — `PASS` or `FAIL` plus
  concrete feedback.
- The loop runs until `PASS` or a maximum number of rounds.

You'll see the tagline visibly improve as the evaluator's notes get folded in.

## When to use it

Reach for evaluator-optimizer when:

- you can articulate **clear criteria** for a good answer, and
- **iteration improves quality** — the first draft is rarely the best, and
  targeted feedback closes the gap.

**Examples from the article:** literary translation, where an evaluator can catch
nuances the first pass missed; multi-round research tasks that need several
cycles of searching and refining before the answer is complete.

## Don't loop forever

Always cap the iterations. Without a stopping condition you can burn unbounded
tokens — or get stuck oscillating. A max-rounds limit (plus the evaluator's
`PASS`) gives the loop a guaranteed terminal state.

➡️ **Next:** [06 · Autonomous Agent](../06-autonomous-agent/) — hand the control
flow to the model itself.
