#!/bin/bash
set -e

echo ""
echo "  ================================================================"
echo "       [*]  G A L A X Y   (J A R V I S)   S Y S T E M"
echo "       Permission-Based Autonomous Multi-Agent OS"
echo "  ================================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "  [ERROR] Python3 not found. Install: sudo apt install python3 python3-pip"
    exit 1
fi

# Start Ollama if available and not running
if command -v ollama &> /dev/null; then
    if ! pgrep -x "ollama" > /dev/null; then
        echo "  [1/3] Starting Ollama..."
        ollama serve &
        sleep 3
    else
        echo "  [1/3] Ollama already running."
    fi
else
    echo "  [1/3] Ollama not found. Cloud LLMs only."
fi

# Start Galaxy server
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo "  [2/3] Galaxy server already running."
else
    echo "  [2/3] Starting Galaxy server..."
    python3 run.py &
    SERVER_PID=$!
    
    echo "  [3/3] Waiting for server..."
    for i in $(seq 1 30); do
        if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
fi

echo ""
echo "  ================================================================"
echo "       [OK] Galaxy is ready!"
echo "  ================================================================"
echo ""

# Get LAN IP
LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "YOUR-IP")

echo "  Web UI:    http://localhost:8000"
echo "  Phone:     http://${LAN_IP}:8000 (same Wi-Fi)"
echo "  API Docs:  http://localhost:8000/docs"
echo ""

# Try Electron, fall back to browser
if [ -d "$SCRIPT_DIR/desktop/node_modules" ]; then
    echo "  [*] Launching desktop app..."
    cd "$SCRIPT_DIR/desktop" && npx electron . &
else
    echo "  [*] Opening in browser..."
    xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000 2>/dev/null || echo "  Open http://localhost:8000 in your browser"
fi

echo ""
echo "  Press Ctrl+C to stop."
wait
