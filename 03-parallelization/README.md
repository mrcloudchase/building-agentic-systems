# 03 · Parallelization

> Run multiple LLM calls at the same time, then aggregate the results.

## What it is

Sometimes the work doesn't need to happen in sequence — it can happen *at once*.
Parallelization runs several LLM calls concurrently and combines their outputs.
The article describes two distinct flavors:

### Sectioning

Break a task into **independent subtasks** that don't depend on each other, run
them in parallel, and stitch the pieces together.

```
          ┌─→ [subtask A] ─┐
input ────┼─→ [subtask B] ─┼─→ aggregate → output
          └─→ [subtask C] ─┘
```

### Voting

Run the **same task multiple times** to get diverse attempts, then combine them
— take a majority vote, require N-of-M agreement, or merge perspectives.

```
          ┌─→ [attempt 1] ─┐
input ────┼─→ [attempt 2] ─┼─→ vote / merge → output
          └─→ [attempt 3] ─┘
```

Both are **workflows**: the structure is fixed in advance.

## Why parallelize?

Two different reasons, matching the two flavors:

- **Sectioning → speed and focus.** Independent pieces finish in the time of the
  slowest one instead of the sum of all of them. And each call gets a narrow,
  focused task, which tends to improve quality.
- **Voting → confidence.** Multiple independent attempts at the same judgment
  give you a confidence signal. One pass might miss something; three passes that
  agree are more trustworthy. You can also tune sensitivity (e.g. flag if *any*
  attempt finds a problem).

## What the example does

[`parallelization.py`](./parallelization.py) demonstrates both flavors using a
thread pool to fan out concurrent API calls:

1. **Sectioning** — score a product idea on three independent dimensions
   (market size, technical feasibility, competition) in parallel, then assemble
   a combined report.
2. **Voting** — ask three independent reviewers whether a snippet of text is
   safe to publish, then apply a rule: if *any* reviewer flags it, it's flagged.

## When to use it

Reach for parallelization when:

- **(sectioning)** subtasks are independent and can run concurrently for speed,
  or you want each handled by a focused call; or
- **(voting)** multiple attempts at the same task give you better coverage or a
  confidence signal.

**Examples from the article:** *sectioning* — one model processes a user query
while another simultaneously screens it for inappropriate content; *voting* —
several prompts review the same code for vulnerabilities and flag it if any of
them find an issue.

➡️ **Next:** [04 · Orchestrator-Workers](../04-orchestrator-workers/) — when you
*can't* predict the subtasks in advance.
