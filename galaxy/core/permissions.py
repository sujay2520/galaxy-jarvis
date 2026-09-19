from enum import Enum
from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, Field
import time
from datetime import datetime, timedelta
import fnmatch

class Permission(str, Enum):
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_DELETE = "file:delete"
    TERMINAL_EXECUTE = "terminal:execute"
    TERMINAL_INSTALL = "terminal:install"
    BROWSER_NAVIGATE = "browser:navigate"
    BROWSER_INTERACT = "browser:interact"
    NETWORK_HTTP = "network:http"
    NETWORK_DOWNLOAD = "network:download"
    PROCESS_SPAWN = "process:spawn"
    SYSTEM_ENV = "system:env"
    
    def scoped(self, scope: str) -> "PermissionGrant":
        return PermissionGrant(permission=self, scope=scope)

class PermissionGrant(BaseModel):
    permission: Permission
    scope: Optional[str] = None
    expires_at: Optional[float] = None
    
    def expires_in(self, minutes: int) -> "PermissionGrant":
        self.expires_at = time.time() + (minutes * 60)
        return self

    def is_valid(self) -> bool:
        if self.expires_at is None:
            return True
        return time.time() <= self.expires_at

    def matches(self, target_permission: Permission, target_scope: Optional[str] = None) -> bool:
        if self.permission != target_permission:
            return False
        if not self.is_valid():
            return False
        if self.scope is None:
            return True # Unscoped grant covers all scopes
        if target_scope is None:
            return True # If target doesn't require a scope, a scoped grant still matches the permission
        # Wilcard matching for scopes
        return fnmatch.fnmatch(target_scope, self.scope)

class PermissionSet(BaseModel):
    grants: List[PermissionGrant] = Field(default_factory=list)

    def has_permission(self, permission: Permission, scope: Optional[str] = None) -> bool:
        return any(grant.matches(permission, scope) for grant in self.grants)
    
    def add_grant(self, grant: PermissionGrant):
        self.grants.append(grant)
        
    def revoke_permission(self, permission: Permission):
        self.grants = [g for g in self.grants if g.permission != permission]

class PermissionEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PermissionEngine, cls).__new__(cls)
            cls._instance.agent_permissions = {} # agent_id -> PermissionSet
        return cls._instance
    
    def register_agent(self, agent_id: str, permissions: PermissionSet):
        self.agent_permissions[agent_id] = permissions
        
    def check(self, agent_id: str, permission: Permission, scope: Optional[str] = None) -> bool:
        from galaxy.security.audit import audit_logger
        pset = self.agent_permissions.get(agent_id)
        if not pset:
            audit_logger.log_check(agent_id, permission, scope, False)
            return False
        result = pset.has_permission(permission, scope)
        audit_logger.log_check(agent_id, permission, scope, result)
        return result
        
    def grant(self, agent_id: str, grant: PermissionGrant):
        if agent_id not in self.agent_permissions:
            self.agent_permissions[agent_id] = PermissionSet()
        self.agent_permissions[agent_id].add_grant(grant)
        
    def revoke(self, agent_id: str, permission: Permission):
        if agent_id in self.agent_permissions:
            self.agent_permissions[agent_id].revoke_permission(permission)

permission_engine = PermissionEngine()
