"""00 · The Augmented LLM — an LLM that can call tools.

This is the building block for every other pattern. We give Claude two tools
and run the tool-use loop by hand so you can see each step: the model requests a
tool, *we* execute it, we hand the result back, and the model continues until it
has a final answer.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 00-augmented-llm/augmented_llm.py
"""

import os

import anthropic

# Defaults to the most capable Claude model. Override with ANTHROPIC_MODEL to
# experiment with a cheaper/faster one (the pattern is identical either way).
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# Reads ANTHROPIC_API_KEY from the environment.
client = anthropic.Anthropic()


# --- The tools the model is allowed to call --------------------------------
# Each tool needs a name, a description (the model reads this to decide when to
# use it — write it carefully), and a JSON Schema for its inputs.

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression and return the "
        "numeric result. Use this for any math instead of computing it yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python arithmetic expression, e.g. '42 * 1.08'.",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "search_knowledge_base",
        "description": "Look up a fact in the company knowledge base. Use this "
        "when you need company-specific information you don't already know.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to look up, e.g. 'sales tax rate'.",
                }
            },
            "required": ["query"],
        },
    },
]


# --- The actual implementations (this is YOUR code, not the model's) -------

# A stand-in for a real database / vector store / API.
_KNOWLEDGE_BASE = {
    "sales tax rate": "The sales tax rate is 8%.",
    "widget price": "A single widget costs $42.",
}


def run_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool call to its implementation and return a string result."""
    if name == "calculator":
        # In real code, never eval() untrusted input. This is a teaching demo.
        try:
            return str(eval(tool_input["expression"], {"__builtins__": {}}))
        except Exception as exc:  # noqa: BLE001
            return f"Error evaluating expression: {exc}"

    if name == "search_knowledge_base":
        query = tool_input["query"].lower()
        for key, value in _KNOWLEDGE_BASE.items():
            if key in query or query in key:
                return value
        return "No matching entry found in the knowledge base."

    return f"Unknown tool: {name}"


# --- The tool-use loop ------------------------------------------------------


def ask(question: str) -> str:
    """Run an augmented LLM call: keep going until the model stops using tools."""
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        # Print anything the model said out loud this turn.
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"  [model] {block.text.strip()}")
            elif block.type == "tool_use":
                print(f"  [tool call] {block.name}({block.input})")

        # If the model didn't ask for a tool, it's done.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Otherwise: append the model's turn, run each requested tool, and send
        # the results back as a single user message.
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"  [tool result] {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    question = (
        "How much would 5 widgets cost in total, including sales tax? "
        "Look up the prices and tax rate rather than guessing."
    )
    print(f"Question: {question}\n")
    print("--- tool-use loop ---")
    answer = ask(question)
    print("\n--- final answer ---")
    print(answer)
