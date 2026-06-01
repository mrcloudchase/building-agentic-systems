# Building Agentic Systems

Runnable Python examples of the agentic patterns described in Anthropic's
[**Building Effective Agents**](https://www.anthropic.com/research/building-effective-agents)
(Erik Schluntz & Barry Zhang, December 2024).

Each folder teaches **one** pattern: a short, heavily-commented program plus a
README that explains the pattern the way you'd explain it to a colleague — what
it is, when to reach for it, and how the code maps to the idea.

## The big idea

The article's thesis is simple:

> **The most successful agentic implementations use simple, composable patterns
> rather than complex frameworks.**

Start with the simplest thing that works — often a single LLM call. Add
complexity *only* when it measurably improves outcomes, because every step you
add trades latency and cost for capability.

It also draws one important distinction:

- **Workflows** — LLMs and tools orchestrated through **predefined code paths**.
  *You* decide the control flow. Predictable and consistent.
- **Agents** — the LLM **dynamically directs its own process** and tool usage.
  *The model* decides the control flow. Flexible and open-ended.

Everything is built from one foundational block: the **augmented LLM** (an LLM
with retrieval, tools, and memory).

## The patterns

| # | Pattern | Type | One-liner |
|---|---------|------|-----------|
| [00](./00-augmented-llm/) | Augmented LLM | building block | An LLM that can call tools — the unit everything else is made of |
| [01](./01-prompt-chaining/) | Prompt Chaining | workflow | Decompose a task into a fixed sequence of steps, with optional gates |
| [02](./02-routing/) | Routing | workflow | Classify the input, then send it to a specialized handler |
| [03](./03-parallelization/) | Parallelization | workflow | Run LLM calls concurrently — sectioning and voting |
| [04](./04-orchestrator-workers/) | Orchestrator-Workers | workflow | An orchestrator dynamically splits work and delegates to workers |
| [05](./05-evaluator-optimizer/) | Evaluator-Optimizer | workflow | One LLM generates, another critiques, loop until good enough |
| [06](./06-autonomous-agent/) | Autonomous Agent | agent | A tool-using loop that runs until the task is done |

Patterns 01–05 are **workflows** (you control the flow). Pattern 06 is a true
**agent** (the model controls the flow). Pattern 00 is the building block they
all share.

## Setup

```bash
# 1. Install the Anthropic SDK
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. (Optional) pick a cheaper/faster model for experimentation
export ANTHROPIC_MODEL="claude-sonnet-4-6"   # defaults to claude-opus-4-8
```

## Running an example

Each example is a standalone script. Run any of them from the repo root:

```bash
python 01-prompt-chaining/prompt_chaining.py
python 02-routing/routing.py
python 03-parallelization/parallelization.py
python 04-orchestrator-workers/orchestrator_workers.py
python 05-evaluator-optimizer/evaluator_optimizer.py
python 00-augmented-llm/augmented_llm.py
python 06-autonomous-agent/autonomous_agent.py
```

All examples share [`shared.py`](./shared.py), which holds the client setup and
a tiny `complete()` helper so each file can focus on the pattern itself.

## How to read this repo

Go in order. Pattern 00 shows you the building block. Patterns 01–05 show you
increasingly flexible *workflows* built from that block. Pattern 06 shows you
what happens when you hand control of the flow to the model itself.

The guiding question at every step: **could a simpler pattern have done this
job?** If yes, use the simpler one. That's the whole lesson of the article.
