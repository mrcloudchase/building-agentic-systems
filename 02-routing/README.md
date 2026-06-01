# 02 · Routing

> Classify the input, then send it to a specialized handler.

## What it is

Routing separates **classification** from **handling**. A first LLM call looks
at the input and decides what *kind* of thing it is; based on that, you direct
it to a prompt (or model, or pipeline) specialized for that category:

```
                 ┌─→ [billing handler]
input → [router] ─┼─→ [technical handler]
                 └─→ [general handler]
```

It's still a **workflow** — the routes are predefined; the only dynamic choice
is *which* fixed path to take.

## Why route?

**Separation of concerns.** Without routing, you'd cram instructions for every
case into one giant prompt, and optimizing it for billing questions would
degrade it for technical ones. Routing lets each handler have a focused prompt
tuned for exactly its category. Improving the billing flow can't break the
technical flow.

It also enables a useful cost trick: route easy inputs to a small, cheap model
and hard ones to a large, capable model.

## The one prerequisite: accurate classification

Routing only works if you can classify reliably. If the router constantly
mislabels inputs, every downstream handler gets the wrong work. So the
classification step deserves real attention — clear category definitions, and
ideally a structured output so you get back a clean label instead of prose you
have to parse.

## What the example does

[`routing.py`](./routing.py) is a customer-support triage. The router classifies
each incoming message into `billing`, `technical`, or `general`, and then a
category-specific handler — each with its own tailored system prompt — answers
it. The router is forced to return one of the valid labels so the routing
decision is unambiguous.

Try the three sample messages and watch each one take a different path.

## When to use it

Reach for routing when:

- the inputs fall into **distinct categories** that are genuinely better handled
  separately, and
- you can **classify them accurately** (by LLM or by plain rules).

**Examples from the article:** directing customer-service queries (refund vs.
technical support vs. general) into different downstream flows; sending easy
questions to a smaller model and hard ones to a more capable model to save cost.

➡️ **Next:** [03 · Parallelization](../03-parallelization/) — run multiple calls at
once instead of choosing one path.
