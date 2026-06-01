# 04 · Orchestrator-Workers

> A central LLM dynamically breaks work into subtasks, delegates them, and
> synthesizes the results.

## What it is

An **orchestrator** LLM looks at a task, decides *on the fly* how to break it
into subtasks, hands each subtask to a **worker** LLM, and then combines the
workers' outputs into a final result:

```
                  ┌─→ [worker] ─┐
task → [orchestrator] ─→ [worker] ─┼─→ [orchestrator synthesizes] → output
                  └─→ [worker] ─┘
```

## How it differs from parallelization

This looks a lot like [sectioning](../03-parallelization/) — split work, run
workers, combine. The crucial difference is **who decides the subtasks**:

- **Parallelization:** *you* hard-code the subtasks in advance. The structure is
  fixed.
- **Orchestrator-workers:** the *orchestrator* determines the subtasks at
  runtime, based on the specific input. The structure is dynamic.

That dynamism is exactly why this pattern exists — and it's the line where
workflows start to blur into agents. You use it precisely when you **can't
predict** how many pieces a task will have or what they'll be until you see it.

## What the example does

[`orchestrator_workers.py`](./orchestrator_workers.py) writes a short research
brief on a topic in three phases:

1. **Orchestrate** — Claude looks at the topic and decides which subtopics are
   worth covering, returning them as a structured list. *We don't know in
   advance how many there will be or what they are* — that's the point.
2. **Workers** — one worker call researches each subtopic (run in parallel).
3. **Synthesize** — Claude stitches the worker outputs into one coherent brief.

Run it on different topics and notice that the orchestrator picks *different*
subtopics each time. The workflow adapts its own shape to the input.

## When to use it

Reach for orchestrator-workers when:

- the task needs to be decomposed, but you **can't predict the subtasks** ahead
  of time — they depend on the specific input.

**Examples from the article:** coding tasks that touch an unpredictable number of
files (the orchestrator decides which files need changes); search/research tasks
that gather and combine information from multiple sources chosen on the fly.

## A note on trust

Because the orchestrator decides the plan, you're handing it more autonomy than
in the earlier workflows. That's powerful but means errors compound — a bad
decomposition produces bad workers. Keep the orchestrator's job well-scoped and
its output structured so you can inspect the plan before acting on it.

➡️ **Next:** [05 · Evaluator-Optimizer](../05-evaluator-optimizer/) — improve a
single output through a feedback loop.
