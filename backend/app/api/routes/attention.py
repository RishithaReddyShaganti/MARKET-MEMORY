"""Read APIs and a deterministic demo scenario for the end-to-end product flow."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.watchlists import for_development_user
from app.db.session import get_db
from app.models.entities import ChangeSignal, Evidence, Insight, MarketEvent, MarketSnapshot, RelevanceScore, Watchlist, WatchlistItem
from app.models.enums import FreshnessStatus, IntentType, VerificationStatus
from app.services.market_intelligence import attention_assessment, create_change_signal, evaluate_watchlist_item, record_event, record_snapshot

router = APIRouter(tags=["attention"])


def insight_data(insight: Insight) -> dict[str, object]:
    relevance = insight.relevance_score
    signal = insight.change_signal
    significance = float(signal.significance_score or 0)
    relevance_value = float(relevance.intent_match_score or 0) if relevance else 0
    return {"id": str(insight.id), "symbol": signal.symbol, "significance": significance, "relevance": relevance_value, "attention_score": attention_assessment(significance, relevance_value).score, "attention_level": insight.attention_level, "confidence": float(insight.confidence or 0), "explanation": insight.explanation, "freshness": "fresh", "evidence_available": bool(insight.evidence), "watchlist_item_id": str(relevance.watchlist_item_id) if relevance else None}


@router.post("/demo/flagship")
def seed_flagship(db: Session = Depends(get_db)) -> dict[str, object]:
    """Idempotently seed the deterministic starting watchlist and its insights."""
    user_id = for_development_user(db)
    watchlist = db.scalar(select(Watchlist).where(Watchlist.user_id == user_id, Watchlist.name == "Flagship demo"))
    if watchlist is None:
        watchlist = Watchlist(user_id=user_id, name="Flagship demo")
        db.add(watchlist); db.commit(); db.refresh(watchlist)
    now = datetime.now(timezone.utc)
    starting_stocks = [
        ("TATAMOTORS", "Tata Motors", IntentType.GROWTH, "I want to track EV growth.", 800, 1040, 5_000_000, 0.20, True, True),
        ("INFY", "Infosys", IntentType.EARNINGS, "I want to follow earnings and growth.", 1500, 1575, 2_000_000, 0.10, True, False),
        ("RELIANCE", "Reliance", IntentType.LONG_TERM_BUSINESS, "I am watching the long-term business.", 2900, 2958, 1_200_000, 0.15, True, False),
        ("HDFCBANK", "HDFC Bank", IntentType.VALUATION, None, 1600, 1616, 1_000_000, None, False, False),
        ("M&M", "M&M", IntentType.GROWTH, None, 1800, 1818, 1_000_000, None, False, False),
        ("MARUTI", "Maruti", IntentType.COMPETITION, None, 12000, 12120, 1_000_000, None, False, False),
    ]
    seeded = False
    primary: Insight | None = None
    for symbol, name, intent, intent_text, previous_price, current_price, volume, fundamental, has_event, news in starting_stocks:
        item = db.scalar(select(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist.id, WatchlistItem.symbol == symbol))
        if item is None:
            item = WatchlistItem(watchlist_id=watchlist.id, symbol=symbol, company_name=name, intent_type=intent, intent_text=intent_text)
            db.add(item); db.commit(); db.refresh(item)
        existing = db.scalar(select(Insight).join(RelevanceScore).where(RelevanceScore.watchlist_item_id == item.id))
        if existing is not None:
            if symbol == "TATAMOTORS": primary = existing
            continue
        previous = record_snapshot(db, MarketSnapshot(symbol=symbol, price=previous_price, volume=1_000_000, market_return=0.01, sector_return=0.01, timestamp=now - timedelta(days=1), source="demo", freshness_status=FreshnessStatus.FRESH))
        current = record_snapshot(db, MarketSnapshot(symbol=symbol, price=current_price, volume=volume, market_return=0.01, sector_return=0.01, timestamp=now, source="demo", freshness_status=FreshnessStatus.FRESH))
        event = record_event(db, MarketEvent(symbol=symbol, event_type="corporate_event", event_time=now, source="demo", source_event_id=f"{symbol.lower()}-starting-v1", event_hash=f"{symbol.lower()}-starting-v1")) if has_event else None
        signal = create_change_signal(db, current, previous, baseline_volume=1_000_000, historical_return_baseline=0.02, fundamental_change=fundamental, event=event, news_strength=news)
        _, insight = evaluate_watchlist_item(db, signal, item)
        evidence = [Evidence(insight_id=insight.id, evidence_type="market_snapshot", description=f"Observed price moved from {previous_price} to {current_price} with recorded trading volume.", source="demo", source_reference=None, observed_at=now, freshness_status=FreshnessStatus.FRESH, verification_status=VerificationStatus.VERIFIED)]
        if event is not None:
            evidence.append(Evidence(insight_id=insight.id, evidence_type="corporate_event", description="Synthetic corporate event recorded for this watched stock.", source="demo", source_reference=None, observed_at=now, freshness_status=FreshnessStatus.FRESH, verification_status=VerificationStatus.VERIFIED))
        db.add_all(evidence); db.commit(); seeded = True
        if symbol == "TATAMOTORS": primary = insight
    if primary is None:
        primary = db.scalar(select(Insight).join(RelevanceScore).join(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist.id, WatchlistItem.symbol == "TATAMOTORS"))
    return {"watchlist_id": str(watchlist.id), "insight": insight_data(primary) if primary else None, "seeded": seeded}


@router.get("/attention")
def attention_feed(db: Session = Depends(get_db)) -> dict[str, object]:
    user_id = for_development_user(db)
    insights = list(db.scalars(select(Insight).join(ChangeSignal).join(RelevanceScore).join(WatchlistItem).join(Watchlist).where(Watchlist.user_id == user_id).order_by(ChangeSignal.significance_score.desc())).all())
    cards = [insight_data(insight) for insight in insights]
    return {"watched_stocks": len({card["symbol"] for card in cards}), "events_detected": len(cards), "normal": sum(card["attention_level"] == "NORMAL" for card in cards), "worth_knowing": sum(card["attention_level"] in {"NOTABLE", "IMPORTANT"} for card in cards), "need_attention": sum(card["attention_level"] == "HIGH ATTENTION" for card in cards), "items": cards}


@router.get("/stocks/{symbol}")
def stock_detail(symbol: str, db: Session = Depends(get_db)) -> dict[str, object]:
    normalized = symbol.upper()
    snapshot = db.scalar(select(MarketSnapshot).where(MarketSnapshot.symbol == normalized).order_by(MarketSnapshot.timestamp.desc()))
    signal = db.scalar(select(ChangeSignal).where(ChangeSignal.symbol == normalized).order_by(ChangeSignal.detected_at.desc()))
    if snapshot is None or signal is None:
        raise HTTPException(404, "Stock detail not found")
    insights = list(db.scalars(select(Insight).join(ChangeSignal).where(ChangeSignal.id == signal.id)).all())
    return {"symbol": normalized, "price": float(snapshot.price) if snapshot.price is not None else None, "market_return": float(snapshot.market_return) if snapshot.market_return is not None else None, "sector_return": float(snapshot.sector_return) if snapshot.sector_return is not None else None, "freshness": snapshot.freshness_status.value, "breakdown": {"price": float(signal.price_signal or 0), "volume": float(signal.volume_signal or 0), "market": float(signal.market_signal or 0), "sector": float(signal.sector_signal or 0), "fundamental": float(signal.fundamental_signal or 0), "event": float(signal.event_signal or 0), "news": float(signal.news_signal or 0)}, "insights": [insight_data(insight) for insight in insights]}


@router.get("/insights/{insight_id}/evidence")
def evidence_for_insight(insight_id: str, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    insight = db.get(Insight, insight_id)
    if insight is None:
        raise HTTPException(404, "Insight not found")
    return [{"id": str(item.id), "type": item.evidence_type, "description": item.description, "source": item.source, "reference": item.source_reference, "observed_at": item.observed_at, "freshness": item.freshness_status.value, "verification": item.verification_status.value} for item in insight.evidence]


@router.get("/insights/{insight_id}/trace")
def trace_change(insight_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    insight = db.get(Insight, insight_id)
    if insight is None:
        raise HTTPException(404, "Insight not found")
    signal = insight.change_signal
    return {"observed_facts": {"symbol": signal.symbol, "signals": {"price": float(signal.price_signal or 0), "volume": float(signal.volume_signal or 0), "market": float(signal.market_signal or 0), "sector": float(signal.sector_signal or 0)}}, "detected_signal": {"significance": float(signal.significance_score or 0)}, "relevant_evidence": [{"description": e.description, "verification": e.verification_status.value} for e in insight.evidence], "user_intent": insight.relevance_score.matched_intent if insight.relevance_score else None, "generated_explanation": insight.explanation}
