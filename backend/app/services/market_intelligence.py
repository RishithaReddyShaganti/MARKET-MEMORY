"""Deterministic change detection and attention ranking for Market Memory."""

from dataclasses import dataclass
from math import isfinite

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entities import ChangeSignal, Insight, MarketEvent, MarketSnapshot, RelevanceScore, WatchlistItem
from app.models.enums import IntentType

PRICE_MOVE_CAP = 0.10
VOLUME_RATIO_CAP = 5.0
FUNDAMENTAL_CHANGE_CAP = 0.20

SIGNIFICANCE_WEIGHTS = {
    "price": 0.25,
    "volume": 0.20,
    "market": 0.15,
    "sector": 0.15,
    "fundamental": 0.10,
    "event": 0.10,
    "news": 0.05,
}


@dataclass(frozen=True)
class SignalValues:
    stock_return: float | None
    volume_ratio: float | None
    price: float
    volume: float
    market: float
    sector: float
    historical: float
    fundamental: float
    event: float
    news: float
    significance: float


@dataclass(frozen=True)
class AttentionAssessment:
    score: float
    level: str


def clamp(value: float | int | None) -> float:
    """Constrain optional numeric input to a safe normalized 0–1 value."""
    if value is None:
        return 0.0
    number = float(value)
    if not isfinite(number):
        return 0.0
    return max(0.0, min(number, 1.0))


def stock_return(current_price: float | None, previous_price: float | None) -> float | None:
    """Calculate a safe decimal stock return, or None when it cannot be calculated."""
    if current_price is None or previous_price is None or previous_price == 0:
        return None
    result = (float(current_price) - float(previous_price)) / abs(float(previous_price))
    return result if isfinite(result) else None


def divergence(stock_change: float | None, benchmark_change: float | None) -> float | None:
    """Calculate the signed divergence between a stock and a benchmark return."""
    if stock_change is None or benchmark_change is None:
        return None
    result = float(stock_change) - float(benchmark_change)
    return result if isfinite(result) else None


def volume_ratio(current_volume: float | None, baseline_volume: float | None) -> float | None:
    """Calculate a safe current-to-baseline volume ratio."""
    if current_volume is None or baseline_volume is None or baseline_volume <= 0:
        return None
    result = float(current_volume) / float(baseline_volume)
    return result if isfinite(result) else None


def normalize_movement(value: float | None, cap: float = PRICE_MOVE_CAP) -> float:
    return clamp(abs(value) / cap if value is not None and cap > 0 else None)


def normalize_volume(ratio: float | None) -> float:
    """Map normal volume (1x) to 0 and a 5x-or-greater spike to 1."""
    return clamp((abs(ratio - 1.0) / (VOLUME_RATIO_CAP - 1.0)) if ratio is not None else None)


def historical_abnormality(stock_change: float | None, baseline_return: float | None) -> float:
    """Map movement beyond its historical baseline to a normalized anomaly score."""
    if stock_change is None or baseline_return is None or baseline_return <= 0:
        return 0.0
    multiple = abs(stock_change) / abs(baseline_return)
    return clamp((multiple - 1.0) / 4.0)


def calculate_signals(
    current_price: float | None,
    previous_price: float | None,
    current_volume: float | None = None,
    baseline_volume: float | None = None,
    market_return: float | None = None,
    sector_return: float | None = None,
    historical_return_baseline: float | None = None,
    fundamental_change: float | None = None,
    event_strength: float | bool | None = None,
    news_strength: float | bool | None = None,
) -> SignalValues:
    """Produce normalized component signals and a bounded 0–100 significance score."""
    change = stock_return(current_price, previous_price)
    market_gap = divergence(change, market_return)
    sector_gap = divergence(change, sector_return)
    ratio = volume_ratio(current_volume, baseline_volume)
    historical = historical_abnormality(change, historical_return_baseline)
    price = max(normalize_movement(change), historical)
    volume = normalize_volume(ratio)
    market = normalize_movement(market_gap)
    sector = normalize_movement(sector_gap)
    fundamental = normalize_movement(fundamental_change, FUNDAMENTAL_CHANGE_CAP)
    event = clamp(float(event_strength) if event_strength is not None else None)
    news = clamp(float(news_strength) if news_strength is not None else None)
    significance = 100 * (
        price * SIGNIFICANCE_WEIGHTS["price"]
        + volume * SIGNIFICANCE_WEIGHTS["volume"]
        + market * SIGNIFICANCE_WEIGHTS["market"]
        + sector * SIGNIFICANCE_WEIGHTS["sector"]
        + fundamental * SIGNIFICANCE_WEIGHTS["fundamental"]
        + event * SIGNIFICANCE_WEIGHTS["event"]
        + news * SIGNIFICANCE_WEIGHTS["news"]
    )
    return SignalValues(change, ratio, price, volume, market, sector, historical, fundamental, event, news, max(0.0, min(significance, 100.0)))


