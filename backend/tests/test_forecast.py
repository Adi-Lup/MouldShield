"""T17 tests for GET /forecast and GET /readings/history. They use a fake Open-Meteo, so they
never call the internet, and a temporary database, so they never touch the real one.
Run from the backend folder: python -m unittest discover tests"""

import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import forecast
import main
from hash_chain import GENESIS_HASH, calculate_hash

NOW = datetime(2026, 10, 27, 18, 30, tzinfo=timezone.utc)


def open_meteo(night_low=0.0):
    # Same shape as the Open-Meteo answer: hourly times in London time, without the zone
    start = datetime(2026, 10, 27, 0, 0)
    times, temps = [], []
    for i in range(72):
        moment = start + timedelta(hours=i)
        times.append(moment.strftime("%Y-%m-%dT%H:%M"))
        temps.append(night_low if moment.hour < 8 else 11.0)
    return {
        "current": {"time": "2026-10-27T18:30", "temperature_2m": 9.4, "weather_code": 61},
        "hourly": {"time": times, "temperature_2m": temps},
        "daily": {"time": ["2026-10-27", "2026-10-28", "2026-10-29"],
                  "temperature_2m_max": [12.0, 10.2, 11.0]},
    }


def save_readings(db_file, readings):
    conn = sqlite3.connect(db_file)
    conn.execute(
        "CREATE TABLE readings (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT NOT NULL, "
        "timestamp TEXT NOT NULL, temperature_c REAL NOT NULL, humidity_pct REAL NOT NULL, "
        "prev_hash TEXT, hash TEXT)")
    prev = GENESIS_HASH
    for device, moment, temp, hum in readings:
        ts = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
        new = calculate_hash(prev, device, ts, temp, hum)
        conn.execute(
            "INSERT INTO readings (device_id, timestamp, temperature_c, humidity_pct, prev_hash, hash) "
            "VALUES (?, ?, ?, ?, ?, ?)", (device, ts, temp, hum, prev, new))
        prev = new
    conn.commit()
    conn.close()


class ForecastTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.folder.name, "test.db")
        forecast.DB_FILE = self.db_file
        main.DB_FILE = self.db_file
        forecast.saved.clear()
        self.calls = 0
        self.answer = open_meteo()
        self.fail = False

        def fake_fetch():
            self.calls += 1
            if self.fail:
                raise ConnectionError("no internet")
            return self.answer
        forecast.fetch_weather = fake_fetch

    def tearDown(self):
        forecast.saved.clear()
        self.folder.cleanup()

    def test_answer_in_the_dashboard_format(self):
        save_readings(self.db_file, [("mouldshield-01", NOW, 20.0, 75.0)])
        result = forecast.make_forecast(now=NOW)
        self.assertTrue(result["available"])
        self.assertEqual(result["condensation"]["warning"], "High condensation risk tonight")
        self.assertEqual(result["condensation"]["horizon_hours"], 48)
        self.assertEqual(result["outside"], {"now_c": 9, "tonight_min_c": 0, "tomorrow_c": 10})
        self.assertEqual(result["weather_code"], 61)
        self.assertTrue(result["updated_at"].endswith("Z"))
        self.assertEqual(result["indoor_reading"]["humidity_pct"], 75.0)

    def test_uses_the_last_reading(self):
        save_readings(self.db_file, [("mouldshield-01", NOW - timedelta(minutes=1), 20.0, 75.0),
                                     ("mouldshield-01", NOW, 20.0, 45.0)])
        result = forecast.make_forecast(now=NOW)
        self.assertEqual(result["condensation"]["level"], "LOW")

    def test_open_meteo_is_asked_once_in_30_minutes(self):
        save_readings(self.db_file, [("mouldshield-01", NOW, 20.0, 60.0)])
        for _ in range(10):
            forecast.make_forecast(now=NOW)
        self.assertEqual(self.calls, 1)

    def test_no_weather(self):
        save_readings(self.db_file, [("mouldshield-01", NOW, 20.0, 60.0)])
        self.fail = True
        result = forecast.make_forecast(now=NOW)
        self.assertFalse(result["available"])
        self.assertIn("not available", result["reason"])
        # It does not ask again straight away after a failure
        forecast.make_forecast(now=NOW)
        self.assertEqual(self.calls, 1)

    def test_no_reading(self):
        result = forecast.make_forecast(now=NOW)
        self.assertEqual(result, {"available": False, "reason": "there is no indoor reading yet"})
        self.assertEqual(self.calls, 0)

    def test_location_is_not_sent_back(self):
        save_readings(self.db_file, [("mouldshield-01", NOW, 20.0, 60.0)])
        text = str(forecast.make_forecast(now=NOW))
        self.assertNotIn(str(forecast.LATITUDE), text)
        self.assertNotIn(str(forecast.LONGITUDE), text)


class HistoryTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        main.DB_FILE = os.path.join(self.folder.name, "test.db")
        main.history_cache.clear()

    def tearDown(self):
        self.folder.cleanup()

    def test_last_seven_days_of_one_device_oldest_first(self):
        readings = [("mouldshield-01", NOW - timedelta(days=8), 18.0, 60.0)]
        readings += [("mouldshield-01", NOW - timedelta(days=d), 18.0, 60.0 + d) for d in (6, 3, 1)]
        readings += [("simulator-01", NOW - timedelta(hours=2), 20.0, 90.0)]
        readings += [("mouldshield-01", NOW, 18.4, 72.3)]
        save_readings(main.DB_FILE, readings)
        rows = main.readings_history()["readings"]
        self.assertEqual([r["humidity_pct"] for r in rows], [66.0, 63.0, 61.0, 72.3])
        self.assertTrue(all(r["device_id"] == "mouldshield-01" for r in rows))

    def test_empty(self):
        self.assertEqual(main.readings_history(), {"readings": []})

    def test_answer_is_kept_for_one_minute(self):
        save_readings(main.DB_FILE, [("mouldshield-01", NOW - timedelta(hours=1), 18.0, 60.0)])
        self.assertEqual(len(main.readings_history()["readings"]), 1)
        conn = sqlite3.connect(main.DB_FILE)
        conn.execute("INSERT INTO readings (device_id, timestamp, temperature_c, humidity_pct) "
                     "VALUES ('mouldshield-01', ?, 18.1, 61.0)", (NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),))
        conn.commit()
        conn.close()
        # Within the minute: the same answer, the database is not read again
        self.assertEqual(len(main.readings_history()["readings"]), 1)
        # After the minute: the new reading is there
        at, answer = main.history_cache[main.DB_FILE]
        main.history_cache[main.DB_FILE] = (at - 61, answer)
        self.assertEqual(len(main.readings_history()["readings"]), 2)


if __name__ == "__main__":
    unittest.main()
