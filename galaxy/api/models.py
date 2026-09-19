"""Galaxy API — Pydantic request/response models."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class TaskRequest(BaseModel):
    description: str
    working_dir: Optional[str] = None


class TaskResponse(BaseModel):
    message: str
    task_id: str
    status: str


class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    status: str
    current_task: Optional[str] = None


class PermissionRequest(BaseModel):
    permission: str  # e.g., "file:read"
    scope: Optional[str] = None
    expires_in_minutes: Optional[int] = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    is_task: bool = False


class ApproveRequest(BaseModel):
    approved: bool
