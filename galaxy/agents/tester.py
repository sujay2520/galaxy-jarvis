"""Tester Agent — writes and runs tests."""
from galaxy.core.agent import Agent
from galaxy.core.registry import agent_registry
from galaxy.core.permissions import PermissionSet, Permission, PermissionGrant

TESTER_PERMISSIONS = PermissionSet(grants=[
    PermissionGrant(permission=Permission.FILE_READ),
    PermissionGrant(permission=Permission.FILE_WRITE),
    PermissionGrant(permission=Permission.TERMINAL_EXECUTE),
])


class TesterAgent(Agent):
    SYSTEM_PROMPT = """You are a QA/Testing agent.
Your specialty is writing comprehensive tests and validating code quality.

When given a task:
1. Read the source code to understand what to test
2. Write unit tests covering edge cases
3. Run the tests using execute_command
4. Report results — passed, failed, coverage

Use appropriate testing frameworks (pytest for Python, jest for JS, etc.).
"""

    def __init__(self, role="tester", permissions=None, name=None):
        super().__init__(role, permissions or TESTER_PERMISSIONS, name)


agent_registry.register_type("tester", TesterAgent, TESTER_PERMISSIONS)
