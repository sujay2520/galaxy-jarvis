"""Galaxy Security — Sandbox for isolated command execution."""
import asyncio
import os
from typing import Tuple


class Sandbox:
    """Lightweight process-level sandbox for command execution.
    
    Restricts working directory, filters environment variables,
    and enforces timeouts. Future: Docker container support.
    """

    # Environment variables that should NOT be passed to sandboxed processes
    FILTERED_ENV_VARS = {
        "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GITHUB_TOKEN", "GH_TOKEN",
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
        "DATABASE_URL", "DB_PASSWORD",
    }

    def __init__(self, working_dir: str = "."):
        self.working_dir = os.path.abspath(working_dir)

    def _safe_env(self) -> dict:
        """Create a filtered copy of environment variables."""
        env = {}
        for key, value in os.environ.items():
            if key not in self.FILTERED_ENV_VARS:
                env[key] = value
        env["PYTHONIOENCODING"] = "utf-8"
        return env

    async def execute(self, cmd: str, timeout: int = 120) -> Tuple[int, str, str]:
        """Execute a command in the sandbox with timeout."""
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_dir,
            env=self._safe_env(),
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            stdout = stdout_bytes.decode("utf-8", errors="replace")
            stderr = stderr_bytes.decode("utf-8", errors="replace")
            return (proc.returncode or 0, stdout, stderr)
        except asyncio.TimeoutError:
            proc.kill()
            return (-1, "", f"Command timed out after {timeout}s")
