"""Tests for the srooter-scout recommender engine."""
from srooter_scout.hardware import HardwareProfile
from srooter_scout.history import ScanResult
from srooter_scout.recommender import recommend_models, Recommendation


def test_recommend_micro_models():
    hw = HardwareProfile(ram_gb=4, cpu_cores=4, cpu_arch='x86_64', gpu_name=None, gpu_vram_gb=None)
    hist = ScanResult(total_tokens=1000, model_spend={'claude-opus': {'input': 500, 'output': 500}})
    rec = recommend_models(hw, hist)
    assert isinstance(rec, Recommendation)
    assert 'Micro' in rec.local_model or '1.5b' in rec.local_model.lower()
    assert rec.srooter_cost_est < hist.total_cost


def test_recommend_standard_models():
    hw = HardwareProfile(ram_gb=10, cpu_cores=8, cpu_arch='arm64', gpu_name=None, gpu_vram_gb=None)
    hist = ScanResult(total_tokens=1000, model_spend={'claude-opus': {'input': 500, 'output': 500}})
    rec = recommend_models(hw, hist)
    assert '7b' in rec.local_model or '8b' in rec.local_model
    assert rec.savings_pct > 0.0


def test_recommend_power_models():
    hw = HardwareProfile(ram_gb=64, cpu_cores=16, cpu_arch='arm64', gpu_name='Apple M4 Ultra', gpu_vram_gb=48)
    hist = ScanResult(total_tokens=1000, model_spend={'claude-opus': {'input': 500, 'output': 500}})
    rec = recommend_models(hw, hist)
    assert '70b' in rec.local_model or '32b' in rec.local_model


def test_srooter_savings_calc_empty_history():
    hw = HardwareProfile(ram_gb=16, cpu_cores=8, cpu_arch='arm64', gpu_name=None, gpu_vram_gb=None)
    hist = ScanResult()
    rec = recommend_models(hw, hist)
    assert rec.srooter_cost_est == 0.0
    assert rec.savings_pct == 0.0
