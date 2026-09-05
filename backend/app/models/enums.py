from enum import Enum


class IntentType(str, Enum):
    EARNINGS = "earnings"
    GROWTH = "growth"
    VALUATION = "valuation"
    COMPETITION = "competition"
    CORPORATE_EVENT = "corporate_event"
    LONG_TERM_BUSINESS = "long_term_business"
    EXPLORING = "exploring"
    CUSTOM = "custom"


class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    UNAVAILABLE = "unavailable"
    CONFLICTING = "conflicting"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    CONFLICTING = "conflicting"
