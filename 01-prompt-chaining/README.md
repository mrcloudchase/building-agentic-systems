# 01 · Prompt Chaining

> Decompose a task into a fixed sequence of LLM calls, where **each call
> processes the output of the previous one**.

## What it is

The simplest way to compose multiple LLM calls: call the model, then call it
again with the previous answer fed into the next prompt.

```
input → [LLM call 1] → [LLM call 2] → output
```

The defining property is that **handoff** — call 2 works on whatever call 1
produced. Because *you* fix the order of steps in code, this is a **workflow**,
not an agent: nothing is decided at runtime.

## What the example does

[`prompt_chaining.py`](./prompt_chaining.py) writes a how-to technical document
in two chained calls:

| Step | Input | Output |
|------|-------|--------|
| 1 · outline | the topic ("how to build & train a GPT-3-style LLM") | a numbered outline of the steps |
| 2 · write | the outline from step 1 | the full how-to doc |

That's the entire pattern: the `outline` variable is pasted into step 2's
prompt. This is the article's own example — "write an outline of a document,
then write the document based on the outline."

## Why chain instead of one big prompt?

You *could* ask for the whole doc in one call. Chaining trades a little latency
for accuracy: **each call is an easier task than the whole.** Outlining first
gives the model a clear structure to follow, so the final doc is better
organized than if you'd asked for everything at once.

## When to use it

Reach for prompt chaining when the task **cleanly decomposes** into fixed,
ordered steps, and each step is a distinct transformation of the previous
result.

**Examples from the article:** writing an outline and then the full document
from it (what we do here); generating marketing copy and then translating it.

## When *not* to use it

If you can't lay out the steps before running — if later steps depend on what
earlier ones discover — chaining is the wrong tool. That points to
[orchestrator-workers](../04-orchestrator-workers/) or a full
[agent](../06-autonomous-agent/).

## Optional: add a gate

The article notes you can insert a programmatic **gate** between steps — a check
that decides whether the chain should continue — so a bad intermediate result
doesn't flow downstream:

```python
outline = ask(f"List the steps as a numbered outline for: {topic}")
if "1." not in outline:                 # the gate: did we actually get steps?
    raise ValueError("step 1 didn't produce an outline — stopping")
doc = ask(f"Write the doc from this outline:\n{outline}")
```

The gate is a useful embellishment, not the core idea — the pattern *is* the
chain.

➡️ **Next:** [02 · Routing](../02-routing/) — pick a specialized path based on the
input instead of running a fixed sequence.
