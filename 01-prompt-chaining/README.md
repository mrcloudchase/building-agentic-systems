# 01 · Prompt Chaining

> Decompose a task into a fixed sequence of LLM calls, where **each call
> processes the output of the previous one**.

## What it is

Prompt chaining is the simplest way to compose multiple LLM calls. You break a
task into an ordered sequence of steps, and the output of each step becomes the
input to the next:

```
input → [LLM call 1] → [LLM call 2] → [LLM call 3] → output
```

The defining property — the thing that makes it *chaining* — is that **handoff**:
step 2 works on what step 1 produced, step 3 works on what step 2 produced. Each
link transforms the material into something new.

Because *you* fix the order of steps in code, this is a **workflow**, not an
agent. There's no runtime decision about what to do next — the path is
predetermined.

## Why chain instead of using one big prompt?

You *could* ask for everything in a single prompt. Chaining trades a little
latency for accuracy: **each call is an easier task than the whole.** A model
asked to "write on-brand copy, translate it, and fit it to a tweet" all at once
does each part a bit worse than a model given one clean, focused step at a time.

## What the example does

[`prompt_chaining.py`](./prompt_chaining.py) turns a one-line product brief into
a translated social post through three transformative links:

| Step | Input | Output |
|------|-------|--------|
| 1 · write copy | the product brief | an English marketing blurb |
| 2 · translate | the English blurb | a Spanish blurb |
| 3 · shorten | the Spanish blurb | a short social post with hashtags |

Notice that each step's output is the *entire* input to the next — that's the
chain. (This is the article's own example — "generate marketing copy, then
translate it" — with one more link added so the handoff is unmistakable.)

## When to use it

Reach for prompt chaining when:

- the task **cleanly decomposes** into fixed, ordered subtasks, and
- each subtask is a distinct transformation of the previous result.

**Examples from the article:** generating marketing copy and then translating it
into another language; writing a document outline and then writing the full
document from that outline.

## When *not* to use it

If you can't draw the boxes and arrows before you run it — if the steps depend on
what earlier steps discover — chaining is the wrong tool. That points to
[orchestrator-workers](../04-orchestrator-workers/) (dynamic decomposition) or a
full [agent](../06-autonomous-agent/).

## Optional: add a gate

The article notes you can insert a programmatic **gate** between steps — a check
that decides whether the chain should continue — so a bad intermediate result
doesn't flow downstream:

```
input → [step 1] → (gate: passes check?) → [step 2] → output
                        │
                        └─ no → stop / retry / route elsewhere
```

The gate is plain code (or another LLM call). It's a useful embellishment, not
the core idea — the pattern *is* the chain. Dropping a gate into the example
would look like:

```python
blurb = write_copy(brief)
if len(blurb.split()) > 80:          # the gate
    raise ValueError("draft too long — stopping before we spend more calls")
spanish = translate(blurb)
```

➡️ **Next:** [02 · Routing](../02-routing/) — pick a specialized path based on the
input instead of running a fixed sequence.
