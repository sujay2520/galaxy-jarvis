"""Network tools — permission-gated HTTP operations."""
import os
import httpx
from typing import Optional, Any
from .base import BaseTool
from galaxy.core.permissions import Permission
from galaxy.security.approval import RiskTier


class HttpGetTool(BaseTool):
    name = "http_get"
    description = "Make an HTTP GET request. Args: url (str), headers (dict, optional)"
    risk_level = RiskTier.LOW
    required_permission = Permission.NETWORK_HTTP

    def get_scope(self, url: str = "", **kwargs) -> Optional[str]:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return url

    async def _execute(self, agent_id: str, url: str, headers: dict = None, **kwargs) -> Any:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(url, headers=headers or {})
                content = resp.text
                # Truncate large responses
                if len(content) > 20000:
                    content = content[:20000] + f"\n... (truncated, {len(content)} total chars)"
                return {
                    "status_code": resp.status_code,
                    "content": content,
                    "headers": dict(resp.headers),
                    "url": str(resp.url),
                }
        except Exception as e:
            return {"error": str(e), "url": url}


class HttpPostTool(BaseTool):
    name = "http_post"
    description = "Make an HTTP POST request. Args: url (str), data (dict), headers (dict, optional)"
    risk_level = RiskTier.MEDIUM
    required_permission = Permission.NETWORK_HTTP

    def get_scope(self, url: str = "", **kwargs) -> Optional[str]:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return url

    async def _execute(self, agent_id: str, url: str, data: dict = None, headers: dict = None, **kwargs) -> Any:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                resp = await client.post(url, json=data or {}, headers=headers or {})
                content = resp.text
                if len(content) > 20000:
                    content = content[:20000] + f"\n... (truncated)"
                return {
                    "status_code": resp.status_code,
                    "content": content,
                    "url": str(resp.url),
                }
        except Exception as e:
            return {"error": str(e), "url": url}


class DownloadFileTool(BaseTool):
    name = "download_file"
    description = "Download a file from a URL to disk. Args: url (str), save_path (str)"
    risk_level = RiskTier.MEDIUM
    required_permission = Permission.NETWORK_DOWNLOAD

    def get_scope(self, url: str = "", **kwargs) -> Optional[str]:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return url

    async def _execute(self, agent_id: str, url: str, save_path: str, **kwargs) -> Any:
        abs_path = os.path.abspath(save_path)
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            async with httpx.AsyncClient(follow_redirects=True, timeout=120.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                with open(abs_path, "wb") as f:
                    f.write(resp.content)
                return {
                    "success": True,
                    "path": abs_path,
                    "size_bytes": len(resp.content),
                    "url": url,
                }
        except Exception as e:
            return {"error": str(e), "url": url}
