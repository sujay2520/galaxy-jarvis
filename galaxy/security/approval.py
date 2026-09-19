from enum import Enum
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio
import time
import uuid
from galaxy.config.settings import settings


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalRequest(BaseModel):
    id: str
    agent_id: str
    action: str
    details: Dict[str, str]
    risk: RiskTier
    created_at: float
    status: str = "pending"  # pending, approved, denied


class ApprovalSystem:
    def __init__(self):
        self.requests: Dict[str, ApprovalRequest] = {}
        self._waiters: Dict[str, asyncio.Event] = {}

    async def request_approval(
        self, agent_id: str, action: str, details: Dict, risk: RiskTier
    ) -> bool:
        # LOW and MEDIUM risk: auto-approve (normal file ops, shell commands, http)
        if risk in (RiskTier.LOW, RiskTier.MEDIUM):
            return True

        # CRITICAL: always block
        if risk == RiskTier.CRITICAL:
            return False

        # HIGH: queue for human review (or timeout to auto-deny)
        req_id = f"req_{uuid.uuid4().hex[:8]}"
        req = ApprovalRequest(
            id=req_id,
            agent_id=agent_id,
            action=action,
            details={k: str(v) for k, v in details.items()},
            risk=risk,
            created_at=time.time(),
        )
        self.requests[req_id] = req
        event = asyncio.Event()
        self._waiters[req_id] = event

        # Notify via event bus so the WebSocket broadcasts to UI
        try:
            from galaxy.core.events import event_bus, Event, EventType
            await event_bus.publish(Event(
                type=EventType.ApprovalRequired,
                payload={"request_id": req_id, "action": action, "risk": risk.value, "agent_id": agent_id},
                source="approval_system",
            ))
        except Exception:
            pass

        try:
            timeout = settings.APPROVAL_TIMEOUT_MINUTES * 60
            await asyncio.wait_for(event.wait(), timeout=timeout)
            return self.requests[req_id].status == "approved"
        except asyncio.TimeoutError:
            self.requests[req_id].status = "denied"
            return False

    def resolve(self, req_id: str, approved: bool):
        if req_id in self.requests and self.requests[req_id].status == "pending":
            self.requests[req_id].status = "approved" if approved else "denied"
            if req_id in self._waiters:
                self._waiters[req_id].set()


approval_system = ApprovalSystem()
