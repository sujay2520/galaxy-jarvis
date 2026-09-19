"""Galaxy Settings — Global configuration loaded from environment."""
import os
import socket
from pydantic_settings import BaseSettings
from pydantic import Field


def get_local_ip() -> str:
    """Detect LAN IP address for phone/laptop connectivity."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class Settings(BaseSettings):
    """Galaxy configuration. Loaded from .env file and environment variables."""

    # -- Application --
    APP_NAME: str = "Galaxy"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # -- Server (0.0.0.0 allows phones & laptops on same Wi-Fi/LAN to connect) --
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOCAL_IP: str = Field(default_factory=get_local_ip)

    # -- Local LLM (Ollama) --
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_LOCAL_MODEL: str = "qwen2.5:3b"
    MISTRAL_LOCAL_MODEL: str = "mistral:7b"
    PREFERRED_PROVIDER: str = "auto"  # "auto", "local", "groq", "gemini", "mistral"
    PREFERRED_MODEL: str = "mistral"   # "mistral", "qwen2.5:3b", "llama-3.1-8b", etc.

    # -- API LLMs (Free Tier / Cloud APIs) --
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_MISTRAL_MODEL: str = "mixtral-8x7b-32768"

    MISTRAL_API_KEY: str = ""
    MISTRAL_API_MODEL: str = "mistral-small-latest"

    # -- Security --
    APPROVAL_TIMEOUT_MINUTES: int = 5
    MAX_COMMAND_TIMEOUT: int = 120
    BLOCKED_PATHS: list = Field(default_factory=lambda: [
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/.aws"),
        os.path.expanduser("~/.gnupg"),
    ])

    # -- Working Directory --
    DEFAULT_WORKSPACE: str = Field(default_factory=lambda: os.getcwd())

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
