"""Galaxy API Server — FastAPI backend with REST + WebSocket."""
import asyncio
import json
import os
from typing import List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from galaxy.api.models import (
    TaskRequest, TaskResponse, AgentResponse,
    PermissionRequest, ChatRequest, ChatResponse, ApproveRequest,
)
from galaxy.core.orchestrator import orchestrator
from galaxy.core.registry import agent_registry
from galaxy.core.permissions import permission_engine, Permission, PermissionGrant
from galaxy.core.events import event_bus, Event, EventType
from galaxy.security.audit import audit_logger
from galaxy.security.approval import approval_system
from galaxy.llm.router import llm_router
from galaxy.config.system_detect import detect_system
from galaxy.config.settings import settings

# Import agents to trigger registration
import galaxy.agents.coder
import galaxy.agents.tester
import galaxy.agents.researcher
import galaxy.agents.devops
import galaxy.agents.reviewer


# ── WebSocket connection manager ────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        """Send JSON message to all connected WebSocket clients."""
        data = json.dumps(message, default=str)
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_text(data)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


ws_manager = ConnectionManager()


# ── Event handlers — bridge events to WebSocket ────────────────
async def _on_agent_event(event: Event):
    await ws_manager.broadcast({
        "type": event.type.value,
        "payload": event.payload,
        "source": event.source,
    })


async def _on_approval_event(event: Event):
    await ws_manager.broadcast({
        "type": "ApprovalRequired",
        "payload": event.payload,
        "source": event.source,
    })


# ── App lifecycle ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Subscribe to events for WebSocket broadcasting
    for etype in EventType:
        event_bus.subscribe(etype, _on_agent_event)
    print("\n[*] Galaxy API Server started")
    print(f"   REST API:  http://localhost:{os.environ.get('PORT', 8000)}/api")
    print(f"   WebSocket: ws://localhost:{os.environ.get('PORT', 8000)}/ws")
    print(f"   Web UI:    http://localhost:{os.environ.get('PORT', 8000)}\n")
    yield
    print("\n[*] Galaxy API Server shutting down")


