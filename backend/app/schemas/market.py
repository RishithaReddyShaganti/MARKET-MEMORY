import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import FreshnessStatus, VerificationStatus


class ORMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MarketSnapshotResponse(ORMResponse):
    id: uuid.UUID; symbol: str; price: Decimal | None; volume: Decimal | None; market_return: Decimal | None; sector_return: Decimal | None; timestamp: datetime; source: str; freshness_status: FreshnessStatus


class MarketEventResponse(ORMResponse):
    id: uuid.UUID; symbol: str; event_type: str; event_time: datetime; received_at: datetime; source: str; source_event_id: str; payload: dict | None; event_hash: str


class ChangeSignalResponse(ORMResponse):
    id: uuid.UUID; symbol: str; detected_at: datetime; price_signal: Decimal | None; volume_signal: Decimal | None; market_signal: Decimal | None; sector_signal: Decimal | None; historical_signal: Decimal | None; fundamental_signal: Decimal | None; event_signal: Decimal | None; news_signal: Decimal | None; significance_score: Decimal | None


class RelevanceScoreResponse(ORMResponse):
    id: uuid.UUID; change_signal_id: uuid.UUID; watchlist_item_id: uuid.UUID; intent_match_score: Decimal | None; relevance_level: str | None; matched_intent: str | None; reason: str | None


class InsightResponse(ORMResponse):
    id: uuid.UUID; change_signal_id: uuid.UUID; relevance_score_id: uuid.UUID | None; attention_level: str | None; explanation: str | None; confidence: Decimal | None; created_at: datetime; updated_at: datetime


class EvidenceResponse(ORMResponse):
    id: uuid.UUID; insight_id: uuid.UUID; evidence_type: str; description: str; source: str; source_reference: str | None; observed_at: datetime; freshness_status: FreshnessStatus; verification_status: VerificationStatus
