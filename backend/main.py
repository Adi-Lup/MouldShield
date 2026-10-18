# main.py - simple MouldShield back-end for Sprint 1
# Saves one reading in a SQLite database file

import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel

DB_FILE = "mouldshield.db"

app = FastAPI(title="MouldShield API")


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
    return conn


class Reading(BaseModel):
    # The JSON the device sends (same names as in 8c)
    device_id: str
    timestamp: str
    temperature_c: float
    humidity_pct: float


@app.post("/readings")
def save_reading(reading: Reading):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO readings "
        "(device_id, timestamp, temperature_c, humidity_pct) "
        "VALUES (?, ?, ?, ?)",
        (reading.device_id, reading.timestamp,
         reading.temperature_c, reading.humidity_pct),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"saved": True, "id": new_id}


@app.get("/readings/latest")
def latest_reading():
    conn = get_db()
    row = conn.execute(
        "SELECT id, device_id, timestamp, temperature_c, humidity_pct "
        "FROM readings ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row is None:
        return {"message": "no readings yet"}
    return {
        "id": row[0],
        "device_id": row[1],
        "timestamp": row[2],
        "temperature_c": row[3],
        "humidity_pct": row[4],
    }
