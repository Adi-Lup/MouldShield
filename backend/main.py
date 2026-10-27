# main.py - MouldShield back-end API
# Saves the readings in a SQLite database file and gives them back with their risk level

import sqlite3

from datetime import timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from hash_chain import GENESIS_HASH, calculate_hash, verify_chain
from risk import risk_level
from report import router as report_router
from forecast import router as forecast_router
from report_text import TIME_FORMAT, parse_time

DB_FILE = "mouldshield.db"

app = FastAPI(title="MouldShield API")

# T13: POST /report (explanation and letter to the landlord)
app.include_router(report_router)
# T17: GET /forecast (condensation warning for the next 48 hours)
app.include_router(forecast_router)

# Big answers (the 7-day history) are sent compressed, about 10 times smaller
app.add_middleware(GZipMiddleware, minimum_size=1000)


def get_db():
    # Opens the database file and creates the table the first time
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            humidity_pct REAL NOT NULL,
            prev_hash TEXT,
            hash TEXT
        )
        """
    )
    # T17: makes the 7-day history quick to read for one device
    conn.execute(
        "CREATE INDEX IF NOT EXISTS readings_device_time ON readings (device_id, timestamp)"
    )
    return conn


class Reading(BaseModel):
    # The JSON the device sends (same names as in 8c)
    device_id: str
    timestamp: str
    temperature_c: float
    humidity_pct: float


@app.post("/readings", status_code=201)
def save_reading(reading: Reading):
    conn = get_db()
    # T12: lock the database while we read the last hash and save the new reading,
    # so two readings arriving at the same time cannot both link to the same one.
    conn.execute("BEGIN IMMEDIATE")
    last = conn.execute(
        "SELECT hash FROM readings ORDER BY id DESC LIMIT 1"
    ).fetchone()
    prev_hash = last[0] if last else GENESIS_HASH
    new_hash = calculate_hash(prev_hash, reading.device_id, reading.timestamp,
                              reading.temperature_c, reading.humidity_pct)
    cursor = conn.execute(
        "INSERT INTO readings "
        "(device_id, timestamp, temperature_c, humidity_pct, prev_hash, hash) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (reading.device_id, reading.timestamp,
         reading.temperature_c, reading.humidity_pct, prev_hash, new_hash),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"saved": True, "id": new_id, "hash": new_hash,
            "risk": risk_level(reading.humidity_pct)}


@app.get("/readings/latest")
def latest_reading():
    conn = get_db()
    row = conn.execute(
        "SELECT id, device_id, timestamp, temperature_c, humidity_pct "
        "FROM readings ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row is None:
        # 404, because there is no reading to give back yet (action from the 22 Oct stand-up)
        raise HTTPException(status_code=404, detail="no readings yet")
    return {
        "id": row[0],
        "device_id": row[1],
        "timestamp": row[2],
        "temperature_c": row[3],
        "humidity_pct": row[4],
        "risk": risk_level(row[4]),
    }


@app.get("/verify")
def verify():
    # T12: checks the whole hash chain from the first reading to the last.
    # Answers "OK", or "Tampered" with the id of the first reading that was changed.
    conn = get_db()
    rows = conn.execute(
        "SELECT id, device_id, timestamp, temperature_c, humidity_pct, prev_hash, hash "
        "FROM readings ORDER BY id"
    ).fetchall()
    conn.close()
    return verify_chain(rows)


@app.get("/readings/history")
def readings_history():
    # T17: the readings of the last 7 days for the dashboard graph, oldest first.
    # Same device as the last reading, and the exact values, not rounded.
    conn = get_db()
    last = conn.execute(
        "SELECT device_id, timestamp FROM readings ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if last is None:
        conn.close()
        return {"readings": []}
    device_id, newest = last
    since = (parse_time(newest) - timedelta(days=7)).strftime(TIME_FORMAT)
    rows = conn.execute(
        "SELECT id, device_id, timestamp, temperature_c, humidity_pct FROM readings "
        "WHERE device_id = ? AND timestamp > ? ORDER BY timestamp",
        (device_id, since),
    ).fetchall()
    conn.close()
    return {"readings": [
        {"id": r[0], "device_id": r[1], "timestamp": r[2], "temperature_c": r[3], "humidity_pct": r[4]}
        for r in rows
    ]}
