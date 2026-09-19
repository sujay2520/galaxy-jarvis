"""Terminal tools — permission-gated shell command execution."""
import asyncio
import os
import re
from typing import Optional, Any, List
from .base import BaseTool
from galaxy.core.permissions import Permission
from galaxy.security.approval import RiskTier


# Commands that are always blocked for safety
BLOCKED_COMMANDS = [
    r"\brm\s+(-rf?|--recursive)\s+/\s*$",  # rm -rf /
    r"\bformat\b.*\b[a-zA-Z]:\b",           # format C:
    r"\bshutdown\b",
    r"\brestart\b.*(/r|--reboot)",
    r"\bmkfs\b",
    r"\bdd\b.*\bof=/dev/",
    r"\b(del|rmdir)\s+/s\s+/q\s+[A-Z]:\\",  # Windows: del /s /q C:\
]


def is_command_blocked(cmd: str) -> bool:
    """Check if a command matches any blocked patterns."""
    for pattern in BLOCKED_COMMANDS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return True
    return False


class TerminalExecuteTool(BaseTool):
    name = "execute_command"
    description = "Execute a shell command. Args: cmd (str), cwd (str, optional — working directory)"
    risk_level = RiskTier.HIGH
    required_permission = Permission.TERMINAL_EXECUTE

    def get_scope(self, cwd: str = ".", **kwargs) -> Optional[str]:
        return os.path.abspath(cwd)

    async def _execute(self, agent_id: str, cmd: str, cwd: str = ".", timeout: int = 120, **kwargs) -> Any:
        if is_command_blocked(cmd):
            return {"error": f"Command blocked by safety policy: {cmd}"}

        abs_cwd = os.path.abspath(cwd)
        if not os.path.isdir(abs_cwd):
            return {"error": f"Working directory not found: {cwd}"}

        try:
            # Determine shell based on OS
            if os.name == "nt":
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=abs_cwd,
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
            else:
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=abs_cwd,
                )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return {"error": f"Command timed out after {timeout}s", "cmd": cmd}

            stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
            stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

            # Truncate very long output
            max_len = 10000
            if len(stdout) > max_len:
                stdout = stdout[:max_len] + f"\n... (truncated, {len(stdout)} total chars)"
            if len(stderr) > max_len:
                stderr = stderr[:max_len] + f"\n... (truncated, {len(stderr)} total chars)"

            return {
                "exit_code": proc.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "cmd": cmd,
            }
        except Exception as e:
            return {"error": str(e), "cmd": cmd}


class InstallPackageTool(BaseTool):
    name = "install_package"
    description = "Install a package using pip or npm. Args: package (str), manager (str, default 'pip')"
    risk_level = RiskTier.HIGH
    required_permission = Permission.TERMINAL_INSTALL

    def get_scope(self, **kwargs) -> Optional[str]:
        return "global"

    async def _execute(self, agent_id: str, package: str, manager: str = "pip", cwd: str = ".", **kwargs) -> Any:
        # Sanitize package name
        if not re.match(r"^[a-zA-Z0-9_\-\.>=<\[\],\s]+$", package):
            return {"error": f"Invalid package name: {package}"}

        if manager == "pip":
            cmd = f"pip install {package}"
        elif manager == "npm":
            cmd = f"npm install {package}"
        else:
            return {"error": f"Unsupported package manager: {manager}"}

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.abspath(cwd),
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=300
            )

            stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
            stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

            return {
                "exit_code": proc.returncode,
                "stdout": stdout[-2000:] if len(stdout) > 2000 else stdout,
                "stderr": stderr[-2000:] if len(stderr) > 2000 else stderr,
                "package": package,
                "manager": manager,
            }
        except asyncio.TimeoutError:
            return {"error": f"Package install timed out: {package}"}
        except Exception as e:
            return {"error": str(e)}
