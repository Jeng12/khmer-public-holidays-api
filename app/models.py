"""Pydantic data models for Khmer public holidays."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HolidayType(str, Enum):
    """Category of a public holiday."""

    fixed = "fixed"
    national = "national"
    international = "international"
    traditional = "traditional"
    religious = "religious"
    royal = "royal"


class HolidayBase(BaseModel):
    """Fields shared by create, update, and read models."""

    name_kh: str = Field(..., min_length=1, description="Holiday name in Khmer.")
    name_en: str = Field(..., min_length=1, description="Holiday name in English.")
    date: date = Field(..., description="Holiday date in ISO 8601 (YYYY-MM-DD).")
    type: HolidayType = Field(
        default=HolidayType.national, description="Category of the holiday."
    )
    description: Optional[str] = Field(
        default=None, description="Short explanation of the holiday."
    )
    is_fixed: bool = Field(
        default=True,
        description="True if the date is the same every year, False if it is movable.",
    )
    notes: Optional[str] = Field(default=None, description="Any additional notes.")

    @field_validator("name_kh", "name_en")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name fields must not be empty")
        return value


class HolidayCreate(HolidayBase):
    """Payload for creating a holiday."""


class HolidayUpdate(BaseModel):
    """Payload for updating a holiday. All fields are optional."""

    name_kh: Optional[str] = Field(default=None, min_length=1)
    name_en: Optional[str] = Field(default=None, min_length=1)
    date: Optional[date] = None
    type: Optional[HolidayType] = None
    description: Optional[str] = None
    is_fixed: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator("name_kh", "name_en")
    @classmethod
    def _not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("name fields must not be empty")
        return value


class Holiday(HolidayBase):
    """A holiday as stored and returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique holiday identifier.")
