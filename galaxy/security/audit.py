"""Galaxy Security — Audit logging for all agent actions."""
import json
import time
import os
from typing import List, Dict, Any, Optional
from galaxy.core.permissions import Permission


class AuditEntry:
    def __init__(self, agent_id: str, action: str, permission: Optional[str],
                 scope: Optional[str], result: str, details: Optional[Dict] = None):
        self.timestamp = time.time()
        self.agent_id = agent_id
        self.action = action
        self.permission = permission
        self.scope = scope
        self.result = result  # "allowed", "denied", "error"
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.timestamp)),
            "agent_id": self.agent_id,
            "action": self.action,
            "permission": self.permission,
            "scope": self.scope,
            "result": self.result,
            "details": self.details,
        }


class AuditLogger:
    """Thread-safe audit logger with in-memory buffer and optional file output."""

    def __init__(self, log_dir: str = ".galaxy_audit"):
        self._entries: List[AuditEntry] = []
        self._log_dir = log_dir
        self._max_entries = 10000

    def log_check(self, agent_id: str, permission: Permission,
                  scope: Optional[str], allowed: bool):
        """Log a permission check."""
        entry = AuditEntry(
            agent_id=agent_id,
            action="permission_check",
            permission=permission.value,
            scope=scope,
            result="allowed" if allowed else "denied",
        )
        self._add(entry)

    def log_tool(self, agent_id: str, tool_name: str, args: Dict,
                 result: str, details: Optional[Dict] = None):
        """Log a tool execution."""
        entry = AuditEntry(
            agent_id=agent_id,
            action=f"tool:{tool_name}",
            permission=None,
            scope=None,
            result=result,
            details={**args, **(details or {})},
        )
        self._add(entry)

    def log_approval(self, agent_id: str, action: str, approved: bool):
        """Log an approval decision."""
        entry = AuditEntry(
            agent_id=agent_id,
            action=f"approval:{action}",
            permission=None,
            scope=None,
            result="approved" if approved else "denied",
        )
        self._add(entry)

    def _add(self, entry: AuditEntry):
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

    def get_logs(self, limit: int = 200, agent_id: str = None) -> List[Dict]:
        entries = self._entries
        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        return [e.to_dict() for e in entries[-limit:]]

    def export_json(self, filepath: str):
        """Export full audit log to JSON file."""
        data = [e.to_dict() for e in self._entries]
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


audit_logger = AuditLogger()
