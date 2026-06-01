# 04 · Orchestrator-Workers

> A central LLM dynamically breaks work into subtasks, delegates them, and
> synthesizes the results.

## What it is

An **orchestrator** looks at a task, decides *on the fly* how to split it into
subtasks, hands each one to a **worker**, and combines the workers' outputs:

```
                  ┌─→ [worker] ─┐
task → [orchestrator] ─→ [worker] ─┼─→ [synthesize] → output
                  └─→ [worker] ─┘
```

It's still a **workflow**, but the most dynamic one — which is why it sits right
at the edge of being an agent.

## The one thing that makes it different from parallelization

Both split work and combine results. The difference is **who decides the
subtasks**:

| | Parallelization (03) | Orchestrator-Workers (04) |
|--|----------------------|---------------------------|
| Subtasks | **fixed by you** in code | **chosen by the model** at runtime |
| Shape | same every run | adapts to the input |

That's the whole point: you use this pattern precisely when you **can't predict**
the subtasks in advance.

## What the example does

[`orchestrator_workers.py`](./orchestrator_workers.py) answers a complex question
in three phases:

1. **Orchestrate** — the model splits the question into a JSON list of
   sub-questions. *We don't know how many or what they are until it answers* —
   that's the dynamic decomposition.
2. **Workers** — one worker call answers each sub-question (run in parallel).
3. **Synthesize** — the orchestrator integrates the answers into one coherent
   response to the original question.

Run it on a different question and the orchestrator picks different
sub-questions — the workflow reshapes itself to the input.

## When to use it

Reach for orchestrator-workers when the task needs decomposition but you
**can't predict the subtasks** ahead of time — they depend on the specific input.

**Examples from the article:** coding tasks that change an unpredictable number
of files (the orchestrator decides which files need edits); search tasks that
gather and combine information from multiple sources chosen on the fly.

## A note on trust

Because the orchestrator decides the plan, you hand it more autonomy than the
earlier workflows — so errors compound (a bad decomposition yields bad workers).
Keeping its output **structured** (here, a JSON list) lets you inspect the plan
before acting on it.

➡️ **Next:** [05 · Evaluator-Optimizer](../05-evaluator-optimizer/) — improve a
single output through a feedback loop.
