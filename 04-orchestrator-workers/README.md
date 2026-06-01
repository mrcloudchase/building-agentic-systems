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
still a **workflow**, but the most dynamic one. The difference from
parallelization is **who decides the subtasks**:

| | Parallelization (03) | Orchestrator-Workers (04) |
|--|----------------------|---------------------------|
| Subtasks | **fixed by you** in code | **chosen by the model** at runtime |
| Shape | same every run | adapts to the input |

## When to use it

Reach for orchestrator-workers when the task needs decomposition but you
**can't predict the subtasks** ahead of time — they depend on the specific input.
If you *can* draw the boxes before running, a fixed workflow (chaining or
parallelization) is simpler.

Because the orchestrator decides the plan, you hand it more autonomy, so errors
compound — keeping its output **structured** (a JSON list) lets you inspect the
plan before acting on it. Note the boundary, too: this is a single pass with no
feedback loop. A full agent like Claude Code wraps this kind of plan-and-delegate
move inside an *agent loop* ([06](../06-autonomous-agent/)) that runs tools and
adapts — orchestrator-workers is a building block such an agent reaches for, not
the whole agent.

**Examples from the article:** coding tasks that change an unpredictable number
of files (the orchestrator decides which files need edits); search tasks that
gather and combine information from multiple sources chosen on the fly.

## Example

[`orchestrator_workers.py`](./orchestrator_workers.py) produces a market /
due-diligence research brief. Because the decomposition is model-driven, the code
isn't tied to one request — it's a reusable `run(request)` made of three small
functions, one per job above: `orchestrate(request)` returns a JSON list of
research angles chosen for this request, `work(request, angle)` researches each
angle in parallel, and `synthesize(...)` combines them into one brief.

Pass any request and the workflow reshapes itself to it:

```bash
python 04-orchestrator-workers/orchestrator_workers.py "Diligence on a B2B payroll startup"
# no argument → default: market opportunity for an AI meal-planning app
```

For the default request, the three jobs play out as:

- **Decompose** → research angles like `["market size & growth", "target
  customers", "competitive landscape", "key risks"]` — this list *is* the plan,
  chosen at runtime.
- **Delegate** → each angle is researched by its own worker, in parallel.
- **Synthesize** → the sections are merged into one brief with an executive
  summary.

Swap the request for a diligence prompt and the angles change to fit it — same
machinery, decomposition driven entirely by the input.

➡️ **Next:** [05 · Evaluator-Optimizer](../05-evaluator-optimizer/) — improve a
single output through a feedback loop.
