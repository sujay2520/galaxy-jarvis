from enum import Enum
import asyncio
from typing import Callable, Dict, List, Any
from pydantic import BaseModel

class EventType(str, Enum):
    AgentStarted = "AgentStarted"
    AgentCompleted = "AgentCompleted"
    AgentError = "AgentError"
    PermissionRequested = "PermissionRequested"
    PermissionGranted = "PermissionGranted"
    PermissionDenied = "PermissionDenied"
    TaskAssigned = "TaskAssigned"
    TaskCompleted = "TaskCompleted"
    ApprovalRequired = "ApprovalRequired"
    ApprovalGranted = "ApprovalGranted"

class Event(BaseModel):
    type: EventType
    payload: Dict[str, Any]
    source: str

class EventBus:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.subscribers = {t: [] for t in EventType}
        return cls._instance
        
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        self.subscribers[event_type].append(callback)
        
    async def publish(self, event: Event):
        # We run callbacks asynchronously
        cbs = self.subscribers[event.type]
        for cb in cbs:
            if asyncio.iscoroutinefunction(cb):
                asyncio.create_task(cb(event))
            else:
                cb(event)

event_bus = EventBus()
