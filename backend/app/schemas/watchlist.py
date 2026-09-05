import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import IntentType


class WatchlistCreate(BaseModel):
    name: str = Field(max_length=120)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Watchlist name cannot be blank")
        return value


class WatchlistUpdate(WatchlistCreate):
    pass


class WatchlistItemCreate(BaseModel):
    symbol: str = Field(max_length=32)
    company_name: str = Field(min_length=1, max_length=255)
    intent_type: IntentType
    intent_text: str | None = Field(default=None, max_length=2000)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("Symbol cannot be blank")
        return value

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Company name cannot be blank")
        return value

    @field_validator("intent_text")
    @classmethod
    def normalize_intent_text(cls, value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None

    @model_validator(mode="after")
    def custom_intent_needs_text(self) -> "WatchlistItemCreate":
        if self.intent_type is IntentType.CUSTOM and not self.intent_text:
            raise ValueError("Custom intent requires intent_text")
        return self


class WatchlistItemUpdate(BaseModel):
    intent_type: IntentType
    intent_text: str | None = Field(default=None, max_length=2000)

    @field_validator("intent_text")
    @classmethod
    def normalize_intent_text(cls, value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None

    @model_validator(mode="after")
    def custom_intent_needs_text(self) -> "WatchlistItemUpdate":
        if self.intent_type is IntentType.CUSTOM and not self.intent_text:
            raise ValueError("Custom intent requires intent_text")
        return self


class WatchlistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    watchlist_id: uuid.UUID
    symbol: str
    company_name: str
    intent_type: IntentType
    intent_text: str | None
    added_at: datetime
    last_checked_at: datetime | None


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
