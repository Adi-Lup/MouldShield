# main.py - MouldShield back-end API
# Saves the readings in a SQLite database file

import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from hash_chain import GENESIS_HASH, calculate_hash, verify_chain

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
    return {"saved": True, "id": new_id, "hash": new_hash}


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
