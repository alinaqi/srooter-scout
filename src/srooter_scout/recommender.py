"""Model recommendation engine — local models and srooter routing estimation."""
from __future__ import annotations

from dataclasses import dataclass

from srooter_scout.hardware import HardwareProfile
from srooter_scout.history import ScanResult
from srooter_scout.ratings_data import cost_usd, rating_for, tier_models

# Tier routing: srooter routes each task to the best cheap model that meets its
# quality threshold. These are the routing assignments for cost estimation.
_TIER_ROUTING: dict[str, str] = {
    'trivial': 'gemini',
    'substantive': 'glm-5.2',
    'long_context': 'glm-5.2',
    'think': 'deepseek-pro',
    'critical': 'claude-opus',
}

# Estimated workload distribution (modifiable percentage breakdown) of a typical
# coding session — based on srooter's observed routing from ~1000 benchmark turns.
_WORKLOAD_DISTRIBUTION: dict[str, float] = {
    'trivial': 0.35,
    'substantive': 0.35,
    'long_context': 0.10,
    'think': 0.10,
    'critical': 0.10,
}

_LOCAL_MODELS: dict[str, str] = {
    'micro': 'Qwen 2.5-Coder 1.5B (Ollama: qwen-coder:1.5b)',
    '7b': 'Qwen 2.5-Coder 7B (Ollama: qwen-coder:7b)',
    '14b-32b': 'Qwen 2.5-Coder 14B or DeepSeek-Coder 33B (Ollama: qwen-coder:14b)',
    '32b+': 'DeepSeek-Coder V2 70B or Qwen 2.5-Coder 32B (Ollama: deepseek-coder-v2:70b)',
}


@dataclass
class Recommendation:
    local_model: str
    srooter_cost_est: float
    savings_pct: float
    current_cost_est: float


def _routed_cost(total_tokens: int) -> float:
    """Estimate the cost if the same total_tokens were routed through srooter's
    tier system, applying the workload distribution."""
    total_cost = 0.0
    for tier, fraction in _WORKLOAD_DISTRIBUTION.items():
        model = _TIER_ROUTING[tier]
        tin_est = int(total_tokens * fraction * 0.75)  # ~75% input, 25% output
        tout_est = int(total_tokens * fraction * 0.25)
        total_cost += cost_usd(model, tin_est, tout_est)
    return round(total_cost, 6)


def recommend_models(hw: HardwareProfile, history: ScanResult) -> Recommendation:
    local_model = _LOCAL_MODELS.get(hw.model_size_class(), _LOCAL_MODELS['micro'])
    current_cost = history.total_cost
    srooter_cost = _routed_cost(history.total_tokens) if history.total_tokens > 0 else 0.0
    savings_pct = round((1 - srooter_cost / current_cost) * 100, 1) if current_cost > 0 else 0.0
    return Recommendation(
        local_model=local_model,
        srooter_cost_est=srooter_cost,
        savings_pct=savings_pct,
        current_cost_est=current_cost,
    )
