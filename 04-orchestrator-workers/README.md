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

Three jobs, always the same whatever the task: **decompose** (split into
subtasks — *this is the plan*, produced at runtime), **delegate** (hand each
subtask to a worker), **synthesize** (merge the results into one output). It's
still a **workflow**, but the most dynamic one: the subtasks aren't hard-coded —
the model chooses them at runtime, so the shape adapts to each input.

## When to use it

Reach for orchestrator-workers when the task needs decomposition but you
**can't predict the subtasks** ahead of time — they depend on the specific input.
If you *can* draw the boxes before running, a fixed workflow (chaining or
parallelization) is simpler.

Because the orchestrator decides the plan, you hand it more autonomy, so errors
compound — keeping its output **structured** (a JSON list) lets you inspect the
plan before acting on it. Note the boundary, too: this is a single structured
pass with no feedback loop — it decomposes, delegates, and synthesizes once,
without acting on the world or adapting to results.

**Examples from the article:** coding tasks that change an unpredictable number
of files (the orchestrator decides which files need edits); search tasks that
gather and combine information from multiple sources chosen on the fly.

## Example

Because the decomposition is model-driven, the code isn't tied to one task.
[`orchestrator_workers.py`](./orchestrator_workers.py) is a reusable `run(task)`
made of three small functions — one per job above: `orchestrate(task)` returns a
JSON list of subtasks chosen for this prompt, `work(task, subtask)` completes
each subtask in parallel, and `synthesize(...)` combines the outputs into one
cohesive result.

Pass any prompt and the workflow reshapes itself to it:

```bash
python 04-orchestrator-workers/orchestrator_workers.py "Plan a 3-day trip to Tokyo"
python 04-orchestrator-workers/orchestrator_workers.py "Outline a course on databases"
# no argument → default: "Write a practical guide to starting a podcast."
```

For the prompt *"Add rate limiting to a REST API,"* the three jobs play out as:

- **Decompose** → `["pick an algorithm (token bucket)", "add a Redis store",
  "write the middleware", "return 429s with retry headers", "add tests"]` — this
  list *is* the plan.
- **Delegate** → each subtask is fleshed out by its own worker, in parallel.
- **Synthesize** → the outputs are merged into one ordered implementation plan.

Swap the prompt for *"Plan a 3-day trip to Tokyo"* and the plan becomes
`["day-by-day itinerary", "budget", "getting around", "where to eat"]` — same
machinery, decomposition driven entirely by the input.
