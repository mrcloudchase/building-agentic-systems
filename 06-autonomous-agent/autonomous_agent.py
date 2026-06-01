"""06 · Autonomous Agent — a tool-using loop where the MODEL drives.

We hand Claude a goal and file tools scoped to a sandbox directory, then let it
decide the sequence of actions itself. The loop runs until the model stops
requesting tools (it considers the task done), with a hard iteration cap as a
safety stop.

Mechanically it's a tool-use loop, but the mindset is open-ended: the model
chooses the steps and runs to completion on its own.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 06-autonomous-agent/autonomous_agent.py
"""

import os
from pathlib import Path

import anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

# Everything the agent does is confined to this scratch directory (gitignored).
SANDBOX = Path(__file__).resolve().parent / "sandbox"

MAX_ITERATIONS = 10  # the stopping condition — never let an agent loop forever

SYSTEM_PROMPT = (
    "You are a careful file-system agent working inside a sandbox directory. "
    "Use the provided tools to accomplish the user's task. Think step by step, "
    "take one action at a time, and when the task is fully complete, reply with "
    "a brief summary instead of calling another tool."
)

TOOLS = [
    {
        "name": "list_files",
        "description": "List the files currently in the sandbox directory.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_file",
        "description": "Read and return the contents of a file in the sandbox.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to read."}
            },
            "required": ["filename"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file in the sandbox with the given text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Name of the file to write."},
                "content": {"type": "string", "description": "Text to write into the file."},
            },
            "required": ["filename", "content"],
        },
    },
]


def _safe_path(filename: str) -> Path:
    """Resolve a filename inside the sandbox, refusing path traversal."""
    target = (SANDBOX / filename).resolve()
    if SANDBOX.resolve() not in target.parents and target != SANDBOX.resolve():
        raise ValueError("Path escapes the sandbox.")
    return target


def run_tool(name: str, tool_input: dict) -> str:
    """Execute a tool call (this is YOUR code — the model only requested it)."""
    try:
        if name == "list_files":
            files = [p.name for p in SANDBOX.iterdir() if p.is_file()]
            return "Files: " + (", ".join(sorted(files)) if files else "(empty)")

        if name == "read_file":
            return _safe_path(tool_input["filename"]).read_text()

        if name == "write_file":
            path = _safe_path(tool_input["filename"])
            path.write_text(tool_input["content"])
            return f"Wrote {len(tool_input['content'])} chars to {tool_input['filename']}."

    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"

    return f"Unknown tool: {name}"


def run_agent(task: str) -> str:
    SANDBOX.mkdir(exist_ok=True)
    messages = [{"role": "user", "content": task}]

    for step in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"[step {step}] thinking: {block.text.strip()}")
            elif block.type == "tool_use":
                print(f"[step {step}] action: {block.name}({block.input})")

        # The model stopped asking for tools → it considers the task done.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Run the requested tools and feed results back.
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"          observed: {result}")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )
        messages.append({"role": "user", "content": tool_results})

    return "(reached the iteration cap without finishing)"


if __name__ == "__main__":
    task = (
        "Create a file 'greeting.txt' containing a friendly hello message, then "
        "create 'summary.txt' that lists every file now in the directory and "
        "describes what you did. Then tell me you're done."
    )
    print(f"Task: {task}\n")
    print(f"(working in {SANDBOX})\n")
    result = run_agent(task)
    print("\n--- agent finished ---")
    print(result)
