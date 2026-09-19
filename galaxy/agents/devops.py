"""DevOps Agent — manages deployments, infrastructure, CI/CD."""
from galaxy.core.agent import Agent
from galaxy.core.registry import agent_registry
from galaxy.core.permissions import PermissionSet, Permission, PermissionGrant

DEVOPS_PERMISSIONS = PermissionSet(grants=[
    PermissionGrant(permission=Permission.FILE_READ),
    PermissionGrant(permission=Permission.FILE_WRITE),
    PermissionGrant(permission=Permission.TERMINAL_EXECUTE),
    PermissionGrant(permission=Permission.TERMINAL_INSTALL),
    PermissionGrant(permission=Permission.PROCESS_SPAWN),
])


class DevOpsAgent(Agent):
    SYSTEM_PROMPT = """You are a DevOps agent.
Your specialty is infrastructure, deployment, and system configuration.

When given a task:
1. Set up project environments and dependencies
2. Install required packages using install_package
3. Configure build tools, Docker, CI/CD
4. Run deployment scripts and verify results

Always check for existing configuration before making changes.
"""

    def __init__(self, role="devops", permissions=None, name=None):
        super().__init__(role, permissions or DEVOPS_PERMISSIONS, name)


agent_registry.register_type("devops", DevOpsAgent, DEVOPS_PERMISSIONS)
