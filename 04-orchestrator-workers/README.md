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

The three jobs are always the same, whatever the task:

1. **Decompose** — the orchestrator splits the task into subtasks. *This is the
   plan*, and it's produced at runtime from the input.
2. **Delegate** — each subtask is handed to a worker that does it.
3. **Synthesize** — the orchestrator merges the workers' results into one output.

It's still a **workflow**, but the most dynamic one — which is why it sits right
at the edge of being an agent.

## How it differs from parallelization

Both split work and combine results. The difference is **who decides the
subtasks**:

| | Parallelization (03) | Orchestrator-Workers (04) |
|--|----------------------|---------------------------|
| Subtasks | **fixed by you** in code | **chosen by the model** at runtime |
| Shape | same every run | adapts to the input |

That's the whole point: you use this pattern precisely when you **can't predict**
the subtasks in advance.

## When to use it

Reach for orchestrator-workers when the task needs decomposition but you
**can't predict the subtasks** ahead of time — they depend on the specific input.

**Examples from the article:** coding tasks that change an unpredictable number
of files (the orchestrator decides which files need edits); search tasks that
gather and combine information from multiple sources chosen on the fly.

## A note on trust

Because the orchestrator decides the plan, you hand it more autonomy than the
earlier workflows — so errors compound (a bad decomposition yields bad workers).
Keeping its output **structured** (a JSON list) lets you inspect the plan before
acting on it.

It's also worth being clear about the boundary: this is a single pass —
decompose, delegate, synthesize — with no acting on the world and no feedback
loop. A full agent like Claude Code wraps this kind of plan-and-delegate move
inside an *agent loop* (see [06](../06-autonomous-agent/)) that runs tools,
observes real results, and adapts. Orchestrator-workers is a building block such
an agent reaches for — not the whole agent.

---

## The example: a reusable pipeline for any prompt

Because the decomposition is model-driven, the code isn't tied to one task.
[`orchestrator_workers.py`](./orchestrator_workers.py) is a reusable `run(task)`
made of three small, generic functions — one per job above:

1. **`orchestrate(task)`** — returns a JSON list of subtasks chosen for this
   prompt.
2. **`work(task, subtask)`** — one worker completes each subtask, run in
   parallel.
3. **`synthesize(...)`** — combines the workers' outputs into one cohesive
   result.

Pass any prompt and the workflow reshapes itself to it:

```bash
python 04-orchestrator-workers/orchestrator_workers.py "Plan a 3-day trip to Tokyo"
python 04-orchestrator-workers/orchestrator_workers.py "Outline a course on databases"
# no argument → default: "Write a practical guide to starting a podcast."
```

### A concrete run

To make the three jobs tangible, here's what they look like for the prompt
*"Add rate limiting to a REST API"*:

- **Decompose** (`orchestrate`) → subtasks like `["pick an algorithm (token
  bucket)", "add a Redis store", "write the middleware", "return 429s with retry
  headers", "add tests"]`. (Remember: this list *is* the plan — decomposition,
  not synthesis.)
- **Delegate** (`work`) → each subtask is fleshed out by its own worker, in
  parallel.
- **Synthesize** → the workers' outputs are merged into one ordered
  implementation plan.

Swap the prompt for *"Plan a 3-day trip to Tokyo"* and the plan becomes
`["day-by-day itinerary", "budget", "getting around", "where to eat"]` — same
machinery, decomposition driven entirely by the input.

➡️ **Next:** [05 · Evaluator-Optimizer](../05-evaluator-optimizer/) — improve a
single output through a feedback loop.
