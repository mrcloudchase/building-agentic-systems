"""06 · Autonomous Agent — a minimal coding agent (one bash tool).

A simplified take on Quark (https://github.com/averagejoeslab/quark): one loop,
one bash tool, the model drives. You type a request; the agent uses bash to carry
it out — inspecting the project, reading and writing files, running commands —
and gets the real command output back at each step, so it can course-correct
until your request is done. The conversation history is its memory across turns.

There is no built-in task: it's just the agent loop plus a bash tool.

    you → [model plans → runs bash → sees output] → repeat → reply

⚠️  The bash tool runs real shell commands on your machine — it is NOT sandboxed.
Run it in a throwaway / trusted directory.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 06-autonomous-agent/autonomous_agent.py
"""

import os
import subprocess

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

MAX_STEPS = 25  # safety cap on tool calls per request

SYSTEM_PROMPT = (
    "You are a coding agent. You have one tool: bash. Use it to inspect the "
    "project, read and write files, and run commands. Work step by step, and when "
    "the user's request is done, reply with a short summary instead of calling "
    "bash again."
)

BASH_TOOL = {
    "name": "bash",
    "description": "Run a bash command and return its output.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string", "description": "The command to run."}},
        "required": ["command"],
    },
}


def run_bash(command: str) -> str:
    """Execute a bash command; return its exit code and combined output."""
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=60
        )
        return f"exit {proc.returncode}\n{(proc.stdout + proc.stderr).strip()}".strip()
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


def agent_turn(messages: list) -> None:
    """Run the tool loop until the model stops calling bash."""
    for _ in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=[BASH_TOOL],
            messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n{block.text.strip()}")
            elif block.type == "tool_use":
                print(f"\n$ {block.input['command']}")

        messages.append({"role": "assistant", "content": response.content})

        # No tool requested → the model is done with this request.
        if response.stop_reason != "tool_use":
            return

        # Run each command and feed the output back.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_bash(block.input["command"])
                print(output)
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    print("Coding agent (one bash tool). Type a request, or Ctrl-D to quit.\n")
    messages: list = []  # the conversation history is the agent's memory
    while True:
        try:
            user = input("you> ").strip()
        except EOFError:
            break
        if not user:
            continue
        messages.append({"role": "user", "content": user})
        agent_turn(messages)
        print()
