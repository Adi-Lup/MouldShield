# forecast.py - T17: GET /forecast, the condensation warning for the next 48 hours
#
# The server asks Open-Meteo for the outside temperature in London (our device has no
# GPS), takes the last indoor reading from our database, and uses condensation.py to
# decide if condensation is likely. The answer is in the format the dashboard expects
# (dashboard/docs/API_INTEGRATION.md).
#
# The dashboard asks every 15 seconds, so we keep the Open-Meteo answer for 30 minutes
# and only ask again after that. Weather data by Open-Meteo.com (CC BY 4.0).

import os
import sqlite3
import time
from datetime import datetime, timezone

import requests
from fastapi import APIRouter

from condensation import HORIZON_HOURS, assess, tonight_minimum
from report_text import LONDON

DB_FILE = "mouldshield.db"
LATITUDE = float(os.environ.get("MOULDSHIELD_LATITUDE", "51.5072"))
LONGITUDE = float(os.environ.get("MOULDSHIELD_LONGITUDE", "-0.1276"))
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

KEEP_SECONDS = 30 * 60        # keep a good answer for 30 minutes
RETRY_SECONDS = 5 * 60        # after a failure, wait 5 minutes before asking again

router = APIRouter()

# The last Open-Meteo answer: {"at": time.time(), "weather": {...}} or {"at": ..., "error": "..."}
saved = {}


def fetch_weather():
    # Asks Open-Meteo. The tests replace this function, so they never call the internet.
    answer = requests.get(OPEN_METEO_URL, params={
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,weather_code",
        "hourly": "temperature_2m",
        "daily": "temperature_2m_max",
        "timezone": "Europe/London",
        "forecast_days": 3,
    }, timeout=10)
    answer.raise_for_status()
    return answer.json()


def read_weather(raw):
    # Takes only what we need from the Open-Meteo answer
    hours = []
    for moment, temp in zip(raw["hourly"]["time"], raw["hourly"]["temperature_2m"]):
        if temp is not None:
            hours.append((datetime.fromisoformat(moment).replace(tzinfo=LONDON), float(temp)))
    return {
        "now_c": float(raw["current"]["temperature_2m"]),
        "weather_code": int(raw["current"]["weather_code"]),
        "tomorrow_c": float(raw["daily"]["temperature_2m_max"][1]),
        "hours": hours,
    }


def weather():
    now = time.time()
    if saved:
        age = now - saved["at"]
        if "weather" in saved and age < KEEP_SECONDS:
            return saved["weather"]
        if "error" in saved and age < RETRY_SECONDS:
            raise RuntimeError(saved["error"])
    try:
        result = read_weather(fetch_weather())
    except Exception:
        saved.clear()
        saved.update({"at": now, "error": "the weather forecast is not available right now"})
        raise RuntimeError(saved["error"])
    saved.clear()
    saved.update({"at": now, "weather": result, "updated_at": datetime.now(timezone.utc)})
    return result


def last_indoor_reading():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute(
            "SELECT id, timestamp, temperature_c, humidity_pct FROM readings ORDER BY id DESC LIMIT 1"
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()


def unavailable(reason):
    return {"available": False, "reason": reason}


def make_forecast(now=None):
    reading = last_indoor_reading()
    if reading is None:
        return unavailable("there is no indoor reading yet")
    reading_id, taken, inside_c, inside_humidity = reading

    try:
        outside = weather()
    except RuntimeError as error:
        return unavailable(str(error))

    now_local = (now or datetime.now(timezone.utc)).astimezone(LONDON)
    try:
        result = assess(inside_c, inside_humidity, outside["hours"], now_local)
    except ValueError:
        return unavailable("the weather forecast does not cover the next 48 hours")
    tonight = tonight_minimum(outside["hours"], now_local)

    return {
        "available": True,
        "condensation": {
            "warning": result["warning"],
            "horizon_hours": HORIZON_HOURS,
            "level": result["level"],
            "advice": result["advice"],
            "dew_point_c": result["dew_point_c"],
            "coldest_surface_c": result["coldest_surface_c"],
        },
        "outside": {
            "now_c": round(outside["now_c"]),
            "tonight_min_c": round(tonight if tonight is not None else outside["now_c"]),
            "tomorrow_c": round(outside["tomorrow_c"]),
        },
        "weather_code": outside["weather_code"],
        "indoor_reading": {"id": reading_id, "timestamp": taken,
                           "temperature_c": inside_c, "humidity_pct": inside_humidity},
        "updated_at": saved["updated_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Weather data by Open-Meteo.com",
    }


@router.get("/forecast")
def get_forecast():
    return make_forecast()
