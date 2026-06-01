"""06 · Autonomous Agent — a tool-using loop where the MODEL drives.

Business use case: a software-engineering agent. At startup we seed a sandbox
with a stub function and a failing test, then give the agent file tools plus a
`run_tests` tool and let it implement the function until the tests pass.

The agent decides the sequence of actions itself — read the test, write code, run
the tests, read the failure, fix it — using the real test output as ground truth
at each step. It loops until the tests pass (it stops on its own) or hits a hard
iteration cap.

Run it:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    python 06-autonomous-agent/autonomous_agent.py
"""

import os
import subprocess
import sys
from pathlib import Path

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

# Everything the agent does is confined to this scratch directory (gitignored).
SANDBOX = Path(__file__).resolve().parent / "sandbox"
TEST_FILE = "test_string_utils.py"

MAX_ITERATIONS = 12  # the stopping condition — never let an agent loop forever

SYSTEM_PROMPT = (
    "You are a software engineer working in a sandbox directory. Use the tools to "
    "read files, write code, and run the tests. Work iteratively: inspect the "
    "test, implement the function, run the tests, and fix any failures. When the "
    "tests pass, stop and give a one-line summary instead of calling another tool."
)

TASK = (
    "Implement the slugify() function in string_utils.py so that "
    f"{TEST_FILE} passes. Read the test first, then write the implementation, and "
    "run the tests to confirm."
)

# Files seeded into the sandbox at startup: a stub to implement and a test that
# checks it. The agent's job is to make the test pass.
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
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file in the sandbox with the given text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "run_tests",
        "description": "Run the test file and return its exit code and output.",
        "input_schema": {"type": "object", "properties": {}},
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
            files = sorted(p.name for p in SANDBOX.iterdir() if p.is_file())
            return "Files: " + ", ".join(files)

        if name == "read_file":
            return _safe_path(tool_input["filename"]).read_text()

        if name == "write_file":
            _safe_path(tool_input["filename"]).write_text(tool_input["content"])
            return f"Wrote {tool_input['filename']}."

        if name == "run_tests":
            proc = subprocess.run(
                [sys.executable, TEST_FILE],
                cwd=SANDBOX,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return f"exit code {proc.returncode}\n{proc.stdout}{proc.stderr}".strip()

    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"

    return f"Unknown tool: {name}"


def seed_sandbox() -> None:
    """Write the stub + test into the sandbox so the run is reproducible."""
    SANDBOX.mkdir(exist_ok=True)
    (SANDBOX / "string_utils.py").write_text(STUB)
    (SANDBOX / TEST_FILE).write_text(TEST)


def run_agent(task: str) -> str:
    seed_sandbox()
    messages = [{"role": "user", "content": task}]

    for step in range(1, MAX_ITERATIONS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
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
    print(f"Task: {TASK}\n")
    print(f"(working in {SANDBOX})\n")
    result = run_agent(TASK)
    print("\n--- agent finished ---")
    print(result)
