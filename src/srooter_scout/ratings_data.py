"""Ported model ratings, tier difficulties, and pricing (MIT-licensed).

All figures are ESTIMATES based on SWE-bench Verified + provider-published data.
Actual performance and pricing may vary. The data here is the same that powers
srooter's own routing engine, extracted as a static snapshot.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRating:
    speed: float
    quality: float


# Tier difficulty — the minimum quality required to serve a task capably.
TIER_DIFFICULTY: dict[str, float] = {
    'trivial': 3.0,
    'substantive': 7.5,
    'long_context': 7.5,
    'think': 8.5,
    'critical': 9.5,
}

# Model ratings (alias -> (speed, quality)), 0-10 scale.
_UNKNOWN_RATING = ModelRating(speed=6.0, quality=7.0)

RATINGS: dict[str, ModelRating] = {
    'claude-opus': ModelRating(5.0, 9.8),
    'claude-haiku': ModelRating(9.0, 7.0),
    'deepseek-pro': ModelRating(6.0, 9.0),
    'deepseek': ModelRating(7.0, 7.0),
    'gemini': ModelRating(9.0, 8.2),
    'glm-5.2': ModelRating(6.5, 9.8),
    'gpt-5.5': ModelRating(5.5, 9.3),
    'codex': ModelRating(4.0, 9.2),
    'grok': ModelRating(7.0, 8.5),
    'qwen': ModelRating(7.5, 7.5),
    'minimax-m2.5': ModelRating(8.0, 8.0),
    'cerebras': ModelRating(10.0, 7.0),
    'kimi': ModelRating(5.0, 7.8),
}

# Prices: $ per 1K tokens (input, output). Estimates — always range-check.
# Unknown models return (0, 0).
PRICES: dict[str, tuple[float, float]] = {
    'claude-opus': (0.015, 0.075),
    'claude-haiku': (0.0008, 0.004),
    'deepseek-pro': (0.00044, 0.00087),
    'deepseek': (0.00014, 0.00028),
    'gemini': (0.00015, 0.00060),
    'glm-5.2': (0.0006, 0.0022),
    'gpt-5.5': (0.005, 0.015),
    'codex': (0.015, 0.075),
    'grok': (0.002, 0.010),
    'qwen': (0.0002, 0.0005),
    'minimax-m2.5': (0.0003, 0.0003),
    'cerebras': (0.00025, 0.00069),
    'kimi': (0.0006, 0.0025),
}


def rating_for(alias: str) -> ModelRating:
    return RATINGS.get(alias, _UNKNOWN_RATING)


def price_for(alias: str) -> tuple[float, float]:
    return PRICES.get(alias, (0.0, 0.0))


def cost_usd(alias: str, tin: int, tout: int) -> float:
    inp, out = price_for(alias)
    if inp == 0 and out == 0:
        return 0.0
    return round(tin * inp + tout * out, 6)


def tier_models(tier: str) -> list[tuple[str, ModelRating]]:
    need = TIER_DIFFICULTY.get(tier, 5.0)
    return [(a, r) for a, r in RATINGS.items() if r.quality >= need]
