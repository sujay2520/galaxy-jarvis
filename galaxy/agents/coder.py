"""Coder Agent — writes code, creates files, implements features."""
from galaxy.core.agent import Agent
from galaxy.core.registry import agent_registry
from galaxy.core.permissions import PermissionSet, Permission, PermissionGrant


CODER_PERMISSIONS = PermissionSet(grants=[
    PermissionGrant(permission=Permission.FILE_READ),
    PermissionGrant(permission=Permission.FILE_WRITE),
    PermissionGrant(permission=Permission.TERMINAL_EXECUTE),
])


class CoderAgent(Agent):
    SYSTEM_PROMPT = """You are an expert software engineer agent (Coder).
Your specialty is writing clean, production-quality code.

When given a task:
1. First understand what needs to be built
2. Plan the file structure
3. Write the code file by file using the write_file tool
4. Test your code using execute_command when appropriate
5. Report what you built

Best practices:
- Write complete, working code — no placeholders or TODOs
- Include proper imports, error handling, and comments
- Create directory structures as needed
- Follow the project's coding conventions if visible
"""

    def __init__(self, role="coder", permissions=None, name=None):
        super().__init__(role, permissions or CODER_PERMISSIONS, name)


agent_registry.register_type("coder", CoderAgent, CODER_PERMISSIONS)
