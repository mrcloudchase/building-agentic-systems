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

[`orchestrator_workers.py`](./orchestrator_workers.py) is a reusable `run(task)`
that works for **any prompt**. It's three small, generic functions:

1. **`orchestrate(task)`** — the model splits the task into a JSON list of
   subtasks. *We don't know how many or which ones until it answers* — they're
   chosen at runtime from the prompt.
2. **`work(task, subtask)`** — one worker completes each subtask, run in
   parallel.
3. **`synthesize(...)`** — the orchestrator combines the workers' outputs into
   one cohesive result.

None of it is hard-coded to a particular task, which is the point — pass any
prompt and the workflow reshapes itself to it:

```bash
python 04-orchestrator-workers/orchestrator_workers.py "Plan a 3-day trip to Tokyo"
python 04-orchestrator-workers/orchestrator_workers.py "Outline a course on databases"
```

The default prompt (no argument) writes a guide to starting a podcast. A
software feature request would instead produce an implementation plan; a
research question would produce a researched answer. Same machinery, any input.

### A concrete run

To make the three phases tangible, here's what they look like for the prompt
*"Add rate limiting to a REST API"* — note that the **plan is the decomposition
step**, not the synthesis step:

- **Plan** (`orchestrate`) → the model returns subtasks like
  `["pick an algorithm (token bucket)", "add a Redis store", "write the
  middleware", "return 429s with retry headers", "add tests"]`. These are chosen
  for *this* prompt; a different prompt yields a different list.
- **Delegate** (`work`) → each subtask is fleshed out by its own worker, in
  parallel.
- **Synthesize** → the workers' outputs are merged into one ordered
  implementation plan.

Swap the prompt for "Plan a 3-day trip to Tokyo" and the plan becomes
`["day-by-day itinerary", "budget", "getting around", "where to eat"]` — same
machinery, decomposition driven entirely by the input.

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
