# 06 · Autonomous Agent

> Hand the control flow to the model: a tool-using loop that runs until the task
> is done.

## What it is

This is what people usually mean by "agent." You give the model a goal and a set
of tools, and it runs a loop — planning, acting with a tool, observing the real
result, and deciding its next move — until it judges the task complete:

```
goal → ┌─────────────────────────────────────────┐
       │  model plans → calls a tool → observes   │
       │       ▲                          │        │
       │       └──────── repeat ──────────┘        │
       └─────────────────────────────────────────┘
                          │
                  task complete → output
```

The defining difference from the workflows (01–05): **the model decides what
happens next**, not your code. The control flow is dynamic and the number of
steps is open-ended. The model gets ground truth from the environment (real tool
results) at each step, which lets it course-correct as it goes.

## When to use it

Reach for an agent when the task is **open-ended**, the number of steps **can't
be predicted** or hard-coded, you can **trust the model's decision-making** in
the loop, and there's a feedback signal (tool results) to self-correct on. If a
fixed workflow can do the job, prefer it — agents trade latency, cost, and a
larger error surface for flexibility.

Autonomy amplifies both capability and the cost of mistakes, so build with
guardrails: keep it simple, make the agent's planning and actions transparent,
invest in good tool design and documentation (the agent-computer interface), and
**test in a sandbox with a bounded loop**.

**Examples from the article:** coding agents that solve real software tasks
editing many files (e.g. SWE-bench); "computer use" agents that operate a
desktop.

## Example

[`autonomous_agent.py`](./autonomous_agent.py) is a minimal coding agent in the
spirit of [Quark](https://github.com/averagejoeslab/quark): one loop, one
**bash** tool. At startup it seeds a gitignored `sandbox/` with a stub function
(`string_utils.py`) and a failing test (`test_string_utils.py`), then gives the
agent a single `bash` tool and one goal: make the tests pass.

With just bash, the agent does everything itself — `cat` the test, write the
implementation, run `python test_string_utils.py`, read the output, fix, and
re-run — using the real test result as **ground truth** at each step. It loops
until the tests pass (it stops on its own) or hits `MAX_ITERATIONS`. Every
command is printed so you can follow its reasoning.

```bash
python 06-autonomous-agent/autonomous_agent.py
```

> ⚠️ The bash tool runs real shell commands on your machine (with the sandbox as
> the working directory, but it is **not** a hardened sandbox). Run it in a
> throwaway / trusted environment.

➡️ **Back to:** [the overview](../README.md) — and remember the through-line:
start simple, and only graduate to this much autonomy when the task genuinely
demands it.
