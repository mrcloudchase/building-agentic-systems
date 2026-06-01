# 06 · Autonomous Agent

> Hand the control flow to the model: a tool-using loop that runs until the task
> is done.

## What it is

This is the part everyone means when they say "agent." Unlike the workflows
(01–05), where *your code* decides what happens next, here **the model decides**.
You give it a goal and a set of tools, and it runs in a loop — planning, acting
with tools, observing the results, and deciding its next move — until it judges
the task complete:

```
goal → ┌─────────────────────────────────────────┐
       │  model plans → calls a tool → observes   │
       │       ▲                          │        │
       │       └──────── repeat ──────────┘        │
       └─────────────────────────────────────────┘
                          │
                  task complete → output
```

The model gets "ground truth" from the environment at each step — real tool
results, not its own assumptions — which lets it course-correct as it goes.

## Agent vs. workflow

This is the central distinction of the whole article:

|  | Workflows (01–05) | Agent (06) |
|--|-------------------|------------|
| Who decides the next step? | your code | the model |
| Control flow | predefined | dynamic |
| Number of steps | fixed/bounded by design | open-ended |
| Best for | well-defined tasks | open-ended tasks you can't script |

Mechanically it's just a tool-use loop — the same request/execute/feed-back
cycle any tool-using LLM call uses. What makes it an *agent* is mindset and
scope: the model runs many steps autonomously toward an open-ended goal,
deciding for itself which tools to call and when it's finished.

## What the example does

[`autonomous_agent.py`](./autonomous_agent.py) is a small file-system agent
working in a sandbox directory. It's given file tools — `list_files`,
`read_file`, `write_file` — and a task like *"create a `greeting.txt` and then a
`summary.txt` describing what you did."*

The agent decides the sequence of tool calls entirely on its own. It loops until
it stops requesting tools (`stop_reason == "end_turn"`), with a hard cap on
iterations as a safety stop. Everything happens inside `06-autonomous-agent/sandbox/`,
which is gitignored.

## When to use it

Reach for an agent when:

- the task is **open-ended**, with a number of steps you **can't predict** or
  hard-code, and
- you can **trust the model's decision-making** in the loop, and
- there's a feedback signal (tool results) that lets it self-correct.

**Examples from the article:** coding agents that solve real software tasks
editing many files (à la SWE-bench); "computer use" agents that operate a
desktop.

## Build it responsibly

Autonomy cuts both ways — it amplifies capability *and* the cost of mistakes.
The article's guardrails apply most strongly here:

- **Maintain simplicity** — don't add autonomy you don't need.
- **Prioritize transparency** — show the agent's planning and actions (this
  example prints every tool call) so you can follow what it's doing.
- **Engineer the agent-computer interface (ACI)** — invest in tool design and
  documentation as much as in prompts. A confusing tool surface produces a
  confused agent.
- **Test in a sandbox** and bound the loop. This example does both: a scratch
  directory and a max-iteration cap (the stopping condition).

➡️ **Back to:** [the overview](../README.md) — and remember the through-line:
start simple, and only graduate to this much autonomy when the task genuinely
demands it.
