import platform
import psutil
import subprocess
from dataclasses import dataclass
import shutil
import asyncio

@dataclass
class SystemSpecs:
    os_name: str
    cpu_count: int
    ram_gb: float
    disk_free_gb: float
    gpu_name: str | None
    vram_gb: float | None
    recommended_llm: str

async def detect_system() -> SystemSpecs:
    os_name = platform.system()
    cpu_count = psutil.cpu_count(logical=True)
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    disk_usage = shutil.disk_usage("/")
    disk_free_gb = disk_usage.free / (1024**3)
    
    gpu_name = None
    vram_gb = None
    
    if os_name == "Windows":
        try:
            # Try nvidia-smi first
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                parts = result.stdout.strip().split(",")
                gpu_name = parts[0].strip()
                vram_gb = float(parts[1].strip().split()[0]) / 1024
        except FileNotFoundError:
            # Try wmic for generic GPU
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, check=True
                )
                lines = [line.strip() for line in result.stdout.split('\n') if line.strip() and "Name" not in line]
                if lines:
                    gpu_name = lines[0]
            except FileNotFoundError:
                pass
    else:
        # Assuming linux
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                parts = result.stdout.strip().split(",")
                gpu_name = parts[0].strip()
                vram_gb = float(parts[1].strip().split()[0]) / 1024
        except FileNotFoundError:
            pass

    recommended_llm = auto_recommend_llm(ram_gb, gpu_name, vram_gb)
    
    return SystemSpecs(
        os_name=os_name,
        cpu_count=cpu_count,
        ram_gb=ram_gb,
        disk_free_gb=disk_free_gb,
        gpu_name=gpu_name,
        vram_gb=vram_gb,
        recommended_llm=recommended_llm
    )

def auto_recommend_llm(ram_gb: float, gpu_name: str | None, vram_gb: float | None) -> str:
    if ram_gb >= 16 and gpu_name and vram_gb and vram_gb >= 6:
        return 'mistral:7b'
    elif ram_gb >= 8:
        return 'qwen2.5:3b'
    else:
        return 'cloud_only'
