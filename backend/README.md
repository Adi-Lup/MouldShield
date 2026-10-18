# Back-end

FastAPI app for MouldShield. Owner: Sergiu (tasks 6, 7, 9, 10, 13, 17).

Sprint 1 version: a simple API on a laptop that saves readings in a SQLite file (`mouldshield.db`). No AWS needed. The full back-end comes in Sprint 2.

## Files

- `main.py`: the API (T06 database, T07 FastAPI back-end)
- `simulator.py`: sends a realistic test reading every 5 seconds (T09)

## Database (T06)

One table, `readings`, created automatically the first time the API runs:

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key, auto-increment |
| device_id | TEXT | For example `mouldshield-01` or `simulator-01` |
| timestamp | TEXT | UTC time, for example `2026-10-15T10:30:00Z` |
| temperature_c | REAL | Degrees Celsius |
| humidity_pct | REAL | Relative humidity in % |
| prev_hash | TEXT | Empty for now, filled in Sprint 2 (T12) |
| hash | TEXT | Empty for now, filled in Sprint 2 (T12) |

The database file is not committed (it is in `.gitignore`).

## Run it (Windows PowerShell)

Set up once:

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the API:

```
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try it.

- `POST /readings` saves a reading and returns `{"saved": true, "id": ...}`
- `GET /readings/latest` returns the last saved reading

Example reading (the same field names are used on the device and in the database):

```json
{
  "device_id": "mouldshield-01",
  "timestamp": "2026-10-15T10:30:00Z",
  "temperature_c": 20.4,
  "humidity_pct": 63.2
}
```

## Run the simulator

Keep the API running. In a second PowerShell window:

```
cd backend
.venv\Scripts\activate
python simulator.py
```

A new reading is sent every 5 seconds. Stop it with Ctrl + C.
