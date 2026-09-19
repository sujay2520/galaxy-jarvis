from enum import Enum
from typing import List, Dict, Any

class PermissionProfile(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    DEVELOPER = "developer"
    FULL_ACCESS = "full_access"

# Will map to actual permissions in core.permissions
PROFILES: Dict[PermissionProfile, List[str]] = {
    PermissionProfile.MINIMAL: [
        "file:read"
    ],
    PermissionProfile.STANDARD: [
        "file:read",
        "file:write",
        "terminal:execute"
    ],
    PermissionProfile.DEVELOPER: [
        "file:read",
        "file:write",
        "terminal:execute",
        "network:http",
        "network:download"
    ],
    PermissionProfile.FULL_ACCESS: [
        "file:read",
        "file:write",
        "file:delete",
        "terminal:execute",
        "terminal:install",
        "browser:navigate",
        "browser:interact",
        "network:http",
        "network:download",
        "process:spawn",
        "system:env"
    ]
}
