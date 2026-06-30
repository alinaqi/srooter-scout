"""Tests for report generation."""
from srooter_scout.hardware import HardwareProfile
from srooter_scout.history import ScanResult
from srooter_scout.recommender import Recommendation
from srooter_scout.report import generate_report


def test_generate_report_has_sections():
    hw = HardwareProfile(ram_gb=16, cpu_cores=8, cpu_arch='arm64', gpu_name='Apple M3', gpu_vram_gb=None)
    hist = ScanResult(total_tokens=10000, model_spend={'claude-opus': {'input': 5000, 'output': 5000}})
    rec = Recommendation(local_model='Qwen 7B', srooter_cost_est=10.0, savings_pct=75.0, current_cost_est=40.0)
    report = generate_report(hw, hist, rec, 'markdown')
    assert '## ' in report
    assert 'Hardware' in report
    assert 'srooter' in report.lower() or 'Savings' in report
    assert '10.0' in report or '$' in report


def test_generate_report_markdown_export():
    hw = HardwareProfile(ram_gb=8, cpu_cores=4, cpu_arch='x86_64', gpu_name=None, gpu_vram_gb=None)
    hist = ScanResult()
    rec = Recommendation(local_model='Qwen 1.5B', srooter_cost_est=0.0, savings_pct=0.0, current_cost_est=0.0)
    report = generate_report(hw, hist, rec, 'markdown')
    assert report.startswith('#') or report.startswith('##')
    assert 'Summary' in report
