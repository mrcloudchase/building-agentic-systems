"""06 · Autonomous Agent — a coding agent in under 15 lines.

One loop, one bash tool, the model drives (in the spirit of Quark:
github.com/averagejoeslab/quark). Type a request; the agent runs bash commands to
carry it out and feeds the output back to itself until it's done. The
conversation history is its memory; Ctrl-C to quit.

⚠️  bash runs real shell commands on your machine — it is NOT sandboxed. Run it
in a throwaway / trusted directory.

    pip install anthropic && export ANTHROPIC_API_KEY=sk-ant-...
    python 06-autonomous-agent/autonomous_agent.py
"""

import subprocess, anthropic

client = anthropic.Anthropic()
TOOLS = [{"name": "bash", "description": "Run a bash command.", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}]
def sh(cmd): return subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
messages = []
while True:
    messages.append({"role": "user", "content": input("\nyou> ")})
    while True:
        r = client.messages.create(model="claude-opus-4-8", max_tokens=4096, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        print("".join(b.text for b in r.content if b.type == "text"))
        if r.stop_reason != "tool_use": break
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": b.id, "content": sh(b.input["command"]) or "(no output)"} for b in r.content if b.type == "tool_use"]})
