# 01 · Prompt Chaining

> Decompose a task into a fixed sequence of steps, each feeding the next.

## What it is

Prompt chaining is the simplest way to compose multiple LLM calls. You break a
task into a **fixed, predefined sequence** of subtasks, and each call works on
the output of the previous one:

```
input → [LLM call 1] → [LLM call 2] → [LLM call 3] → output
```

Because *you* hard-code the order of steps, this is a **workflow**, not an agent.
There's no dynamic decision-making about what to do next — the path is fixed.

## Why bother splitting it up?

Couldn't one big prompt do all of this? Sometimes. But chaining trades a little
latency for a lot of accuracy: **each call is easier than the whole task.** A
model asked to "write a polished, on-brand, fact-checked, translated blog post"
in one shot will do every part a little worse than a model asked to do one
clean step at a time.

## Gates

The article highlights a powerful addition: a **gate** — a programmatic check
*between* steps that decides whether to continue. If step 1's output fails a
check, you can stop, retry, or route elsewhere instead of wasting the
downstream calls.

```
input → [generate] → (gate: passes check?) → [refine] → output
                          │
                          └─ no → stop / retry
```

The gate can be plain code (does the output contain the required sections?) or
another LLM call.

## What the example does

[`prompt_chaining.py`](./prompt_chaining.py) turns a one-line topic into a short
marketing blurb in three chained steps:

1. **Generate** a first-draft blurb from the topic.
2. **Gate** (plain Python): check the draft is within a length budget. If it
   fails, the chain stops early instead of polishing a bad draft.
3. **Polish** the approved draft into punchy final copy.

Watch how each step's output becomes the next step's input, and how the gate
short-circuits the chain when the draft is out of bounds.

## When to use it

Reach for prompt chaining when:

- the task **cleanly decomposes** into fixed, ordered subtasks, and
- you'd rather trade a bit of latency for higher accuracy on each step.

**Examples from the article:** generating marketing copy and then translating
it; writing a document outline, checking the outline against criteria, then
writing the full document.

## When *not* to use it

If the subtasks aren't known ahead of time — if you can't draw the boxes and
arrows before you run it — chaining is the wrong tool. That's a sign you want
[orchestrator-workers](../04-orchestrator-workers/) (dynamic decomposition) or a
full [agent](../06-autonomous-agent/).

➡️ **Next:** [02 · Routing](../02-routing/) — pick a specialized path based on the
input.
