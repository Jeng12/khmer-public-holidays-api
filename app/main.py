"""FastAPI application exposing Khmer public holiday endpoints."""

from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

from .models import Holiday, HolidayCreate, HolidayType, HolidayUpdate
from .storage import DuplicateDateError, HolidayStore

app = FastAPI(
    title="Khmer Public Holidays API",
    description="A small REST API for Cambodian public holidays, with Khmer and English names.",
    version="1.0.0",
)

_store = HolidayStore()


def get_store() -> HolidayStore:
    """Dependency that supplies the holiday store (overridable in tests)."""
    return _store


@app.get("/", tags=["meta"])
def root() -> dict:
    """Friendly landing payload pointing at the docs."""
    return {
        "name": "Khmer Public Holidays API",
        "docs": "/docs",
        "holidays": "/holidays",
    }


@app.get("/holidays", response_model=List[Holiday], tags=["holidays"])
def list_holidays(
    year: Optional[int] = Query(default=None, ge=1, description="Filter by year."),
    type: Optional[HolidayType] = Query(default=None, description="Filter by type."),
    store: HolidayStore = Depends(get_store),
) -> List[Holiday]:
    """List holidays, optionally filtered by year and/or type."""
    holidays = store.list()
    if year is not None:
        holidays = [h for h in holidays if h.date.year == year]
    if type is not None:
        holidays = [h for h in holidays if h.type == type]
    return holidays


@app.get("/holidays/{holiday_id}", response_model=Holiday, tags=["holidays"])
def get_holiday(
    holiday_id: int, store: HolidayStore = Depends(get_store)
) -> Holiday:
    """Return a single holiday by id."""
    holiday = store.get(holiday_id)
    if holiday is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found"
        )
    return holiday


@app.post(
    "/holidays",
    response_model=Holiday,
    status_code=status.HTTP_201_CREATED,
    tags=["holidays"],
)
def create_holiday(
    payload: HolidayCreate, store: HolidayStore = Depends(get_store)
) -> Holiday:
    """Create a new holiday. Rejects duplicate dates."""
    try:
        return store.create(payload)
    except DuplicateDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@app.patch("/holidays/{holiday_id}", response_model=Holiday, tags=["holidays"])
def update_holiday(
    holiday_id: int,
    payload: HolidayUpdate,
    store: HolidayStore = Depends(get_store),
) -> Holiday:
    """Partially update an existing holiday."""
    try:
        updated = store.update(holiday_id, payload)
    except DuplicateDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found"
        )
    return updated


@app.delete(
    "/holidays/{holiday_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["holidays"],
)
def delete_holiday(
    holiday_id: int, store: HolidayStore = Depends(get_store)
) -> None:
    """Delete a holiday by id."""
    if not store.delete(holiday_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found"
        )
