"""06 · Autonomous Agent — a minimal coding agent (one bash tool).

Inspired by Quark (https://github.com/averagejoeslab/quark): one loop, one bash
tool, the model drives. We seed a sandbox with a stub function and a failing
test, give the agent a single `bash` tool, and let it work until the tests pass.

    task → [model plans → runs bash → sees output] → repeat → done

With just bash the agent does everything itself — read files, write code, run
the tests — and uses the real command output as ground truth to decide its next
move. It loops until it stops requesting tools (it considers the task done) or
hits a hard iteration cap.

⚠️  The bash tool runs real shell commands on your machine (with the sandbox as
the working directory, but this is NOT a hardened sandbox). Run it in a
throwaway / trusted environment.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 06-autonomous-agent/autonomous_agent.py
"""

import os
import subprocess
from pathlib import Path

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# The agent's working directory (gitignored). Commands run here.
SANDBOX = Path(__file__).resolve().parent / "sandbox"
MAX_ITERATIONS = 15  # the stopping condition — never let an agent loop forever

SYSTEM_PROMPT = (
    "You are a coding agent working in a sandbox directory. You have one tool: "
    "bash. Use it to read files, write code, and run commands. Work step by step "
    "until the task is complete; when it is, reply with a short summary instead "
    "of calling bash again."
)

TASK = (
    "The sandbox contains string_utils.py (a stub) and test_string_utils.py. "
    "Implement slugify() in string_utils.py so the tests pass. Run "
    "`python test_string_utils.py` to check your work."
)

# Files seeded into the sandbox at startup so the run is reproducible.
STUB = '''def slugify(text):
    """Convert text into a URL slug (lowercase, words joined by hyphens)."""
    raise NotImplementedError
'''

TEST = '''from string_utils import slugify

assert slugify("Hello World") == "hello-world"
assert slugify("  Spaced  Out  ") == "spaced-out"
assert slugify("Already-Slug") == "already-slug"
print("ALL TESTS PASSED")
'''

# The single tool — exactly like Quark's one bash tool.
BASH_TOOL = {
    "name": "bash",
    "description": "Run a bash command in the sandbox and return its output.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string", "description": "The command to run."}},
        "required": ["command"],
    },
}


def run_bash(command: str) -> str:
    """Execute a bash command in the sandbox; return its exit code and output."""
    try:
        proc = subprocess.run(
            command, shell=True, cwd=SANDBOX,
            capture_output=True, text=True, timeout=30,
        )
        output = (proc.stdout + proc.stderr).strip()
        return f"exit {proc.returncode}\n{output}".strip()
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


def seed_sandbox() -> None:
    SANDBOX.mkdir(exist_ok=True)
    (SANDBOX / "string_utils.py").write_text(STUB)
    (SANDBOX / "test_string_utils.py").write_text(TEST)


def run_agent(task: str) -> str:
    seed_sandbox()
    messages = [{"role": "user", "content": task}]

    for step in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=[BASH_TOOL],
            messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"[step {step}] {block.text.strip()}")
            elif block.type == "tool_use":
                print(f"[step {step}] bash: {block.input['command']}")

        # The model stopped asking for tools → it considers the task done.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Run each requested command and feed the output back.
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_bash(block.input["command"])
                print(f"          {output}")
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
        messages.append({"role": "user", "content": results})

    return "(reached the iteration cap without finishing)"


if __name__ == "__main__":
    print(f"Task: {TASK}\n")
    print(f"(working in {SANDBOX})\n")
    result = run_agent(TASK)
    print("\n--- agent finished ---")
    print(result)
