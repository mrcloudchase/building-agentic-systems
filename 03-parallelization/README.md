# 03 · Parallelization

> Run multiple LLM calls at the same time, then aggregate the results.

## What it is

Sometimes the work doesn't need to happen in sequence — it can happen at once.
Parallelization runs several calls concurrently and combines their outputs. The
article describes two shapes:

```
        ┌─→ [call] ─┐
input ──┼─→ [call] ─┼─→ aggregate → output
        └─→ [call] ─┘
```

- **Sectioning** — break a task into **independent subtasks**, run them in
  parallel, stitch the pieces together.
- **Voting** — run the **same task several times**, then combine the answers
  (majority, unanimity, or merge).

Both are **workflows**: the structure is fixed in advance.

## What the example does

[`parallelization.py`](./parallelization.py) reviews one small code snippet,
using a thread pool to fire the calls concurrently:

- **Sectioning** — three reviewers look at the same code for *different*
  concerns (security, performance, readability) at the same time, then the
  reviews are combined. The snippet has one flaw of each kind, so each reviewer
  finds something different.
- **Voting** — asks "does this code contain a vulnerability?" three times and
  flags the code if *any* of the three says yes.

The whole mechanic is `ThreadPoolExecutor` + `pool.map(ask, ...)` — fan the calls
out, collect the results.

## Why parallelize?

Two reasons, matching the two shapes:

- **Sectioning → speed and focus.** Independent pieces finish in the time of the
  slowest one instead of the sum of all of them, and each call gets a narrow,
  focused task.
- **Voting → confidence.** Multiple independent attempts at the same judgment
  give you a confidence signal, and you can tune the decision rule (here: flag
  if *any* attempt objects).

## When to use it

Reach for parallelization when:

- **(sectioning)** subtasks are independent and can run concurrently, or
- **(voting)** multiple attempts at the same task improve coverage or confidence.

**Examples from the article:** *sectioning* — one model answers a query while
another simultaneously screens it for inappropriate content; *voting* — several
prompts review the same code for vulnerabilities and flag it if any find a
problem.

## How it differs from the earlier patterns

- **Routing** picks *one* path. **Parallelization** runs *many* paths at once.
- The subtasks here are **fixed by you** in advance. When the subtasks must be
  decided at runtime, you want
  [orchestrator-workers](../04-orchestrator-workers/) instead.

➡️ **Next:** [04 · Orchestrator-Workers](../04-orchestrator-workers/) — when you
can't predict the subtasks ahead of time.
