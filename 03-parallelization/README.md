# 03 · Parallelization

> Run multiple LLM calls at the same time, then aggregate the results.

## What it is

Sometimes the work doesn't need to happen in sequence — it can happen at once.
Parallelization runs several calls concurrently and combines their outputs:

```
        ┌─→ [call] ─┐
input ──┼─→ [call] ─┼─→ aggregate → output
        └─→ [call] ─┘
```

It's a **workflow**: the structure is fixed in advance. The article describes
two shapes — **sectioning** (split into independent subtasks) and **voting** (run
the same task several times).

## What it does

- **Sectioning** — break a task into independent subtasks, run them in parallel,
  and stitch the pieces together. Independent pieces finish in the time of the
  slowest one, and each call gets a narrow, focused job.
- **Voting** — run the same task several times and combine the answers (majority,
  unanimity, or "flag if any"). Multiple independent attempts give you a
  confidence signal and a tunable decision rule.

## When to use it

Reach for parallelization when subtasks are **independent and can run
concurrently** (sectioning), or when **multiple attempts at the same task**
improve coverage or confidence (voting).

The subtasks here are **fixed by you** in advance. When they must be decided at
runtime from the input, you want
[orchestrator-workers](../04-orchestrator-workers/) instead.

**Examples from the article:** *sectioning* — one model answers a query while
another simultaneously screens it for inappropriate content; *voting* — several
prompts review the same code for vulnerabilities and flag it if any find a
problem.

## Example

[`parallelization.py`](./parallelization.py) reviews one small code snippet —
which has a SQL-injection hole, an inefficient loop, and unclear names — using a
thread pool to fire the calls concurrently:

- **Sectioning** — three reviewers look at the same code for *different* concerns
  (security, performance, readability) at the same time, so each finds something
  different.
- **Voting** — asks "does this code contain a vulnerability?" three times and
  flags the code if *any* of the three says yes.

The whole mechanic is `ThreadPoolExecutor` + `pool.map(ask, ...)` — fan the calls
out, collect the results.

```bash
python 03-parallelization/parallelization.py
```

➡️ **Next:** [04 · Orchestrator-Workers](../04-orchestrator-workers/) — when you
can't predict the subtasks ahead of time.
