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

It's a **workflow**: the structure is fixed in advance. The article describes two
shapes:

- **Sectioning** — break a task into independent subtasks, run them in parallel,
  stitch the pieces together. Independent pieces finish in the time of the
  slowest one, and each call gets a narrow, focused job.
- **Voting** — run the same task several times and combine the answers (majority,
  unanimity, or "flag if any"). Multiple independent attempts give a confidence
  signal and a tunable decision rule.

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

[`parallelization.py`](./parallelization.py) reviews a contract two ways at once,
fanning the calls out with a thread pool:

```python
aspects = ["payment & renewal", "liability & risk", "missing standard clauses"]
with ThreadPoolExecutor() as pool:
    reviews = list(pool.map(ask, [f"Review this contract for {a}:\n{contract}" for a in aspects]))  # SECTIONING
    votes = list(pool.map(lambda _: ask(f"...high-risk clause needing legal review? YES or NO:\n{contract}"), range(3)))  # VOTING
```

- **Sectioning** reviews each concern in parallel, so each reviewer finds
  something different.
- **Voting** runs the same high-risk check three times and escalates to legal if
  *any* says YES.

Run it:

```bash
python 03-parallelization/parallelization.py
```

➡️ **Next:** [04 · Orchestrator-Workers](../04-orchestrator-workers/) — when you
can't predict the subtasks ahead of time.
