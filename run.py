"""Galaxy — Main Application Runner.

Starts the Galaxy server (FastAPI + WebSockets + Web UI).
Accessible from:
  - Local PC:   http://localhost:8000
  - Phone/LAN:  http://<YOUR_LOCAL_IP>:8000
"""
import sys
import os

# Enable UTF-8 for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from galaxy.config.settings import settings
import galaxy.agents  # Ensure all agents are registered

def print_banner():
    local_ip = settings.LOCAL_IP
    port = settings.PORT
    
    print("\n" + "="*65)
    print("      [*]  G A L A X Y   (J A R V I S)   S Y S T E M")
    print("      Permission-Based Autonomous Multi-Agent OS")
    print("="*65)
    print(f"  [PC] Local Desktop:        http://localhost:{port}")
    print(f"  [Mobile] Phone, Laptop:    http://{local_ip}:{port}")
    print(f"  [API] REST Documentation:  http://localhost:{port}/docs")
    print(f"  [WS] Live WebSocket:       ws://localhost:{port}/ws")
    print("="*65)
    print(f"  [Model] Local: {settings.DEFAULT_LOCAL_MODEL} / {settings.MISTRAL_LOCAL_MODEL}")
    print(f"  [Provider] Active: {settings.PREFERRED_PROVIDER}")
    print("="*65 + "\n")

if __name__ == "__main__":
    print_banner()
    uvicorn.run(
        "galaxy.api.server:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False
    )
