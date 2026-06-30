"""Cross-platform hardware detection — CPU, RAM, GPU."""
from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass


@dataclass
class HardwareProfile:
    ram_gb: float
    cpu_cores: int
    cpu_arch: str
    gpu_name: str | None
    gpu_vram_gb: float | None

    def summary(self) -> str:
        lines = [
            f'CPU: {self.cpu_cores} cores ({self.cpu_arch})',
            f'RAM: {self.ram_gb:.0f} GB',
        ]
        if self.gpu_name and self.gpu_name != 'unknown':
            vram = f' ({self.gpu_vram_gb:.0f} GB VRAM)' if self.gpu_vram_gb else ''
            lines.append(f'GPU: {self.gpu_name}{vram}')
        return ' / '.join(lines)

    def model_size_class(self) -> str:
        """Best local model size for this hardware (Ollama-compatible)."""
        effective = self.gpu_vram_gb if self.gpu_vram_gb else self.ram_gb
        if effective < 6:
            return 'micro'
        if effective < 14:
            return '7b'
        if effective < 36:
            return '14b-32b'
        return '32b+'


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ''


def _detect_ram() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        try:
            out = _run(['sysctl', '-n', 'hw.memsize'])
            return round(int(out.strip()) / (1024 ** 3), 1) if out else 8.0
        except Exception:
            return 8.0


def _detect_cpu() -> tuple[int, str]:
    cores = os.cpu_count() or 4
    arch = platform.machine().lower()
    if arch in ('arm64', 'aarch64'):
        pass
    elif 'x86' in arch:
        arch = 'x86_64'
    else:
        arch = 'unknown'
    return cores, arch


def _detect_gpu() -> tuple[str | None, float | None]:
    # Apple Silicon — check for Metal-capable GPU via system_profiler
    out = _run(['system_profiler', 'SPDisplaysDataType'])
    if out:
        for line in out.splitlines():
            if 'Chipset Model' in line:
                name = line.split(':', 1)[-1].strip()
                return name, None  # Apple unified memory — VRAM ≈ total RAM
            if 'VRAM' in line:
                try:
                    vram = line.split(':', 1)[-1].strip().replace(' MB', '')
                    return None, round(int(vram) / 1024, 1)
                except Exception:
                    pass
        # fallback: if M-series chip detected
        cpu = _run(['sysctl', '-n', 'machdep.cpu.brand_string'])
        if any(m in cpu for m in ('M1', 'M2', 'M3', 'M4')):
            return f'Apple {cpu.strip()}', None

    # NVIDIA
    out = _run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'])
    if out:
        parts = out.split(',')
        if len(parts) >= 2:
            name = parts[0].strip()
            vram = parts[1].strip().replace(' MiB', '').replace(' GiB', '')
            try:
                return name, round(int(vram) / 1024, 1)
            except Exception:
                return name, None

    # AMD ROCm
    out = _run(['rocm-smi', '--showmeminfo', 'vram'])
    if out:
        return 'AMD GPU', None

    return 'unknown', None


def detect_hardware() -> HardwareProfile:
    cores, arch = _detect_cpu()
    ram = _detect_ram()
    gpu_name, gpu_vram = _detect_gpu()
    return HardwareProfile(
        ram_gb=ram, cpu_cores=cores, cpu_arch=arch,
        gpu_name=gpu_name, gpu_vram_gb=gpu_vram)
