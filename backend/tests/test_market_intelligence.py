from datetime import datetime, timezone
import uuid

import pytest

from app.db.session import SessionLocal
from app.models.entities import MarketEvent, MarketSnapshot, User, Watchlist, WatchlistItem
from app.models.enums import FreshnessStatus, IntentType
from app.services.market_intelligence import (
    attention_assessment,
    calculate_signals,
    create_change_signal,
    evaluate_watchlist_item,
    record_event,
    record_snapshot,
    relevance_score,
)


def item(intent_type: IntentType, intent_text: str | None = None) -> WatchlistItem:
    return WatchlistItem(watchlist_id=uuid.uuid4(), symbol="TATAMOTORS", company_name="Tata Motors", intent_type=intent_type, intent_text=intent_text)


def test_normal_movement_has_low_significance() -> None:
    signals = calculate_signals(101, 100, 1_000, 1_000, market_return=0.01, sector_return=0.01, historical_return_baseline=0.02)

    assert signals.significance == pytest.approx(2.5)
    assert signals.price == pytest.approx(0.1)
    assert signals.volume < 0.1


def test_abnormal_price_movement_and_volume_spike_are_normalized() -> None:
    signals = calculate_signals(150, 100, 5_000, 1_000, historical_return_baseline=0.02)

    assert signals.price == 1.0
    assert signals.historical == 1.0
    assert signals.volume == 1.0
    assert signals.significance == pytest.approx(45.0)


def test_market_and_sector_divergence_are_detected() -> None:
    signals = calculate_signals(110, 100, market_return=-0.05, sector_return=-0.03)

    assert signals.market == 1.0
    assert signals.sector == 1.0
    assert signals.significance == pytest.approx(55.0)


def test_relevance_uses_intent_type_and_custom_intent_text() -> None:
    signals = calculate_signals(120, 100, 3_000, 1_000, fundamental_change=0.15, event_strength=True)
    signal = type("Signal", (), {
        "price_signal": signals.price, "volume_signal": signals.volume, "market_signal": signals.market,
        "sector_signal": signals.sector, "fundamental_signal": signals.fundamental, "event_signal": signals.event,
        "news_signal": signals.news, "significance_score": signals.significance,
    })()

    growth_score, _ = relevance_score(signal, item(IntentType.GROWTH, "I want EV growth."))
    event_score, _ = relevance_score(signal, item(IntentType.CORPORATE_EVENT))
    custom_score, _ = relevance_score(signal, item(IntentType.CUSTOM, "Track EV growth"))

    assert growth_score > event_score
    assert custom_score > 0


def test_missing_and_extreme_data_stays_safe_and_bounded() -> None:
    missing = calculate_signals(None, None, None, None)
    extreme = calculate_signals(1e308, 1, 1e308, 1, market_return=-1e308, sector_return=1e308, fundamental_change=1e308, event_strength=99, news_strength=-3)

    assert missing.significance == 0
    assert all(0 <= value <= 1 for value in (extreme.price, extreme.volume, extreme.market, extreme.sector, extreme.fundamental, extreme.event, extreme.news))
    assert 0 <= extreme.significance <= 100


@pytest.mark.parametrize(("score", "relevance", "level"), [(0, 0, "NORMAL"), (30, 30, "NORMAL"), (61, 61, "IMPORTANT"), (81, 81, "HIGH ATTENTION")])
def test_attention_boundaries(score: float, relevance: float, level: str) -> None:
    assert attention_assessment(score, relevance).level == level


def test_flagship_high_attention_growth_scenario() -> None:
    signals = calculate_signals(130, 100, 5_000, 1_000, market_return=0, sector_return=0, historical_return_baseline=0.02, fundamental_change=0.20, event_strength=True, news_strength=True)
    signal = type("Signal", (), {
        "price_signal": signals.price, "volume_signal": signals.volume, "market_signal": signals.market,
        "sector_signal": signals.sector, "fundamental_signal": signals.fundamental, "event_signal": signals.event,
        "news_signal": signals.news, "significance_score": signals.significance,
    })()
    relevance, _ = relevance_score(signal, item(IntentType.GROWTH, "I want to track EV growth."))
    attention = attention_assessment(signals.significance, relevance)

    assert signals.significance == 100
    assert relevance == 100
    assert attention.level == "HIGH ATTENTION"


def test_snapshot_event_processing_and_persisted_insight() -> None:
    db = SessionLocal()
    try:
        timestamp = datetime.now(timezone.utc)
        previous = record_snapshot(db, MarketSnapshot(symbol="TATAMOTORS", price=100, volume=1_000, market_return=0, sector_return=0, timestamp=timestamp, source="test", freshness_status=FreshnessStatus.FRESH))
        current = record_snapshot(db, MarketSnapshot(symbol="TATAMOTORS", price=120, volume=3_000, market_return=0, sector_return=0, timestamp=timestamp, source="test", freshness_status=FreshnessStatus.FRESH))
        event = record_event(db, MarketEvent(symbol="TATAMOTORS", event_type="earnings", event_time=timestamp, source="test", source_event_id="event-1", event_hash="hash-1"))
        assert record_event(db, MarketEvent(symbol="TATAMOTORS", event_type="earnings", event_time=timestamp, source="test", source_event_id="event-1", event_hash="hash-2")).id == event.id

        user = User()
        watchlist = Watchlist(user=user, name="Growth")
        watched = WatchlistItem(watchlist=watchlist, symbol="TATAMOTORS", company_name="Tata Motors", intent_type=IntentType.GROWTH, intent_text="EV growth")
        db.add(watched)
        db.commit()
        signal = create_change_signal(db, current, previous, baseline_volume=1_000, historical_return_baseline=0.02, fundamental_change=0.15, event=event)
        relevance, insight = evaluate_watchlist_item(db, signal, watched)

        assert signal.significance_score is not None
        assert relevance.intent_match_score is not None
        assert insight.attention_level in {"NORMAL", "NOTABLE", "IMPORTANT", "HIGH ATTENTION"}
    finally:
        db.close()
