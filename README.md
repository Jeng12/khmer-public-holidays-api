# Khmer Public Holidays API

**🌐 Live:** https://khmer-public-holidays-api.vercel.app — docs at
[`/docs`](https://khmer-public-holidays-api.vercel.app/docs) ·
holidays at [`/holidays`](https://khmer-public-holidays-api.vercel.app/holidays)

A small REST API for Cambodian public holidays, built with **FastAPI**. Each
holiday carries both a Khmer (`name_kh`) and an English (`name_en`) name. Data
is stored in a static JSON file (`data/holidays.json`) and changes are persisted
back to it.

## Project layout

```
Khmer_Public_Holiday/
├── app/
│   ├── main.py        # FastAPI app and routes
│   ├── models.py      # Pydantic models + validation
│   └── storage.py     # JSON-file CRUD store
├── data/
│   └── holidays.json  # Seed data (2026 Cambodian public holidays)
├── tests/
│   └── test_api.py    # pytest test suite
├── requirements.txt
└── README.md
```

## Setup

Requires **Python 3.9+**. (Python is not currently installed on this machine —
install it from https://www.python.org/downloads/ and tick *"Add to PATH"*.)

```powershell
# from the project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the API

```powershell
uvicorn app.main:app --reload
```

Then open:

- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs
- Holiday list: http://127.0.0.1:8000/holidays

## Run the tests

```powershell
pytest
```

## Data model

| Field         | Type    | Required | Notes                                            |
|---------------|---------|----------|--------------------------------------------------|
| `id`          | int     | auto     | Assigned by the API.                             |
| `name_kh`     | string  | yes      | Khmer name, non-empty.                           |
| `name_en`     | string  | yes      | English name, non-empty.                         |
| `date`        | date    | yes      | ISO 8601 `YYYY-MM-DD`. Unique across holidays.   |
| `type`        | enum    | no       | `fixed`, `national`, `international`, `traditional`, `religious`, `royal`. Default `national`. |
| `description` | string  | no       | Short explanation.                               |
| `is_fixed`    | bool    | no       | `true` if the date is the same every year. Default `true`. |
| `notes`       | string  | no       | Extra notes (e.g. multi-day festivals).          |

## Endpoints

| Method   | Path               | Description                                  |
|----------|--------------------|----------------------------------------------|
| `GET`    | `/holidays`        | List holidays. Query: `year`, `type`.        |
| `GET`    | `/holidays/{id}`   | Get one holiday.                             |
| `POST`   | `/holidays`        | Create a holiday (`201`).                    |
| `PATCH`  | `/holidays/{id}`   | Partially update a holiday.                  |
| `DELETE` | `/holidays/{id}`   | Delete a holiday (`204`).                    |

### Examples

List all holidays in 2026:

```bash
curl http://127.0.0.1:8000/holidays?year=2026
```

Get one holiday:

```json
GET /holidays/2
{
  "id": 2,
  "name_kh": "ទិវាជ័យជម្នះលើរបបប្រល័យពូជសាសន៍",
  "name_en": "Victory over Genocide Day",
  "date": "2026-01-07",
  "type": "national",
  "description": "Commemorates the end of the Khmer Rouge regime in 1979.",
  "is_fixed": true,
  "notes": null
}
```

Create a holiday:

```bash
curl -X POST http://127.0.0.1:8000/holidays \
  -H "Content-Type: application/json" \
  -d '{
        "name_kh": "ទិវាពលកម្មអន្តរជាតិ",
        "name_en": "International Labour Day",
        "date": "2026-05-01",
        "type": "international"
      }'
```

### Status codes

| Code  | Meaning                                              |
|-------|------------------------------------------------------|
| `200` | OK (list / detail / update).                         |
| `201` | Created.                                             |
| `204` | Deleted, no content.                                 |
| `404` | Holiday not found.                                   |
| `409` | A holiday already exists on that date.               |
| `422` | Validation error (bad date, empty name, etc.).       |

## Notes on the data

- Fixed-date holidays (e.g. Independence Day, 9 November) have `is_fixed: true`.
- Movable holidays that follow the lunar calendar — Khmer New Year, Visak Bochea,
  Pchum Ben, the Water Festival, the Royal Ploughing Ceremony — have
  `is_fixed: false`; the seed dates are the **2026** observances and should be
  reviewed each year against the official Royal Government calendar.
