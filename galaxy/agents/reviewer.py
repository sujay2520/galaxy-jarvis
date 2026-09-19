"""Reviewer Agent — reviews code and suggests improvements (read-only)."""
from galaxy.core.agent import Agent
from galaxy.core.registry import agent_registry
from galaxy.core.permissions import PermissionSet, Permission, PermissionGrant

REVIEWER_PERMISSIONS = PermissionSet(grants=[
    PermissionGrant(permission=Permission.FILE_READ),
])


class ReviewerAgent(Agent):
    SYSTEM_PROMPT = """You are a Code Review agent.
Your specialty is reviewing code for quality, bugs, security, and best practices.

When given a task:
1. Read the source code using read_file
2. Analyze for: bugs, security issues, code smells, missing error handling
3. Suggest improvements with specific code examples
4. Rate the overall code quality (1-10)

You have READ-ONLY access — you cannot modify files.
Focus on being thorough but constructive in your feedback.
"""

    def __init__(self, role="reviewer", permissions=None, name=None):
        super().__init__(role, permissions or REVIEWER_PERMISSIONS, name)


agent_registry.register_type("reviewer", ReviewerAgent, REVIEWER_PERMISSIONS)
