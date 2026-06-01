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

[`orchestrator_workers.py`](./orchestrator_workers.py) turns a software feature
request into an implementation plan in three phases:

1. **Orchestrate** — the model breaks the feature into a JSON list of
   implementation subtasks. *This list is the plan* — how many subtasks and
   which ones depend on the feature, so we can't hard-code them.
2. **Workers** — one worker fleshes out each subtask (approach + a short code
   sketch), run in parallel.
3. **Synthesize** — the orchestrator combines the worked-out subtasks into one
   ordered implementation plan.

Run it on a different feature and the orchestrator produces a different plan —
the workflow reshapes itself to the input.

> **This is not a coding agent.** It's a single pass — decompose, delegate,
> synthesize — with no acting on a real codebase and no test feedback. A full
> coding agent like Claude Code wraps this kind of plan-and-delegate move inside
> an *agent loop* (see [06](../06-autonomous-agent/)) that runs tools, observes
> real results, and adapts. Orchestrator-workers is a building block such an
> agent reaches for — not the whole agent.

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