app = FastAPI(
    title="Galaxy API",
    version="0.1.0",
    description="Permission-based multi-agent autonomous system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Task Endpoints ─────────────────────────────────────────────
@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(req: TaskRequest):
    """Create and start a new task."""
    task_coro = orchestrator.process_task(req.description, req.working_dir or ".")
    asyncio.create_task(task_coro)
    return TaskResponse(
        message="Task started",
        task_id="pending",
        status="planning",
    )


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    return orchestrator.list_tasks()


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details."""
    task = orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


# ── Agent Endpoints ────────────────────────────────────────────
@app.get("/api/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all active agents."""
    agents = agent_registry.list_agents()
    return [
        AgentResponse(
            id=a.id,
            name=a.name,
            role=a.role,
            status=a.status,
            current_task=a.current_task,
        )
        for a in agents.values()
    ]


@app.get("/api/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent details."""
    a = agent_registry.get_agent(agent_id)
    if not a:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(
        id=a.id,
        name=a.name,
        role=a.role,
        status=a.status,
        current_task=a.current_task,
    )


# ── Permission Endpoints ──────────────────────────────────────
@app.post("/api/agents/{agent_id}/permissions")
async def grant_permission(agent_id: str, req: PermissionRequest):
    """Grant a permission to an agent."""
    try:
        perm = Permission(req.permission)
        grant = PermissionGrant(permission=perm, scope=req.scope)
        if req.expires_in_minutes:
            grant.expires_in(req.expires_in_minutes)
        permission_engine.grant(agent_id, grant)
        await ws_manager.broadcast({
            "type": "PermissionGranted",
            "payload": {"agent_id": agent_id, "permission": req.permission, "scope": req.scope},
        })
        return {"status": "granted", "permission": req.permission}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid permission: {req.permission}")


@app.delete("/api/agents/{agent_id}/permissions/{permission}")
async def revoke_permission(agent_id: str, permission: str):
    """Revoke a permission from an agent."""
    try:
        perm = Permission(permission)
        permission_engine.revoke(agent_id, perm)
        await ws_manager.broadcast({
            "type": "PermissionDenied",
            "payload": {"agent_id": agent_id, "permission": permission},
        })
        return {"status": "revoked", "permission": permission}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid permission: {permission}")


# ── Approval Endpoints ────────────────────────────────────────
@app.get("/api/approvals")
async def list_approvals():
    """List pending approval requests."""
    return {
        req_id: {
            "id": req.id,
            "agent_id": req.agent_id,
            "action": req.action,
            "risk": req.risk.value,
            "details": req.details,
            "status": req.status,
            "created_at": req.created_at,
        }
        for req_id, req in approval_system.requests.items()
    }


@app.post("/api/approve/{request_id}")
async def approve_request(request_id: str, req: ApproveRequest):
    """Approve or deny a pending request."""
    approval_system.resolve(request_id, req.approved)
    await ws_manager.broadcast({
        "type": "ApprovalGranted" if req.approved else "ApprovalDenied",
        "payload": {"request_id": request_id, "approved": req.approved},
    })
    return {"status": "approved" if req.approved else "denied"}


# ── Chat Endpoint ─────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a chat message and get a response.
    
    Simple messages get a direct LLM response.
    Task-like messages get routed to the orchestrator.
    """
    message = req.message.strip()

    # Check if this looks like a task (starts with action verbs)
    task_indicators = ["build", "create", "make", "write", "fix", "deploy", "install",
                       "setup", "test", "run", "delete", "update", "implement"]
    is_task = any(message.lower().startswith(word) for word in task_indicators)

    if is_task:
        # Route to orchestrator
        asyncio.create_task(orchestrator.process_task(message))
        return ChatResponse(
            response=f"[>] Starting task: {message}\n\nI've dispatched agents to work on this. Check the Agents dashboard for progress.",
            is_task=True,
        )
    else:
        # Direct chat with LLM
        try:
            messages = [
                {"role": "system", "content": "You are Galaxy (Jarvis), a helpful AI assistant. Be concise and friendly."},
                {"role": "user", "content": message},
            ]
            response = await llm_router.generate(messages, complexity="simple")
            return ChatResponse(response=response, is_task=False)
        except Exception as e:
            return ChatResponse(
                response=f"[!] LLM unavailable: {e}\n\nMake sure Ollama is running or API keys are configured in .env",
                is_task=False,
            )


# ── Audit Endpoint ─────────────────────────────────────────────
@app.get("/api/audit")
async def get_audit_log(limit: int = 200, agent_id: str = None):
    """Get audit log entries."""
    return audit_logger.get_logs(limit=limit, agent_id=agent_id)


# ── System Info ────────────────────────────────────────────────
@app.get("/api/status")
async def system_status():
    """Get system status including LLM health."""
    local_healthy = await llm_router.local.is_healthy()
    gemini_healthy = await llm_router.gemini.is_healthy()
    groq_healthy = await llm_router.groq.is_healthy()

    agents = agent_registry.list_agents()
    return {
        "status": "online",
        "version": "0.1.0",
        "agents": {
            "total": len(agents),
            "working": sum(1 for a in agents.values() if a.status == "working"),
        },
        "llm": {
            "local_ollama": "healthy" if local_healthy else "offline",
            "gemini_api": "healthy" if gemini_healthy else "no_key",
            "groq_api": "healthy" if groq_healthy else "no_key",
        },
        "pending_approvals": sum(
            1 for r in approval_system.requests.values() if r.status == "pending"
        ),
    }


@app.get("/api/system-info")
async def get_system_info():
    """Get detected system specs."""
    specs = await detect_system()
    return specs


@app.get("/api/settings")
async def get_settings():
    """Get current configuration."""
    return settings.model_dump()


@app.post("/api/settings")
async def update_settings(new_settings: dict):
    """Update settings and save to .env"""
    # Assuming update settings updates the model and writes to .env
    for key, value in new_settings.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    # Simple write to .env (not exhaustive, for simplicity assuming valid keys)
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"), "w") as f:
        for k, v in settings.model_dump().items():
            f.write(f"{k}={v}\n")
    return {"status": "success", "settings": settings.model_dump()}


# ── WebSocket ──────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket connection for live updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Handle incoming WebSocket messages (e.g., chat from UI)
                if msg.get("type") == "chat":
                    message = msg.get("message", "")
                    messages = [
                        {"role": "system", "content": "You are Galaxy (Jarvis), a helpful AI assistant."},
                        {"role": "user", "content": message},
                    ]
                    try:
                        response = await llm_router.generate(messages, complexity="simple")
                    except Exception:
                        response = "[!] LLM unavailable. Check your configuration."

                    await websocket.send_text(json.dumps({
                        "type": "ChatResponse",
                        "payload": {"message": response},
                    }))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ── Serve Web UI static files ──────────────────────────────────
web_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web", "dist")
if os.path.isdir(web_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(web_dist, "assets")), name="assets")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve the React SPA for all non-API routes."""
        file_path = os.path.join(web_dist, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(web_dist, "index.html"))
