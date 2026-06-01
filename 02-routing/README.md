# 02 · Routing

> Classify the input, then send it to a handler specialized for that category.

## What it is

Routing has two phases: **classify, then dispatch.** A first step decides *what
kind* of request came in; based on that label, you send it down a path — a
prompt, a model, or a toolset — built for exactly that category:

```
                 ┌─→ [handler A]
input → [router] ─┼─→ [handler B]
                 └─→ [handler C]
```

It's a **workflow**, not an agent: the routes are all predefined. The only thing
decided at runtime is *which* fixed path runs — not what the paths are.

## What it does

A classifier (an LLM, a smaller model, or even plain rules) assigns the input a
label. The label selects one specialized handler, and only that handler runs.
Because the handlers are separate, you can tune one without affecting the others
— optimizing the billing path can't degrade the technical path.

## When to use it

Reach for routing when the inputs fall into **distinct categories** that are
genuinely better handled separately, and you can **classify them accurately**.
The whole pattern hinges on the label being right: misclassify, and the wrong
handler gets the work.

Don't use it when one prompt handles everything well — that's simpler. Use it
when separation of concerns is buying you something.

**Examples from the article:** directing customer-service queries (general,
refund, technical) into different downstream prompts and tools; routing easy
questions to a small cheap model and hard ones to a larger capable model to save
cost and latency.

## Example

[`routing.py`](./routing.py) is a support-triage demo. It classifies each
message, then answers it with that category's specialized system prompt:

| Message | Route | Handler |
|---------|-------|---------|
| "I was double-charged — can I get a refund?" | `billing` | billing specialist prompt |
| "The app crashes when I upload a photo." | `technical` | support-engineer prompt |
| "What are your support hours?" | `general` | friendly-generalist prompt |

The whole pattern is the two calls in `handle()`: one to pick the label
(validated against `ROUTES`, with a `general` fallback), one to answer with
`ROUTES[label]`.

```bash
python 02-routing/routing.py
```

➡️ **Next:** [03 · Parallelization](../03-parallelization/) — run multiple calls at
once instead of choosing a single path.
