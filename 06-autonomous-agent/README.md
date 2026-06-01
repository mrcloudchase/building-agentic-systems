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

[`autonomous_agent.py`](./autonomous_agent.py) is a coding agent in **under 15
lines of code** — one loop, one `bash` tool, the model drives (in the spirit of
[Quark](https://github.com/averagejoeslab/quark)). It's an interactive REPL: you
type a request, the agent runs bash commands to carry it out and feeds the output
back to itself until it's done. The conversation history is its memory. That's
the whole pattern — no task-specific scaffolding:

```python
import subprocess, anthropic
client = anthropic.Anthropic()
TOOLS = [{"name": "bash", "description": "Run a bash command.", "input_schema": {...}}]
def sh(cmd): return subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
messages = []
while True:
    messages.append({"role": "user", "content": input("\nyou> ")})
    while True:
        r = client.messages.create(model="claude-opus-4-8", max_tokens=4096, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        print("".join(b.text for b in r.content if b.type == "text"))
        if r.stop_reason != "tool_use": break
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": b.id, "content": sh(b.input["command"])} for b in r.content if b.type == "tool_use"]})
```

```bash
python 06-autonomous-agent/autonomous_agent.py
# then type, e.g.:  create a fizzbuzz.py, run it, and show me the output
```

> ⚠️ The bash tool runs real shell commands on your machine — it is **not**
> sandboxed. Run it in a throwaway / trusted directory.

➡️ **Back to:** [the overview](../README.md) — and remember the through-line:
start simple, and only graduate to this much autonomy when the task genuinely
demands it.
