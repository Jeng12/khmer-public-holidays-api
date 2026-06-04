"""JSON-file backed storage for holidays with CRUD operations."""

from __future__ import annotations

import json
import os
import shutil
import threading
from datetime import date
from pathlib import Path
from typing import List, Optional

from .models import Holiday, HolidayCreate, HolidayUpdate

# The bundled, read-only seed data shipped with the app (root/data/holidays.json).
SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "holidays.json"

# The file the app actually reads from and writes to.
#  - HOLIDAYS_DATA_FILE, if set, always wins.
#  - On Vercel (which sets VERCEL=1 and has a read-only filesystem) we use
#    /tmp/holidays.json; the seed is copied there on first use.
#  - Otherwise we use the bundled file so local edits persist in the repo.
def _resolve_data_file() -> Path:
    explicit = os.environ.get("HOLIDAYS_DATA_FILE")
    if explicit:
        return Path(explicit)
    if os.environ.get("VERCEL"):
        return Path("/tmp/holidays.json")
    return SEED_FILE


DATA_FILE = _resolve_data_file()


class DuplicateDateError(ValueError):
    """Raised when a holiday with the same date already exists."""


class HolidayStore:
    """Loads holidays from a JSON file and persists changes back to it."""

    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self._data_file = data_file
        self._lock = threading.Lock()
        self._holidays: List[Holiday] = []
        self.reload()

    # ----- persistence helpers -------------------------------------------
    def reload(self) -> None:
        """Load holidays from disk.

        If the writable data file does not exist yet but a seed file does, copy
        the seed into place first (used on read-only hosts pointing at /tmp).
        """
        if not self._data_file.exists():
            if self._data_file != SEED_FILE and SEED_FILE.exists():
                self._data_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(SEED_FILE, self._data_file)
            else:
                self._holidays = []
                return
        raw = json.loads(self._data_file.read_text(encoding="utf-8"))
        self._holidays = [Holiday(**item) for item in raw]

    def _save(self) -> None:
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        payload = [h.model_dump(mode="json") for h in self._holidays]
        self._data_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _next_id(self) -> int:
        return max((h.id for h in self._holidays), default=0) + 1

    def _date_taken(self, value: date, exclude_id: Optional[int] = None) -> bool:
        return any(
            h.date == value and h.id != exclude_id for h in self._holidays
        )

    # ----- public API ----------------------------------------------------
    def list(self) -> List[Holiday]:
        return sorted(self._holidays, key=lambda h: h.date)

    def get(self, holiday_id: int) -> Optional[Holiday]:
        return next((h for h in self._holidays if h.id == holiday_id), None)

    def create(self, payload: HolidayCreate) -> Holiday:
        with self._lock:
            if self._date_taken(payload.date):
                raise DuplicateDateError(
                    f"A holiday already exists on {payload.date.isoformat()}"
                )
            holiday = Holiday(id=self._next_id(), **payload.model_dump())
            self._holidays.append(holiday)
            self._save()
            return holiday

    def update(self, holiday_id: int, payload: HolidayUpdate) -> Optional[Holiday]:
        with self._lock:
            existing = self.get(holiday_id)
            if existing is None:
                return None
            changes = payload.model_dump(exclude_unset=True)
            new_date = changes.get("date", existing.date)
            if self._date_taken(new_date, exclude_id=holiday_id):
                raise DuplicateDateError(
                    f"A holiday already exists on {new_date.isoformat()}"
                )
            updated = existing.model_copy(update=changes)
            index = self._holidays.index(existing)
            self._holidays[index] = updated
            self._save()
            return updated

    def delete(self, holiday_id: int) -> bool:
        with self._lock:
            existing = self.get(holiday_id)
            if existing is None:
                return False
            self._holidays.remove(existing)
            self._save()
            return True
