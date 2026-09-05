import uuid
from collections.abc import Callable
from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.watchlist import WatchlistCreate, WatchlistItemCreate, WatchlistItemResponse, WatchlistItemUpdate, WatchlistResponse, WatchlistUpdate
from app.services import watchlists as service

router = APIRouter(prefix="/watchlists", tags=["watchlists"])
T = TypeVar("T")


def for_development_user(db: Session) -> uuid.UUID:
    """Resolve the temporary development user; replace with auth in a future milestone."""
    return service.get_development_user(db).id


def translate_errors(action: Callable[[], T]) -> T:
    try:
        return action()
    except service.NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except service.ConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def create_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)) -> WatchlistResponse:
    return translate_errors(lambda: service.create_watchlist(db, for_development_user(db), payload))


@router.get("", response_model=list[WatchlistResponse])
def get_watchlists(db: Session = Depends(get_db)) -> list[WatchlistResponse]:
    return service.list_watchlists(db, for_development_user(db))


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_one_watchlist(watchlist_id: uuid.UUID, db: Session = Depends(get_db)) -> WatchlistResponse:
    return translate_errors(lambda: service.get_watchlist(db, for_development_user(db), watchlist_id))


@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
def rename_watchlist(watchlist_id: uuid.UUID, payload: WatchlistUpdate, db: Session = Depends(get_db)) -> WatchlistResponse:
    return translate_errors(lambda: service.update_watchlist(db, for_development_user(db), watchlist_id, payload))


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist(watchlist_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    translate_errors(lambda: service.delete_watchlist(db, for_development_user(db), watchlist_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(watchlist_id: uuid.UUID, payload: WatchlistItemCreate, db: Session = Depends(get_db)) -> WatchlistItemResponse:
    return translate_errors(lambda: service.add_item(db, for_development_user(db), watchlist_id, payload))


@router.get("/{watchlist_id}/items", response_model=list[WatchlistItemResponse])
def get_items(watchlist_id: uuid.UUID, db: Session = Depends(get_db)) -> list[WatchlistItemResponse]:
    return translate_errors(lambda: service.list_items(db, for_development_user(db), watchlist_id))


@router.patch("/{watchlist_id}/items/{item_id}", response_model=WatchlistItemResponse)
def edit_item(watchlist_id: uuid.UUID, item_id: uuid.UUID, payload: WatchlistItemUpdate, db: Session = Depends(get_db)) -> WatchlistItemResponse:
    return translate_errors(lambda: service.update_item(db, for_development_user(db), watchlist_id, item_id, payload))


@router.delete("/{watchlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(watchlist_id: uuid.UUID, item_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    translate_errors(lambda: service.delete_item(db, for_development_user(db), watchlist_id, item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
