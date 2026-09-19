"""File system tools — permission-gated file operations."""
import os
import glob
import shutil
import aiofiles
from typing import Optional, Any, List
from .base import BaseTool
from galaxy.core.permissions import Permission
from galaxy.security.approval import RiskTier


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file. Args: path (str)"
    risk_level = RiskTier.LOW
    required_permission = Permission.FILE_READ

    def get_scope(self, path: str = "", **kwargs) -> Optional[str]:
        return os.path.abspath(path) if path else None

    async def _execute(self, agent_id: str, path: str, **kwargs) -> Any:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return {"error": f"File not found: {path}"}
        if not os.path.isfile(abs_path):
            return {"error": f"Not a file: {path}"}
        try:
            async with aiofiles.open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = await f.read()
            return {"content": content, "path": abs_path, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file. Creates parent directories if needed. Args: path (str), content (str)"
    risk_level = RiskTier.MEDIUM
    required_permission = Permission.FILE_WRITE

    def get_scope(self, path: str = "", **kwargs) -> Optional[str]:
        return os.path.abspath(path) if path else None

    async def _execute(self, agent_id: str, path: str, content: str, **kwargs) -> Any:
        abs_path = os.path.abspath(path)
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            async with aiofiles.open(abs_path, "w", encoding="utf-8") as f:
                await f.write(content)
            return {"success": True, "path": abs_path, "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List files and directories in a path. Args: path (str), pattern (str, optional, default '*')"
    risk_level = RiskTier.LOW
    required_permission = Permission.FILE_READ

    def get_scope(self, path: str = ".", **kwargs) -> Optional[str]:
        return os.path.abspath(path)

    async def _execute(self, agent_id: str, path: str = ".", pattern: str = "*", **kwargs) -> Any:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return {"error": f"Path not found: {path}"}
        try:
            entries = []
            search = os.path.join(abs_path, pattern)
            for item in sorted(glob.glob(search)):
                name = os.path.basename(item)
                is_dir = os.path.isdir(item)
                size = os.path.getsize(item) if not is_dir else None
                entries.append({
                    "name": name,
                    "type": "directory" if is_dir else "file",
                    "size": size,
                })
            return {"path": abs_path, "entries": entries, "count": len(entries)}
        except Exception as e:
            return {"error": str(e)}


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Delete a file. Args: path (str)"
    risk_level = RiskTier.HIGH
    required_permission = Permission.FILE_DELETE

    def get_scope(self, path: str = "", **kwargs) -> Optional[str]:
        return os.path.abspath(path) if path else None

    async def _execute(self, agent_id: str, path: str, **kwargs) -> Any:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return {"error": f"File not found: {path}"}
        try:
            if os.path.isfile(abs_path):
                os.remove(abs_path)
            elif os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
            return {"success": True, "deleted": abs_path}
        except Exception as e:
            return {"error": str(e)}


class CopyFileTool(BaseTool):
    name = "copy_file"
    description = "Copy a file or directory. Args: src (str), dst (str)"
    risk_level = RiskTier.MEDIUM
    required_permission = Permission.FILE_WRITE

    def get_scope(self, dst: str = "", **kwargs) -> Optional[str]:
        return os.path.abspath(dst) if dst else None

    async def _execute(self, agent_id: str, src: str, dst: str, **kwargs) -> Any:
        try:
            abs_src = os.path.abspath(src)
            abs_dst = os.path.abspath(dst)
            os.makedirs(os.path.dirname(abs_dst), exist_ok=True)
            if os.path.isdir(abs_src):
                shutil.copytree(abs_src, abs_dst)
            else:
                shutil.copy2(abs_src, abs_dst)
            return {"success": True, "src": abs_src, "dst": abs_dst}
        except Exception as e:
            return {"error": str(e)}


class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Search for files matching a pattern recursively. Args: path (str), pattern (str), content_search (str, optional)"
    risk_level = RiskTier.LOW
    required_permission = Permission.FILE_READ

    def get_scope(self, path: str = ".", **kwargs) -> Optional[str]:
        return os.path.abspath(path)

    async def _execute(self, agent_id: str, path: str = ".", pattern: str = "*", content_search: str = "", **kwargs) -> Any:
        abs_path = os.path.abspath(path)
        results: List[str] = []
        try:
            for root, dirs, files in os.walk(abs_path):
                # Skip common uninteresting directories
                dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "venv"}]
                for filename in files:
                    if glob.fnmatch.fnmatch(filename, pattern):
                        filepath = os.path.join(root, filename)
                        if content_search:
                            try:
                                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                                    if content_search in f.read():
                                        results.append(filepath)
                            except Exception:
                                pass
                        else:
                            results.append(filepath)
                        if len(results) >= 100:
                            break
            return {"matches": results, "count": len(results)}
        except Exception as e:
            return {"error": str(e)}
