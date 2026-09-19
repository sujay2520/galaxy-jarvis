"""Galaxy CLI — Rich terminal interface for Galaxy (Jarvis)."""
import sys

# Force UTF-8 safe mode on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import asyncio
import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console(safe_box=True)
API_URL = "http://127.0.0.1:8000"


@click.group()
def cli():
    """[*] Galaxy (Jarvis) — Autonomous Multi-Agent OS."""
    pass


# ── Status ─────────────────────────────────────────────────────
@cli.command("status")
def status():
    """Check Galaxy system status and LLM health."""
    async def _status():
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(f"{API_URL}/api/status")
                r.raise_for_status()
                data = r.json()

                console.print(Panel(
                    f"[bold green]Galaxy Online[/bold green] (v{data.get('version', '0.1.0')})\n\n"
                    f"[cyan]Agents:[/cyan] {data['agents']['working']} working / {data['agents']['total']} total\n"
                    f"[cyan]Pending Approvals:[/cyan] {data['pending_approvals']}\n"
                    f"[cyan]Local LLM (Ollama):[/cyan] {data['llm']['local_ollama']}\n"
                    f"[cyan]Gemini API:[/cyan] {data['llm']['gemini_api']}\n"
                    f"[cyan]Groq API:[/cyan] {data['llm']['groq_api']}",
                    title="[*] Galaxy Status",
                    border_style="bright_blue",
                ))
            except Exception as e:
                console.print(f"[bold red]Cannot connect to Galaxy server:[/bold red] {e}")
                console.print("[yellow]Make sure the server is running: python run.py[/yellow]")
    asyncio.run(_status())


# ── Chat ───────────────────────────────────────────────────────
@cli.command("chat")
def chat():
    """Interactive chat with Galaxy (Jarvis)."""
    console.print(Panel.fit(
        "[bold cyan][*] Galaxy Interactive Terminal[/bold cyan]\n"
        "Chat with your AI assistant or issue autonomous tasks.\n"
        "Type [bold yellow]exit[/bold yellow] or [bold yellow]quit[/bold yellow] to end the session.",
        border_style="cyan"
    ))

    async def _chat_loop():
        async with httpx.AsyncClient(timeout=180.0) as client:
            while True:
                try:
                    user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
                    if not user_input:
                        continue
                    if user_input.lower() in ["exit", "quit", "q"]:
                        console.print("[dim]Exiting Galaxy chat session. Goodbye![/dim]")
                        break

                    with console.status("[bold blue]Galaxy is thinking...[/bold blue]"):
                        r = await client.post(f"{API_URL}/api/chat", json={"message": user_input})
                        data = r.json()

                    resp_text = data.get("response", "")
                    if data.get("is_task"):
                        console.print(Panel(resp_text, title="[*] Task Dispatched", border_style="green"))
                    else:
                        console.print(f"\n[bold magenta]Galaxy:[/bold magenta] {resp_text}")
                except (KeyboardInterrupt, EOFError):
                    break
                except Exception as e:
                    console.print(f"[red]Error:[/red] {e}")

    asyncio.run(_chat_loop())


# ── Tasks ──────────────────────────────────────────────────────
@cli.command("task")
@click.argument("description")
def task(description: str):
    """Dispatch an autonomous multi-agent task."""
    async def _run():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                r = await client.post(f"{API_URL}/api/tasks", json={"description": description})
                data = r.json()
                console.print(Panel(
                    f"[bold green]Task Started![/bold green]\n\n"
                    f"[cyan]Description:[/cyan] {description}\n"
                    f"[cyan]Status:[/cyan] {data.get('status', 'planning')}\n\n"
                    "Agents are decomposing and executing the task autonomously.\n"
                    "View progress in the Web UI: [link=http://localhost:8000]http://localhost:8000[/link]",
                    title="[*] Galaxy Task",
                    border_style="magenta"
                ))
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    asyncio.run(_run())


# ── Agents ─────────────────────────────────────────────────────
@cli.group("agents")
def agents():
    """Manage and inspect active agents."""
    pass


@agents.command("list")
def list_agents():
    """List all registered agents."""
    async def _list():
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(f"{API_URL}/api/agents")
                agent_list = r.json()
                table = Table(title="[*] Active Galaxy Agents", header_style="bold blue")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Name", style="magenta")
                table.add_column("Role", style="yellow")
                table.add_column("Status", style="green")
                table.add_column("Current Task", style="white")

                for a in agent_list:
                    status_style = "green" if a["status"] == "working" else "dim"
                    table.add_row(
                        a["id"][:8],
                        a["name"],
                        a["role"],
                        f"[{status_style}]{a['status']}[/{status_style}]",
                        a.get("current_task") or "Idle",
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    asyncio.run(_list())


# ── Approvals ──────────────────────────────────────────────────
@cli.group("approvals")
def approvals():
    """Manage action approvals."""
    pass


@approvals.command("list")
def list_approvals():
    """List pending authorization requests."""
    async def _list():
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(f"{API_URL}/api/approvals")
                data = r.json()
                if not data:
                    console.print("[dim]No actions awaiting approval.[/dim]")
                    return

                table = Table(title="[!] Pending Approvals", header_style="bold red")
                table.add_column("ID", style="cyan")
                table.add_column("Agent", style="magenta")
                table.add_column("Action", style="yellow")
                table.add_column("Risk", style="red")
                table.add_column("Status", style="green")

                for req_id, req in data.items():
                    table.add_row(req_id[:8], req["agent_id"][:8], req["action"], req["risk"], req["status"])
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    asyncio.run(_list())


@approvals.command("approve")
@click.argument("request_id")
def approve(request_id: str):
    """Approve a pending action."""
    async def _approve():
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(f"{API_URL}/api/approve/{request_id}", json={"approved": True})
                console.print(f"[green]Approved request {request_id}[/green]")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    asyncio.run(_approve())


@approvals.command("deny")
@click.argument("request_id")
def deny(request_id: str):
    """Deny a pending action."""
    async def _deny():
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(f"{API_URL}/api/approve/{request_id}", json={"approved": False})
                console.print(f"[yellow]Denied request {request_id}[/yellow]")
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    asyncio.run(_deny())


if __name__ == "__main__":
    cli()
