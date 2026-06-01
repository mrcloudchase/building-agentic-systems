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

[`orchestrator_workers.py`](./orchestrator_workers.py) produces a market-research
brief. The model picks the research angles at runtime (**decompose**), a worker
researches each in parallel (**delegate**), then one call combines them
(**synthesize**):

```python
plan = ask(f"Break this into 3-5 research angles. Reply with ONLY a JSON array of strings.\n\n{request}")
angles = json.loads(plan[plan.index("["):plan.rindex("]") + 1])
def work(angle): return f"## {angle}\n" + ask(f"Research this angle of the request '{request}': {angle}")
with ThreadPoolExecutor() as pool:
    sections = list(pool.map(work, angles))
print(ask(f"Combine these into one market brief for '{request}':\n\n" + "\n\n".join(sections)))
```

The angles aren't hard-coded — a different request yields a different plan. Run
it:

```bash
python 04-orchestrator-workers/orchestrator_workers.py
```

➡️ **Next:** [05 · Evaluator-Optimizer](../05-evaluator-optimizer/) — improve a
single output through a feedback loop.
