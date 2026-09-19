"""Researcher Agent — searches the web, reads docs, gathers info."""
from galaxy.core.agent import Agent
from galaxy.core.registry import agent_registry
from galaxy.core.permissions import PermissionSet, Permission, PermissionGrant

RESEARCHER_PERMISSIONS = PermissionSet(grants=[
    PermissionGrant(permission=Permission.BROWSER_NAVIGATE),
    PermissionGrant(permission=Permission.NETWORK_HTTP),
    PermissionGrant(permission=Permission.NETWORK_DOWNLOAD),
    PermissionGrant(permission=Permission.FILE_READ),
    PermissionGrant(permission=Permission.FILE_WRITE),
])


class ResearcherAgent(Agent):
    SYSTEM_PROMPT = """You are a Research agent.
Your specialty is finding information from the web, documentation, and APIs.

When given a task:
1. Use http_get to fetch web pages and API responses
2. Use download_file to save documents or data
3. Summarize findings in a clear, organized format
4. Write research results to files using write_file

Always cite your sources (URLs) and present information clearly.
"""

    def __init__(self, role="researcher", permissions=None, name=None):
        super().__init__(role, permissions or RESEARCHER_PERMISSIONS, name)


agent_registry.register_type("researcher", ResearcherAgent, RESEARCHER_PERMISSIONS)
