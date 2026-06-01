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

[`prompt_chaining.py`](./prompt_chaining.py) generates how-to technical
documentation by feeding each step's output into the next prompt. The whole
thing (with `ask()` a one-line wrapper over `client.messages.create`):

```python
steps = ["Write a numbered outline of the steps for: {}",
         "Write a how-to technical doc (Markdown) from this outline:\n{}",
         "Copy edit this document, keeping its structure and commands:\n{}"]
text = "how to build and train a GPT-3-style LLM from scratch"
for step in steps:
    text = ask(step.format(text)); print(text, "\n")
```

The chain *is* the `steps` list; the loop never changes. Run it:

```bash
python 01-prompt-chaining/prompt_chaining.py
```

➡️ **Next:** [02 · Routing](../02-routing/) — pick a specialized path based on the
input instead of running a fixed sequence.
