# 01 · Prompt Chaining

> Decompose a task into a fixed sequence of LLM calls, where each call processes
> the output of the previous one.

## What it is

The simplest way to compose multiple LLM calls. You break a task into an ordered
sequence of steps, and the output of each step becomes the input to the next:

```
input → [LLM call 1] → [LLM call 2] → [LLM call 3] → output
```

The defining property is that **handoff** — each call transforms whatever the
previous call produced into something new, turning one hard all-at-once task into
a series of easier ones. Because *you* fix the order of steps in code, this is a
**workflow**, not an agent: nothing is decided at runtime. (You can optionally
put a **gate** between steps — a programmatic check that stops the chain if an
intermediate result is bad.)

## When to use it

Reach for prompt chaining when the task **cleanly decomposes** into fixed,
ordered steps, and each step is a distinct transformation of the previous
result. It trades a little latency for accuracy, since each call is an easier
task than the whole.

Don't use it when the steps depend on what earlier steps *discover* — if you
can't lay out the sequence before running, you want
[orchestrator-workers](../04-orchestrator-workers/) or a full
[agent](../06-autonomous-agent/) instead.

**Examples from the article:** writing an outline of a document and then writing
the document from that outline; generating marketing copy and then translating
it into another language.

## Example

[`prompt_chaining.py`](./prompt_chaining.py) writes a how-to technical document
in three chained calls:

| Step | Input | Output |
|------|-------|--------|
| 1 · outline | the topic ("how to build & train a GPT-3-style LLM") | a numbered outline, in a fixed Markdown format |
| 2 · write | the outline from step 1 | the full how-to doc, in a fixed Markdown format |
| 3 · copy edit | the doc from step 2 | a polished final doc, structure unchanged |

Each step's output is pasted into the next step's prompt — that's the chain.
Steps 1 and 2 also show the model an exact Markdown template (`OUTLINE_FORMAT` /
`DOC_FORMAT`) and say "use exactly this format," so the output is consistent run
to run and the next step always gets the shape it expects.

The chain is wrapped in a reusable `run(topic)`, so it works for any how-to
topic — pass one on the command line:

```bash
python 01-prompt-chaining/prompt_chaining.py "how to deploy a Django app to AWS"
# no argument → default: "how to build and train a GPT-3-style LLM"
```

To add a gate, you'd drop a check between two steps:

```python
outline = ask(f"List the steps as a numbered outline for: {topic}")
if "1." not in outline:                 # the gate: did we actually get steps?
    raise ValueError("step 1 didn't produce an outline — stopping")
doc = ask(f"Write the doc from this outline:\n{outline}")
```

➡️ **Next:** [02 · Routing](../02-routing/) — pick a specialized path based on the
input instead of running a fixed sequence.
