# 02 · Routing

> Classify the input, then send it to a handler specialized for that category.

## What it is

Routing has two phases: **classify, then dispatch.** A first step (an LLM, a
smaller model, or even plain rules) decides *what kind* of request came in and
assigns it a label; that label selects one specialized path — a prompt, a model,
or a toolset — and only that path runs:

```
                 ┌─→ [handler A]
input → [router] ─┼─→ [handler B]
                 └─→ [handler C]
```

It's a **workflow**, not an agent: the routes are all predefined, and the only
thing decided at runtime is *which* fixed path runs. Because the handlers are
separate, you can tune one without affecting the others — optimizing the billing
path can't degrade the technical path.

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

[`routing.py`](./routing.py) triages a shared inbox: one call classifies the
email, a second answers with that category's system prompt.

```python
routes = {"sales": "You are a sales rep.", "billing": "You are a billing specialist.",
          "technical": "You are a support engineer.", "careers": "You are a recruiter."}
email = "Could we set up a demo and talk about enterprise pricing?"
category = ask(f"Classify into one of {', '.join(routes)} — reply with one word:\n{email}").strip().lower()
print(f"[{category}]", ask(email, routes.get(category, "You are a helpful assistant.")))
```

The classifier's labels come straight from the `routes` keys, so adding a
category updates the routing automatically. Run it:

```bash
python 02-routing/routing.py
```

➡️ **Next:** [03 · Parallelization](../03-parallelization/) — run multiple calls at
once instead of choosing a single path.
