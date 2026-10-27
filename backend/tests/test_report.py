"""T13 tests for the report (explanation and letter). They use a fake Bedrock client,
so they never call the real AWS, and a temporary database, so they never touch the real one.
Run from the backend folder: python -m unittest discover tests"""

import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import report
import report_text
from hash_chain import GENESIS_HASH, calculate_hash

START = datetime(2026, 10, 20, 12, 0, 0, tzinfo=timezone.utc)
TODAY = datetime(2026, 10, 27, 17, 30, 0, tzinfo=timezone.utc)


class FakeBedrock:
    def __init__(self, answer="Humidity is 72%, which is HIGH risk. Open a window after cooking and keep the room warm."):
        self.calls = 0
        self.answer = answer
        self.fail = False

    def converse(self, modelId, messages, inferenceConfig):
        self.calls += 1
        if self.fail:
            raise RuntimeError("Bedrock is down")
        return {"output": {"message": {"content": [{"text": self.answer}]}}}


def save_readings(db_file, readings):
    # readings: (device_id, datetime, temperature_c, humidity_pct), saved in a valid hash chain
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


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.folder.name, "test.db")
        report.DB_FILE = self.db_file
        self.fake = FakeBedrock()
        report.clients["bedrock"] = self.fake

    def tearDown(self):
        report.clients.clear()
        self.folder.cleanup()

    def week_of_readings(self):
        # A week of readings: one every 15 seconds for an hour each day, 75 % in the
        # middle 30 minutes (so 30 minutes above 70 % a day), and a reading from another device
        readings = []
        for day in range(8):
            for i in range(240):
                moment = START - timedelta(days=1) + timedelta(days=day, seconds=15 * i)
                humidity = 75.0 if 60 <= i < 180 else 62.0
                readings.append(("mouldshield-01", moment, 18.4, humidity))
        readings.append(("simulator-01", START, 20.0, 95.0))
        last = START + timedelta(days=6, hours=5, minutes=20)
        readings.append(("mouldshield-01", last, 18.4, 72.3))
        save_readings(self.db_file, readings)
        return len(readings)

    def test_letter_has_the_numbers_from_the_database(self):
        total = self.week_of_readings()
        result = report.make_report(total, "en", today=TODAY)
        letter = result["letter"]

        self.assertEqual(result["risk"], "HIGH")
        self.assertIn("Request for repair: damp in the [room] at [your address]", letter)
        self.assertIn("27 October 2026", letter)
        self.assertIn("- average humidity over the last 7 days:", letter)
        # 7 days with 30 minutes above 70 %, plus the last reading: about 4 hours
        self.assertIn("- time above 70%: about 4 hours", letter)
        # The 95 % reading is from the simulator, not this device, so it is not the highest
        self.assertIn("- highest reading: 75% on", letter)
        self.assertIn("- last reading: 72% at 18.4 °C on 26 October at 17:20", letter)
        self.assertIn("found all {:,} readings unchanged".format(total), letter)
        self.assertIn("Please reply within 14 days", letter)
        self.assertTrue(letter.endswith("Yours sincerely,\n[Your name]"))

    def test_numbers_in_the_request_are_not_used(self):
        # The route only takes the id; the letter must show what is in the database
        save_readings(self.db_file, [("mouldshield-01", START, 18.0, 55.0)])
        result = report.make_report(1, "en", today=TODAY)
        self.assertEqual(result["risk"], "LOW")
        self.assertIn("- last reading: 55% at 18.0 °C", result["letter"])

    def test_tampered_data_is_not_called_unchanged(self):
        self.week_of_readings()
        conn = sqlite3.connect(self.db_file)
        conn.execute("UPDATE readings SET humidity_pct = 40 WHERE id = 5")
        conn.commit()
        conn.close()
        letter = report.make_report(10, "en", today=TODAY)["letter"]
        self.assertNotIn("unchanged", letter)
        self.assertNotIn("log that shows", letter)

    def test_short_history_says_since(self):
        save_readings(self.db_file, [
            ("mouldshield-01", START, 18.0, 65.0),
            ("mouldshield-01", START + timedelta(days=1), 18.0, 66.0),
        ])
        letter = report.make_report(2, "en", today=TODAY)["letter"]
        self.assertIn("- average humidity since 20 October: 66%", letter)
        self.assertIn("- time above 70%: none", letter)
        self.assertIn("found all 2 readings unchanged", letter)

    def test_ai_explanation_is_saved_and_not_paid_twice(self):
        save_readings(self.db_file, [("mouldshield-01", START, 18.4, 72.0)])
        first = report.make_report(1, "en", today=TODAY)
        second = report.make_report(1, "en", today=TODAY)
        self.assertEqual(first["explanation_source"], "ai")
        self.assertEqual(first["explanation"], second["explanation"])
        self.assertEqual(self.fake.calls, 1)

    def test_fixed_text_when_bedrock_fails(self):
        save_readings(self.db_file, [("mouldshield-01", START, 18.4, 72.0)])
        self.fake.fail = True
        for language, word in (("en", "HIGH"), ("ro", "RIDICAT"), ("pl", "WYSOKIE")):
            result = report.make_report(1, language, today=TODAY)
            self.assertEqual(result["explanation_source"], "fixed")
            self.assertIn(word, result["explanation"])
            self.assertIn("72%", result["explanation"])

    def test_fixed_text_when_the_answer_is_not_plain(self):
        save_readings(self.db_file, [("mouldshield-01", START, 18.4, 65.0)])
        self.fake.answer = "Great question! Here is your explanation."
        result = report.make_report(1, "en", today=TODAY)
        self.assertEqual(result["explanation_source"], "fixed")
        self.assertIn("MODERATE", result["explanation"])

    def test_daily_limit_on_bedrock(self):
        save_readings(self.db_file, [("mouldshield-01", START + timedelta(minutes=i), 18.0, 65.0)
                                     for i in range(report.MAX_AI_PER_24H + 2)])
        for reading_id in range(1, report.MAX_AI_PER_24H + 3):
            result = report.make_report(reading_id, "en", today=TODAY)
        self.assertEqual(self.fake.calls, report.MAX_AI_PER_24H)
        self.assertEqual(result["explanation_source"], "fixed")

    def test_errors(self):
        with self.assertRaises(report.ReportError) as empty_database:
            report.make_report(1, "en")
        self.assertEqual(empty_database.exception.status, 404)
        save_readings(self.db_file, [("mouldshield-01", START, 18.0, 65.0)])
        with self.assertRaises(report.ReportError) as wrong_language:
            report.make_report(1, "de")
        self.assertEqual(wrong_language.exception.status, 422)
        with self.assertRaises(report.ReportError) as missing:
            report.make_report(99, "en")
        self.assertEqual(missing.exception.status, 404)


class CleanAnswerTest(unittest.TestCase):
    def test_plain_text_is_kept(self):
        text = "Humidity is 65%, which is MODERATE risk. Open a window after a shower."
        self.assertEqual(report_text.clean_answer(text), text)

    def test_markdown_and_long_dashes_are_removed(self):
        text = "**Humidity is 65%** — MODERATE risk. Open a window after a shower."
        self.assertEqual(report_text.clean_answer(text),
                         "Humidity is 65%, MODERATE risk. Open a window after a shower.")

    def test_bad_answers_are_refused(self):
        for text in (None, "", "Too short.", "Wow! Humidity is 65% and that is a lot of water.", "x" * 800):
            self.assertIsNone(report_text.clean_answer(text), text)


if __name__ == "__main__":
    unittest.main()
