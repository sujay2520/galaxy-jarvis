# Galaxy (Jarvis)

**Free, cross-platform AI agent OS** that auto-detects your hardware, picks the best LLM, and runs autonomous agents with Playwright-style permissions.

Works on **Windows, Linux, and phones** (via PWA).

---

## Quick Start

### Windows
```
git clone https://github.com/sujay2520/galaxy-jarvis.git
cd galaxy-jarvis
pip install -r requirements.txt
start_galaxy.bat
```

### Linux
```bash
git clone https://github.com/sujay2520/galaxy-jarvis.git
cd galaxy-jarvis
pip install -r requirements.txt
chmod +x start_galaxy.sh
./start_galaxy.sh
```

### Phone (iOS / Android)
1. Start Galaxy on your PC (using Windows or Linux instructions above)
2. Open your phone browser, go to `http://YOUR-PC-IP:8000`
3. Tap "Add to Home Screen" (or "Install App" on Android Chrome)
4. Galaxy works as a full-screen app on your phone

### Desktop App (Electron)
```bash
cd desktop
npm install
npm start
```
Build installers:
```bash
npm run build:win    # Windows .exe installer
npm run build:linux  # Linux AppImage
```

---

## Features

### Smart LLM Selection
Galaxy auto-detects your PC specs and picks the best LLM:
| Hardware | Model | Where |
|:---|:---|:---|
| 16GB+ RAM + GPU 6GB+ | Mistral 7B | Runs locally via Ollama |
| 8-16GB RAM | Qwen 2.5 3B | Runs locally via Ollama |
| Low-end / Phone | Gemini Flash or Groq | Free cloud API |

You can also paste your own API key for any provider in Settings.

### Autonomous Agents
5 specialized agents that decompose tasks and work together:
- **Coder** -- writes and modifies code
- **Tester** -- reviews and tests code
- **Researcher** -- searches the web and docs
- **DevOps** -- handles deployment and infrastructure
- **Reviewer** -- code review and quality checks

### Playwright-Style Permissions
Every tool (file read/write, terminal, network) requires a permission grant:
- **LOW risk** (file read, web search): auto-approved
- **MEDIUM risk** (file write, HTTP requests): auto-approved
- **HIGH risk** (shell commands): queued for human approval
- **CRITICAL** (system changes): always blocked

### Security
- Sandboxed command execution with timeout and blocklist
- Full audit trail of every agent action
- Approval queue for high-risk operations

### Cross-Platform
- **Desktop**: Electron app with system tray (Windows + Linux)
- **Web**: Full-featured UI at http://localhost:8000
- **Mobile**: PWA -- install from browser, works offline
- **CLI**: `python -m galaxy.cli.main chat`

### Light / Dark Theme
Toggle between light and dark themes -- saved to your preferences.

---

## Architecture

```
galaxy-jarvis/
  galaxy/              # Python backend
    core/              # Agent engine, orchestrator, permissions, events
    llm/               # LLM router (Ollama, Gemini, Groq, Mistral)
    tools/             # File, terminal, network, browser tools
    security/          # Approval system, audit logging, sandbox
    api/               # FastAPI server
    cli/               # Rich terminal CLI
    config/            # Settings, system detection
  web/                 # React + TypeScript frontend
    src/components/    # UI components (ChatView, Agents, etc.)
    src/context/       # Theme context
    dist/              # Built static files
  desktop/             # Electron desktop wrapper
  run.py               # Main entry point
  start_galaxy.bat     # Windows launcher
  start_galaxy.sh      # Linux launcher
```

---

## API

| Endpoint | Method | Description |
|:---|:---|:---|
| `/api/status` | GET | System health check |
| `/api/chat` | POST | Chat with AI (auto-routes tasks to agents) |
| `/api/tasks` | POST | Create a multi-agent task |
| `/api/agents` | GET | List active agents |
| `/api/audit` | GET | View audit log |
| `/api/approvals` | GET | Pending approval requests |
| `/api/system-info` | GET | Hardware specs + LLM recommendation |
| `/api/settings` | GET/POST | Runtime configuration |
| `/ws` | WebSocket | Real-time agent events |

Full interactive docs at http://localhost:8000/docs

---

## Requirements

- Python 3.10+
- Node.js 18+ (for Electron desktop app, optional)
- Ollama (for local LLMs, optional -- cloud APIs work without it)

## License

MIT
