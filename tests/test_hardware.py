"""Tests for hardware detection."""
import platform
from srooter_scout.hardware import detect_hardware, HardwareProfile


def test_produces_valid_ram():
    hw = detect_hardware()
    assert hw.ram_gb > 0
    assert hw.ram_gb <= 2048  # nobody has 2TB+ RAM


def test_produces_cpu_cores():
    hw = detect_hardware()
    assert hw.cpu_cores > 0


def test_cpu_arch():
    hw = detect_hardware()
    assert hw.cpu_arch in ('arm64', 'x86_64', 'aarch64', 'unknown')


def test_summary_non_empty():
    hw = detect_hardware()
    assert hw.summary()
    assert 'CPU' in hw.summary()


def test_model_bucket():
    hw = HardwareProfile(ram_gb=4, cpu_cores=8, cpu_arch='arm64', gpu_name=None, gpu_vram_gb=None)
    assert hw.model_size_class() == 'micro'
    hw2 = HardwareProfile(ram_gb=8, cpu_cores=8, cpu_arch='arm64', gpu_name=None, gpu_vram_gb=None)
    assert hw2.model_size_class() == '7b'
    hw3 = HardwareProfile(ram_gb=32, cpu_cores=8, cpu_arch='arm64', gpu_name='Apple M3 Max', gpu_vram_gb=27)
    assert hw3.model_size_class() == '14b-32b'
    hw4 = HardwareProfile(ram_gb=64, cpu_cores=16, cpu_arch='arm64', gpu_name='Apple M4 Ultra', gpu_vram_gb=48)
    assert hw4.model_size_class() == '32b+'


def test_gpu_fallback():
    hw = detect_hardware()
    # always produces a valid profile even if GPU detection fails
    assert hw.gpu_name is not None  # can be 'unknown'
