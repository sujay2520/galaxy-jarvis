# Galaxy (Jarvis) — Autonomous AI Agent OS

**Galaxy** is a free, cross-platform, permission-based AI agent system that runs on your PC, laptop, or phone. It auto-detects your hardware and picks the best LLM — local or cloud — so you get the smartest AI assistant possible, for free.

![Galaxy Screenshot](docs/screenshot.png)

## What Makes Galaxy Different

- **Auto-Detection**: Scans your CPU, RAM, GPU and recommends the best AI model
- **Works Everywhere**: Windows, Linux, phones (via web browser on same Wi-Fi)
- **Permission System**: Playwright-style scoped permissions — agents only access what you allow
- **Multi-Agent**: Breaks complex tasks into subtasks, assigns specialized agents (Coder, Tester, Researcher, DevOps, Reviewer)
- **Free Forever**: Uses local models (Ollama) or free cloud APIs (Gemini Flash, Groq)
- **Your Keys**: Optionally paste your own API keys for any provider
- **Voice + Text**: Chat via typing or voice input (Web Speech API)
- **Secure**: Human-in-the-loop approval for high-risk actions, full audit logging

## Quick Start

### Windows
```bash
# Clone
git clone https://github.com/sujay2520/galaxy-jarvis.git
cd galaxy-jarvis

# Install Python dependencies
pip install -e .

# Start Galaxy (auto-detects your system)
python run.py
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

### From Phone
Connect to `http://<YOUR_PC_IP>:8000` from your phone browser (same Wi-Fi network).

### Linux
```bash
git clone https://github.com/sujay2520/galaxy-jarvis.git
cd galaxy-jarvis
pip install -e .
python run.py
```

## How It Works

```
You (PC/Phone/Laptop)
  |
  v
[Galaxy Web UI] <---> [FastAPI Server]
                           |
                      [LLM Router]
                      /     |     \
               [Ollama]  [Gemini]  [Groq]
               (local)   (free)    (free)
                           |
                     [Orchestrator]
                      /    |    \
                [Coder] [Tester] [DevOps]
                  |        |        |
              [Permission Engine]
              [Approval System]
              [Audit Logger]
```

### Smart LLM Selection

| Your Hardware | What Galaxy Does |
|:---|:---|
| 16GB+ RAM + NVIDIA GPU | Installs Mistral 7B locally (best quality, private) |
| 8-16GB RAM | Installs Qwen 2.5 3B locally (fast, good enough) |
| < 8GB RAM / No GPU | Uses free cloud APIs (Gemini Flash + Groq) |
| You have your own API key | Uses your preferred provider |

## Features

### Permission Engine (Playwright-Style)
```python
# Agents get scoped, time-limited permissions
Permission.FILE_WRITE.scoped("/project/src")  # Only write to /project/src
grant.expires_in(minutes=30)                   # Auto-revoke after 30 min
```

### Multi-Agent Orchestration
Give Galaxy a complex task and it breaks it into subtasks:
```
"Build a web scraper and test it"
  -> CoderAgent: Create scraper.py
  -> TesterAgent: Write unit tests  
  -> TesterAgent: Run tests
```

### Security
- **Risk Tiers**: LOW (auto-approve), MEDIUM (auto-approve + log), HIGH (require human approval), CRITICAL (always block)
- **Command Blocklist**: Dangerous commands (rm -rf, format, shutdown) are blocked
- **Path Scoping**: Agents can only access directories you allow
- **Full Audit Trail**: Every action logged with timestamp

## CLI

```bash
python -m galaxy.cli.main status          # System health check
python -m galaxy.cli.main chat            # Interactive terminal chat
python -m galaxy.cli.main task "build X"  # Dispatch agent task
python -m galaxy.cli.main agents list     # Show active agents
python -m galaxy.cli.main approvals list  # Pending approvals
```

## Configuration

Edit `.env` or use the Settings page in the Web UI:

```env
# Local LLM (auto-detected)
OLLAMA_HOST=http://localhost:11434
DEFAULT_LOCAL_MODEL=mistral

# Free Cloud APIs (optional)
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here

# Server
HOST=0.0.0.0
PORT=8000
```

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic, asyncio
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Local LLM**: Ollama (Mistral 7B, Qwen 2.5 3B)
- **Cloud LLM**: Google Gemini (free), Groq (free), Mistral AI
- **Security**: Custom permission engine, approval system, audit logger

## Project Structure

```
galaxy/
  core/           # Permission engine, agent loop, orchestrator, events
  llm/            # LLM router, local Ollama, cloud API providers
  tools/          # File, terminal, browser, network tools
  agents/         # Coder, tester, researcher, devops, reviewer
  security/       # Approval system, sandbox, audit logger
  api/            # FastAPI server, REST + WebSocket endpoints
  cli/            # Rich terminal CLI
  config/         # Settings, system detection, profiles
web/              # React frontend (Vite + TypeScript)
run.py            # Entry point
start_galaxy.bat  # Windows one-click launcher
```

## License

MIT License — free for personal and commercial use.

## Author

Built by [@sujay2520](https://github.com/sujay2520)
