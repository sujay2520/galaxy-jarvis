"""Galaxy Core Agent — Base class for all specialized agents.

Implements a proper think → plan → act → observe execution loop
with real tool calling through the permission-gated tool layer.
"""
import asyncio
import uuid
import json
import re
from typing import List, Dict, Any, Optional
from galaxy.core.permissions import PermissionSet, permission_engine
from galaxy.core.events import event_bus, Event, EventType

class AgentStatus:
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting_approval"
    ERROR = "error"
    COMPLETED = "completed"


class Agent:
    """Base agent with LLM reasoning and permission-gated tool execution."""

    # Subclasses override this with their system prompt
    SYSTEM_PROMPT: str = "You are a helpful AI agent."

    # Max iterations before agent stops (safety limit)
    MAX_STEPS: int = 15

    def __init__(self, role: str, permissions: PermissionSet, name: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name or f"{role}-{self.id[:8]}"
        self.role = role
        self.status = AgentStatus.IDLE
        self.memory: List[Dict[str, str]] = []
        self.current_task: Optional[str] = None
        self.results: List[Dict[str, Any]] = []
        self._tools: Dict[str, Any] = {}

        # Register permissions with the engine
        permission_engine.register_agent(self.id, permissions)

    def register_tool(self, tool):
        """Register a tool instance this agent can use."""
        self._tools[tool.name] = tool

    def get_tool_descriptions(self) -> str:
        """Generate tool descriptions for the LLM system prompt."""
        if not self._tools:
            return "No tools available."
        lines = []
        for name, tool in self._tools.items():
            lines.append(f"- **{name}**: {tool.description}")
        return "\n".join(lines)

    def _build_system_prompt(self) -> str:
        """Construct the full system prompt with tools and instructions."""
        tool_desc = self.get_tool_descriptions()
        return f"""{self.SYSTEM_PROMPT}

## Available Tools
{tool_desc}

## How to Use Tools
When you need to use a tool, respond with a JSON block in this format:
```tool
{{"tool": "tool_name", "args": {{"arg1": "value1", "arg2": "value2"}}}}
```

You may call multiple tools by including multiple ```tool blocks.

When you have completed the task, include the word TASK_COMPLETE in your response
along with a summary of what you accomplished.

## Rules
- Only use tools you have been given.
- Think step-by-step before acting.
- After each tool result, analyze the output and decide next steps.
- If a tool returns a permission error, do NOT retry — report the issue.
"""

    async def run(self, task: str) -> Dict[str, Any]:
        """Execute a task through the think-plan-act-observe loop."""
        from galaxy.llm.router import llm_router

        self.current_task = task
        self.status = AgentStatus.WORKING
        self.memory = []
        self.results = []

        await event_bus.publish(Event(
            type=EventType.AgentStarted,
            payload={"agent": self.name, "task": task},
            source=self.id,
        ))

        # Initialize conversation
        self.memory.append({"role": "system", "content": self._build_system_prompt()})
        self.memory.append({"role": "user", "content": f"Task: {task}"})

        final_result = {"status": "error", "output": "Max steps exceeded"}

        try:
            for step in range(self.MAX_STEPS):
                # Think — ask the LLM what to do
                response = await llm_router.generate(self.memory, complexity="complex")
                self.memory.append({"role": "assistant", "content": response})

                # Check if agent considers itself done
                if "TASK_COMPLETE" in response:
                    final_result = {
                        "status": "completed",
                        "output": response,
                        "steps": step + 1,
                    }
                    break

                # Act — parse and execute any tool calls
                tool_calls = self._parse_tool_calls(response)
                if not tool_calls:
                    # No tool calls and not done — ask LLM to continue
                    self.memory.append({
                        "role": "user",
                        "content": "Continue working on the task. Use tools if needed, or say TASK_COMPLETE if done.",
                    })
                    continue

                # Execute each tool call and collect observations
                observations = []
                for tc in tool_calls:
                    tool_name = tc.get("tool", "")
                    args = tc.get("args", {})

                    if tool_name not in self._tools:
                        obs = f"[{tool_name}] Error: Tool not available."
                    else:
                        tool = self._tools[tool_name]
                        result = await tool.execute(self.id, **args)
                        self.results.append({
                            "tool": tool_name,
                            "args": args,
                            "result": result,
                        })
                        obs = f"[{tool_name}] Result:\n```json\n{json.dumps(result, indent=2, default=str)}\n```"
                    observations.append(obs)

                # Observe — feed tool results back to the LLM
                observation_text = "\n\n".join(observations)
                self.memory.append({
                    "role": "user",
                    "content": f"Tool Results:\n{observation_text}\n\nAnalyze these results and continue. Use more tools or say TASK_COMPLETE if done.",
                })

            self.status = AgentStatus.COMPLETED
            await event_bus.publish(Event(
                type=EventType.AgentCompleted,
                payload={"agent": self.name, "result": final_result},
                source=self.id,
            ))
            return final_result

        except Exception as e:
            self.status = AgentStatus.ERROR
            error_result = {"status": "error", "error": str(e)}
            await event_bus.publish(Event(
                type=EventType.AgentError,
                payload={"agent": self.name, "error": str(e)},
                source=self.id,
            ))
            return error_result

        finally:
            self.current_task = None

    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Extract ```tool ... ``` JSON blocks from LLM response."""
        calls: List[Dict[str, Any]] = []
        # Match ```tool ... ``` blocks
        pattern = r"```tool\s*\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match.strip())
                if "tool" in parsed:
                    calls.append(parsed)
            except json.JSONDecodeError:
                continue

        # Also try to match plain JSON tool calls (fallback)
        if not calls:
            pattern2 = r'\{"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{[^}]*\}\s*\}'
            matches2 = re.findall(pattern2, response)
            for match in matches2:
                try:
                    parsed = json.loads(match)
                    if "tool" in parsed:
                        calls.append(parsed)
                except json.JSONDecodeError:
                    continue

        return calls
