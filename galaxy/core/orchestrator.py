"""Galaxy Orchestrator — The Director that manages multi-agent task execution.

Takes a high-level task, uses LLM to decompose it into subtasks,
spawns specialized agents with appropriate permissions, and coordinates
their work with authority attenuation.
"""
import asyncio
import json
import uuid
import time
from typing import List, Dict, Any, Optional
from galaxy.core.registry import agent_registry
from galaxy.core.events import event_bus, Event, EventType
from galaxy.tools.file_tool import ReadFileTool, WriteFileTool, ListDirectoryTool, DeleteFileTool
from galaxy.tools.terminal_tool import TerminalExecuteTool, InstallPackageTool
from galaxy.tools.network_tool import HttpGetTool, HttpPostTool, DownloadFileTool


# Tool registry: maps tool names to instances
AVAILABLE_TOOLS = {
    "read_file": ReadFileTool(),
    "write_file": WriteFileTool(),
    "list_directory": ListDirectoryTool(),
    "delete_file": DeleteFileTool(),
    "execute_command": TerminalExecuteTool(),
    "install_package": InstallPackageTool(),
    "http_get": HttpGetTool(),
    "http_post": HttpPostTool(),
    "download_file": DownloadFileTool(),
}

# Which tools each role gets access to
ROLE_TOOLS = {
    "coder": ["read_file", "write_file", "list_directory", "execute_command"],
    "tester": ["read_file", "write_file", "execute_command"],
    "researcher": ["read_file", "write_file", "http_get", "download_file"],
    "devops": ["read_file", "write_file", "list_directory", "execute_command", "install_package"],
    "reviewer": ["read_file", "list_directory"],
}


class Task:
    """Represents a top-level task being orchestrated."""

    def __init__(self, description: str):
        self.id = str(uuid.uuid4())
        self.description = description
        self.status = "pending"  # pending, planning, executing, completed, error
        self.subtasks: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.created_at = time.time()
        self.completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "subtasks": self.subtasks,
            "results": self.results,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class Orchestrator:
    """Coordinates multi-agent task execution with LLM-powered planning."""

    PLANNING_PROMPT = """You are the Galaxy Orchestrator. Your job is to break down a user's task
into actionable subtasks and assign each to the best agent role.

Available agent roles:
- **coder**: Writes code, creates files, runs scripts. Tools: read_file, write_file, list_directory, execute_command
- **tester**: Writes and runs tests. Tools: read_file, write_file, execute_command
- **researcher**: Searches the web, downloads content. Tools: read_file, write_file, http_get, download_file
- **devops**: Manages deployments, installs packages. Tools: read_file, write_file, list_directory, execute_command, install_package
- **reviewer**: Reviews code (read-only). Tools: read_file, list_directory

Respond with a JSON array of subtasks:
```json
[
    {"role": "coder", "task": "Create the project structure and main files", "priority": 1},
    {"role": "coder", "task": "Implement the core logic in main.py", "priority": 2},
    {"role": "tester", "task": "Write unit tests for the core logic", "priority": 3}
]
```

Rules:
- Order subtasks by priority (1 = first)
- Tasks with the same priority can run in parallel
- Be specific in task descriptions — tell the agent exactly what to create/do
- Include the working directory context if relevant
"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._active_agents: Dict[str, Any] = {}

    async def process_task(self, description: str, working_dir: str = ".") -> Dict[str, Any]:
        """Process a high-level task: plan, spawn agents, coordinate."""
        from galaxy.llm.router import llm_router

        task = Task(description)
        self.tasks[task.id] = task

        # Phase 1: Plan — decompose the task
        task.status = "planning"
        await event_bus.publish(Event(
            type=EventType.TaskAssigned,
            payload={"task_id": task.id, "description": description, "phase": "planning"},
            source="orchestrator",
        ))

        plan_messages = [
            {"role": "system", "content": self.PLANNING_PROMPT},
            {"role": "user", "content": f"Task: {description}\nWorking directory: {working_dir}"},
        ]

        try:
            plan_response = await llm_router.generate(plan_messages, complexity="complex")
            subtasks = self._parse_plan(plan_response)

            if not subtasks:
                # Fallback: assign entire task to a coder agent
                subtasks = [{"role": "coder", "task": description, "priority": 1}]

            task.subtasks = subtasks
            task.status = "executing"

        except Exception as e:
            task.status = "error"
            task.results.append({"error": f"Planning failed: {e}"})
            return task.to_dict()

        # Phase 2: Execute — spawn agents grouped by priority
        priorities = sorted(set(st.get("priority", 1) for st in subtasks))

        for priority in priorities:
            batch = [st for st in subtasks if st.get("priority", 1) == priority]

            # Run same-priority subtasks concurrently
            agent_tasks = []
            for st in batch:
                role = st.get("role", "coder")
                subtask_desc = st.get("task", description)

                try:
                    agent = agent_registry.spawn(role, name=f"{role}-{task.id[:6]}")
                    self._register_tools_for_agent(agent, role)
                    self._active_agents[agent.id] = agent
                    agent_tasks.append(self._run_agent(agent, subtask_desc, task))
                except Exception as e:
                    task.results.append({
                        "role": role,
                        "subtask": subtask_desc,
                        "error": str(e),
                    })

            if agent_tasks:
                results = await asyncio.gather(*agent_tasks, return_exceptions=True)
                for r in results:
                    if isinstance(r, Exception):
                        task.results.append({"error": str(r)})
                    else:
                        task.results.append(r)

        # Phase 3: Complete
        task.status = "completed"
        task.completed_at = time.time()

        await event_bus.publish(Event(
            type=EventType.TaskCompleted,
            payload={"task_id": task.id, "results": task.results},
            source="orchestrator",
        ))

        return task.to_dict()

    def _register_tools_for_agent(self, agent, role: str):
        """Give an agent only the tools allowed for its role."""
        tool_names = ROLE_TOOLS.get(role, ["read_file"])
        for name in tool_names:
            if name in AVAILABLE_TOOLS:
                agent.register_tool(AVAILABLE_TOOLS[name])

    async def _run_agent(self, agent, subtask: str, parent_task: Task) -> Dict[str, Any]:
        """Run a single agent on a subtask."""
        try:
            result = await agent.run(subtask)
            return {
                "agent": agent.name,
                "role": agent.role,
                "subtask": subtask,
                "result": result,
            }
        except Exception as e:
            return {
                "agent": agent.name,
                "role": agent.role,
                "subtask": subtask,
                "error": str(e),
            }

    def _parse_plan(self, response: str) -> List[Dict[str, Any]]:
        """Extract the subtask JSON array from LLM response."""
        import re
        # Try ```json block first
        match = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try raw JSON array
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return []

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.tasks.values()]


orchestrator = Orchestrator()
