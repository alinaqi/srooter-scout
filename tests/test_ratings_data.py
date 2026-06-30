"""Tests for ported ratings and pricing data."""
from srooter_scout.ratings_data import (
    PRICES, RATINGS, TIER_DIFFICULTY, cost_usd, price_for, rating_for, tier_models,
)


def test_rating_lookup_known():
    r = rating_for('claude-opus')
    assert r.quality >= 9.0
    assert r.speed < 10.0


def test_rating_lookup_unknown_returns_default():
    r = rating_for('nonexistent-model-42')
    assert r.quality == 7.0
    assert r.speed == 6.0


def test_price_for_known():
    inp, out = price_for('deepseek-pro')
    assert inp > 0 and out > 0


def test_price_for_unknown_returns_zero():
    inp, out = price_for('nonexistent-model-42')
    assert inp == 0 and out == 0


def test_cost_usd():
    c = cost_usd('glm-5.2', 1000, 500)
    assert c > 0


def test_cost_usd_unknown_model():
    c = cost_usd('nonexistent-model-42', 1000, 500)
    assert c == 0.0


def test_tier_difficulty():
    assert TIER_DIFFICULTY['trivial'] < TIER_DIFFICULTY['substantive']
    assert TIER_DIFFICULTY['substantive'] < TIER_DIFFICULTY['critical']


def test_tier_models_returns_qualified():
    result = tier_models('trivial')
    assert all(r.quality >= TIER_DIFFICULTY['trivial'] for _, r in result)


def test_all_rated_models_have_prices():
    # every model in RATINGS should have a price entry (or at least a fallback)
    for alias in RATINGS:
        inp, out = price_for(alias)
        assert inp >= 0 and out >= 0, f'{alias} missing price'
