import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import User, Watchlist, WatchlistItem
from app.schemas.watchlist import WatchlistCreate, WatchlistItemCreate, WatchlistItemUpdate, WatchlistUpdate

DEVELOPMENT_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def get_development_user(db: Session) -> User:
    """Return the deterministic development-only user; this is not authentication."""
    user = db.get(User, DEVELOPMENT_USER_ID)
    if user is None:
        user = User(id=DEVELOPMENT_USER_ID)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def list_watchlists(db: Session, user_id: uuid.UUID) -> list[Watchlist]:
    return list(db.scalars(select(Watchlist).where(Watchlist.user_id == user_id).order_by(Watchlist.created_at)).all())


def get_watchlist(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID) -> Watchlist:
    watchlist = db.scalar(select(Watchlist).where(Watchlist.id == watchlist_id, Watchlist.user_id == user_id))
    if watchlist is None:
        raise NotFoundError("Watchlist not found")
    return watchlist


def create_watchlist(db: Session, user_id: uuid.UUID, payload: WatchlistCreate) -> Watchlist:
    watchlist = Watchlist(user_id=user_id, name=payload.name)
    db.add(watchlist)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError("A watchlist with this name already exists") from error
    db.refresh(watchlist)
    return watchlist


def update_watchlist(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID, payload: WatchlistUpdate) -> Watchlist:
    watchlist = get_watchlist(db, user_id, watchlist_id)
    watchlist.name = payload.name
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError("A watchlist with this name already exists") from error
    db.refresh(watchlist)
    return watchlist


def delete_watchlist(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID) -> None:
    db.delete(get_watchlist(db, user_id, watchlist_id))
    db.commit()


def list_items(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID) -> list[WatchlistItem]:
    get_watchlist(db, user_id, watchlist_id)
    return list(db.scalars(select(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist_id).order_by(WatchlistItem.added_at)).all())


def get_item(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID, item_id: uuid.UUID) -> WatchlistItem:
    get_watchlist(db, user_id, watchlist_id)
    item = db.scalar(select(WatchlistItem).where(WatchlistItem.id == item_id, WatchlistItem.watchlist_id == watchlist_id))
    if item is None:
        raise NotFoundError("Watchlist item not found")
    return item


def add_item(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID, payload: WatchlistItemCreate) -> WatchlistItem:
    get_watchlist(db, user_id, watchlist_id)
    item = WatchlistItem(watchlist_id=watchlist_id, **payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError("This symbol is already in the watchlist") from error
    db.refresh(item)
    return item


def update_item(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID, item_id: uuid.UUID, payload: WatchlistItemUpdate) -> WatchlistItem:
    item = get_item(db, user_id, watchlist_id, item_id)
    item.intent_type = payload.intent_type
    item.intent_text = payload.intent_text
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, user_id: uuid.UUID, watchlist_id: uuid.UUID, item_id: uuid.UUID) -> None:
    db.delete(get_item(db, user_id, watchlist_id, item_id))
    db.commit()
