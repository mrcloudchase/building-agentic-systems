# 00 · The Augmented LLM

> The building block every other pattern is made of.

## What it is

Before you can talk about workflows or agents, you need the unit they're built
from. The article calls it the **augmented LLM**: a language model enhanced with

- **tools** — functions the model can call to act on the world,
- **retrieval** — the ability to pull in outside knowledge, and
- **memory** — the ability to carry state across turns.

The key insight is that the model doesn't just *passively* receive these
capabilities — it *actively decides* how to use them. It generates its own
search queries, picks which tool to call, and decides what's worth remembering.

Everything else in this repo is a way of *arranging* augmented LLM calls. Get
this one right and the rest is composition.

## How tool use actually works

A plain LLM call is "text in, text out." An augmented call adds a loop:

```
1. You send a prompt + a list of tool definitions.
2. The model either answers directly, OR asks to call a tool
   (stop_reason == "tool_use").
3. YOU run the tool and send the result back.
4. The model continues — answering, or calling another tool.
5. Repeat until the model stops asking for tools (stop_reason == "end_turn").
```

Two things are worth burning into memory:

- **You execute the tools, not the model.** The model only *requests* a call
  with structured arguments. Your code runs it and reports back. This is the
  security boundary — the model can't do anything you didn't give it a tool for.
- **The conversation accumulates.** Each tool call and result is appended to the
  message history, which is what gives the model "memory" within the task.

## What the example does

[`augmented_llm.py`](./augmented_llm.py) gives Claude two tools — a calculator
and a tiny mock "knowledge base" lookup — and asks a question that needs both.
You'll see the model:

1. decide it needs a fact, call `search_knowledge_base`,
2. decide it needs arithmetic, call `calculator`,
3. then combine the results into a final answer.

The whole thing is a hand-written tool-use loop so you can see every step. (The
SDK has a `tool_runner` helper that hides this loop — but you should understand
the loop before you let something run it for you.)

## When this is all you need

A huge fraction of "AI features" are just *one* augmented LLM call:
classification, summarization, extraction, answering a question with retrieval.
If a single call with good tools and a clear prompt solves your problem,
**stop there.** Don't reach for a workflow or an agent. The article is emphatic
about this — simplicity first.

## The interface is the product

The article's third guiding principle is to "prompt-engineer your tools." Spend
as much care on tool names, descriptions, and parameter docs as you do on your
prompts. The model decides whether and how to call a tool based almost entirely
on its description — a vague description produces vague tool use.

➡️ **Next:** [01 · Prompt Chaining](../01-prompt-chaining/) — the simplest way to
compose multiple LLM calls.
