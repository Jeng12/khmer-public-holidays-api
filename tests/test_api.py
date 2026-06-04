"""Tests for the Khmer public holidays API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.storage import HolidayStore

SAMPLE = [
    {
        "id": 1,
        "name_kh": "ទិវាចូលឆ្នាំសាកល",
        "name_en": "International New Year's Day",
        "date": "2026-01-01",
        "type": "fixed",
        "description": "New Year.",
        "is_fixed": True,
        "notes": None,
    },
    {
        "id": 2,
        "name_kh": "ទិវាបុណ្យឯករាជ្យជាតិ",
        "name_en": "Independence Day",
        "date": "2026-11-09",
        "type": "national",
        "description": "Independence from France in 1953.",
        "is_fixed": True,
        "notes": None,
    },
]


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    data_file = tmp_path / "holidays.json"
    data_file.write_text(json.dumps(SAMPLE, ensure_ascii=False), encoding="utf-8")
    store = HolidayStore(data_file=data_file)

    app.dependency_overrides[get_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_returns_all_sorted_by_date(client: TestClient) -> None:
    resp = client.get("/holidays")
    assert resp.status_code == 200
    data = resp.json()
    assert [h["id"] for h in data] == [1, 2]
    assert data[0]["date"] == "2026-01-01"


def test_list_filter_by_type(client: TestClient) -> None:
    resp = client.get("/holidays", params={"type": "national"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name_en"] == "Independence Day"


def test_get_detail(client: TestClient) -> None:
    resp = client.get("/holidays/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name_kh"] == "ទិវាចូលឆ្នាំសាកល"
    assert body["name_en"] == "International New Year's Day"


def test_get_missing_returns_404(client: TestClient) -> None:
    assert client.get("/holidays/999").status_code == 404


def test_create_holiday(client: TestClient) -> None:
    payload = {
        "name_kh": "ទិវាពលកម្មអន្តរជាតិ",
        "name_en": "International Labour Day",
        "date": "2026-05-01",
        "type": "international",
    }
    resp = client.post("/holidays", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 3
    assert body["name_en"] == "International Labour Day"
    assert body["is_fixed"] is True  # default applied


def test_create_rejects_duplicate_date(client: TestClient) -> None:
    payload = {
        "name_kh": "ស្ទួន",
        "name_en": "Duplicate",
        "date": "2026-01-01",
    }
    resp = client.post("/holidays", json=payload)
    assert resp.status_code == 409


def test_create_rejects_blank_name(client: TestClient) -> None:
    payload = {"name_kh": "   ", "name_en": "X", "date": "2026-07-01"}
    resp = client.post("/holidays", json=payload)
    assert resp.status_code == 422


def test_create_rejects_bad_date(client: TestClient) -> None:
    payload = {"name_kh": "ល្អ", "name_en": "Good", "date": "01-01-2026"}
    resp = client.post("/holidays", json=payload)
    assert resp.status_code == 422


def test_update_holiday(client: TestClient) -> None:
    resp = client.patch("/holidays/1", json={"description": "Updated."})
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated."


def test_update_to_duplicate_date_conflicts(client: TestClient) -> None:
    resp = client.patch("/holidays/1", json={"date": "2026-11-09"})
    assert resp.status_code == 409


def test_update_missing_returns_404(client: TestClient) -> None:
    assert client.patch("/holidays/999", json={"notes": "x"}).status_code == 404


def test_delete_holiday(client: TestClient) -> None:
    assert client.delete("/holidays/1").status_code == 204
    assert client.get("/holidays/1").status_code == 404


def test_delete_missing_returns_404(client: TestClient) -> None:
    assert client.delete("/holidays/999").status_code == 404


def test_changes_persist_to_disk(client: TestClient, tmp_path: Path) -> None:
    client.post(
        "/holidays",
        json={"name_kh": "ថ្មី", "name_en": "New", "date": "2026-03-08"},
    )
    saved = json.loads((tmp_path / "holidays.json").read_text(encoding="utf-8"))
    assert any(h["name_en"] == "New" for h in saved)
