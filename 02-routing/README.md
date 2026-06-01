# 02 · Routing

> Classify the input, then send it to a handler specialized for that category.

## What it is

Routing has two phases: **classify, then dispatch.** A first step decides *what
kind* of request came in; based on that label, you send it down a path — a
prompt, a model, or a toolset — built for exactly that category.

```
                 ┌─→ [handler A]
input → [router] ─┼─→ [handler B]
                 └─→ [handler C]
```

It's a **workflow**, not an agent: the routes are all predefined. The only thing
decided at runtime is *which* fixed path runs — not what the paths are.

## What the example does

[`routing.py`](./routing.py) is a support-triage demo. It classifies each
message, then answers it with that category's specialized system prompt:

| Message | Route | Handler |
|---------|-------|---------|
| "I was double-charged — can I get a refund?" | `billing` | billing specialist prompt |
| "The app crashes when I upload a photo." | `technical` | support-engineer prompt |
| "What are your support hours?" | `general` | friendly-generalist prompt |

The whole pattern is the two calls in `handle()`: one to pick the label, one to
answer with `ROUTES[label]`.

## Why route instead of one big prompt?

**Separation of concerns.** If one prompt had to handle every category, tuning
it for billing questions would quietly hurt its handling of technical ones.
Routing gives each path its own focused prompt you can improve in isolation — the
billing and technical handlers can't break each other.

## When to use it

Reach for routing when:

- the inputs fall into **distinct categories** that are genuinely better handled
  separately, and
- you can **classify them accurately**.

The classifier doesn't have to be an LLM — the article notes a cheaper
classification model or even plain rules works too. The whole pattern hinges on
getting the label right: misclassify, and the wrong handler gets the work.

**Examples from the article:** directing customer-service queries (general,
refund, technical) into different downstream prompts and tools (what we do
here); routing easy questions to a small cheap model and hard ones to a larger
capable model to save cost and latency.

## How it differs from chaining (pattern 01)

- **Chaining** runs *all* steps in a fixed line — each output feeds the next.
- **Routing** runs *one of several* paths — the classifier picks the branch, and
  only that branch executes.

➡️ **Next:** [03 · Parallelization](../03-parallelization/) — run multiple calls at
once instead of choosing a single path.
