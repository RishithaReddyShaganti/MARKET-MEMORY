import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FreshnessStatus, IntentType, VerificationStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    watchlists: Mapped[list["Watchlist"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Watchlist(Base):
    __tablename__ = "watchlists"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_watchlists_user_name"), Index("ix_watchlists_user_id", "user_id"))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user: Mapped[User] = relationship(back_populates="watchlists")
    items: Mapped[list["WatchlistItem"]] = relationship(back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("watchlist_id", "symbol", name="uq_watchlist_items_watchlist_symbol"), Index("ix_watchlist_items_watchlist_id", "watchlist_id"))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    watchlist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    intent_type: Mapped[IntentType] = mapped_column(SqlEnum(IntentType, native_enum=False, length=32), nullable=False)
    intent_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    watchlist: Mapped[Watchlist] = relationship(back_populates="items")
    relevance_scores: Mapped[list["RelevanceScore"]] = relationship(back_populates="watchlist_item")


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"
    __table_args__ = (Index("ix_market_snapshots_symbol_timestamp", "symbol", "timestamp"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    volume: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    market_return: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    sector_return: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    freshness_status: Mapped[FreshnessStatus] = mapped_column(SqlEnum(FreshnessStatus, native_enum=False, length=16), nullable=False)


class MarketEvent(Base):
    __tablename__ = "market_events"
    __table_args__ = (UniqueConstraint("source", "source_event_id", name="uq_market_events_source_event_id"), Index("ix_market_events_symbol_event_time", "symbol", "event_time"), UniqueConstraint("event_hash", name="uq_market_events_event_hash"))

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class ChangeSignal(Base):
    __tablename__ = "change_signals"
    __table_args__ = (Index("ix_change_signals_symbol_detected_at", "symbol", "detected_at"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    price_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    volume_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    market_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    sector_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    historical_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    fundamental_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    event_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    news_signal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    significance_score: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    relevance_scores: Mapped[list["RelevanceScore"]] = relationship(back_populates="change_signal", cascade="all, delete-orphan")
    insights: Mapped[list["Insight"]] = relationship(back_populates="change_signal", cascade="all, delete-orphan")


class RelevanceScore(Base):
    __tablename__ = "relevance_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    change_signal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("change_signals.id", ondelete="CASCADE"), nullable=False)
    watchlist_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("watchlist_items.id", ondelete="CASCADE"), nullable=False)
    intent_match_score: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    relevance_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    matched_intent: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_signal: Mapped[ChangeSignal] = relationship(back_populates="relevance_scores")
    watchlist_item: Mapped[WatchlistItem] = relationship(back_populates="relevance_scores")
    insights: Mapped[list["Insight"]] = relationship(back_populates="relevance_score")


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    change_signal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("change_signals.id", ondelete="CASCADE"), nullable=False)
    relevance_score_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("relevance_scores.id", ondelete="SET NULL"), nullable=True)
    attention_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    change_signal: Mapped[ChangeSignal] = relationship(back_populates="insights")
    relevance_score: Mapped[RelevanceScore | None] = relationship(back_populates="insights")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="insight", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    insight_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("insights.id", ondelete="CASCADE"), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    freshness_status: Mapped[FreshnessStatus] = mapped_column(SqlEnum(FreshnessStatus, native_enum=False, length=16), nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(SqlEnum(VerificationStatus, native_enum=False, length=16), nullable=False)
    insight: Mapped[Insight] = relationship(back_populates="evidence")