def record_snapshot(db: Session, snapshot: MarketSnapshot) -> MarketSnapshot:
    """Persist an input snapshot without contacting any external market-data provider."""
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def record_event(db: Session, event: MarketEvent) -> MarketEvent:
    """Persist a market event idempotently using its existing source-event constraint."""
    existing = db.scalar(
        select(MarketEvent).where(
            or_(
                (MarketEvent.source == event.source) & (MarketEvent.source_event_id == event.source_event_id),
                MarketEvent.event_hash == event.event_hash,
            )
        )
    )
    if existing is not None:
        return existing
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def create_change_signal(
    db: Session,
    current_snapshot: MarketSnapshot,
    previous_snapshot: MarketSnapshot | None = None,
    *,
    baseline_volume: float | None = None,
    historical_return_baseline: float | None = None,
    fundamental_change: float | None = None,
    event: MarketEvent | None = None,
    news_strength: float | bool | None = None,
) -> ChangeSignal:
    """Detect deterministic changes from snapshots and persist the resulting signal."""
    values = calculate_signals(
        current_price=float(current_snapshot.price) if current_snapshot.price is not None else None,
        previous_price=float(previous_snapshot.price) if previous_snapshot and previous_snapshot.price is not None else None,
        current_volume=float(current_snapshot.volume) if current_snapshot.volume is not None else None,
        baseline_volume=baseline_volume,
        market_return=float(current_snapshot.market_return) if current_snapshot.market_return is not None else None,
        sector_return=float(current_snapshot.sector_return) if current_snapshot.sector_return is not None else None,
        historical_return_baseline=historical_return_baseline,
        fundamental_change=fundamental_change,
        event_strength=event is not None,
        news_strength=news_strength,
    )
    signal = ChangeSignal(
        symbol=current_snapshot.symbol.upper(),
        detected_at=current_snapshot.timestamp,
        price_signal=values.price,
        volume_signal=values.volume,
        market_signal=values.market,
        sector_signal=values.sector,
        historical_signal=values.historical,
        fundamental_signal=values.fundamental,
        event_signal=values.event,
        news_signal=values.news,
        significance_score=values.significance,
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


def _signal_value(signal: ChangeSignal, name: str) -> float:
    return clamp(float(getattr(signal, name) or 0))


def relevance_score(signal: ChangeSignal, item: WatchlistItem) -> tuple[float, str]:
    """Score the match between a detected change and a user's stated watch intent."""
    price = _signal_value(signal, "price_signal")
    volume = _signal_value(signal, "volume_signal")
    market = _signal_value(signal, "market_signal")
    sector = _signal_value(signal, "sector_signal")
    fundamental = _signal_value(signal, "fundamental_signal")
    event = _signal_value(signal, "event_signal")
    news = _signal_value(signal, "news_signal")
    mapping = {
        IntentType.EARNINGS: (0.60 * fundamental + 0.30 * event + 0.10 * news, "earnings-related change"),
        IntentType.GROWTH: (0.45 * price + 0.30 * volume + 0.25 * fundamental, "growth-related movement"),
        IntentType.VALUATION: (0.60 * price + 0.40 * fundamental, "valuation-related movement"),
        IntentType.COMPETITION: (0.55 * sector + 0.25 * market + 0.20 * news, "competitive context change"),
        IntentType.CORPORATE_EVENT: (0.80 * event + 0.20 * news, "corporate event"),
        IntentType.LONG_TERM_BUSINESS: (0.60 * fundamental + 0.25 * event + 0.15 * news, "long-term business change"),
        IntentType.EXPLORING: (float(signal.significance_score or 0) / 100, "general market movement"),
        IntentType.CUSTOM: (0.0, "custom intent"),
    }
    base, reason = mapping[item.intent_type]
    text = (item.intent_text or "").lower()
    text_matches = {
        "earnings": max(fundamental, event, news), "revenue": fundamental, "profit": fundamental,
        "growth": max(price, volume, fundamental), "ev": max(price, volume, fundamental), "valuation": max(price, fundamental),
        "competition": max(sector, news), "competitor": max(sector, news), "event": event,
    }
    matched = [score for keyword, score in text_matches.items() if keyword in text]
    if item.intent_type is IntentType.CUSTOM:
        base = max(matched, default=0.0)
        reason = "matched custom intent" if matched else "no matched custom intent keywords"
    elif matched:
        base = max(base, max(matched))
        reason = "intent text matched detected change"
    return max(0.0, min(base * 100, 100.0)), reason


def attention_assessment(significance: float | None, relevance: float | None) -> AttentionAssessment:
    """Combine separate scores only for ranking, preserving each source score independently."""
    score = max(0.0, min(0.70 * float(significance or 0) + 0.30 * float(relevance or 0), 100.0))
    if score <= 30:
        level = "NORMAL"
    elif score <= 60:
        level = "NOTABLE"
    elif score <= 80:
        level = "IMPORTANT"
    else:
        level = "HIGH ATTENTION"
    return AttentionAssessment(score, level)


def evaluate_watchlist_item(db: Session, signal: ChangeSignal, item: WatchlistItem) -> tuple[RelevanceScore, Insight]:
    """Persist an intent relevance result and its deterministic attention classification."""
    score, reason = relevance_score(signal, item)
    assessment = attention_assessment(float(signal.significance_score or 0), score)
    relevance = RelevanceScore(
        change_signal_id=signal.id,
        watchlist_item_id=item.id,
        intent_match_score=score,
        relevance_level=assessment.level,
        matched_intent=item.intent_type.value,
        reason=reason,
    )
    insight = Insight(
        change_signal_id=signal.id,
        relevance_score=relevance,
        attention_level=assessment.level,
        explanation=f"{reason}; deterministic attention score {assessment.score:.1f}.",
        confidence=score / 100,
    )
    db.add_all([relevance, insight])
    db.commit()
    db.refresh(relevance)
    db.refresh(insight)
    return relevance, insight
