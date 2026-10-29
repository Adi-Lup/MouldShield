"""T22 tests for the tamper check (T12): GET /verify after changing the database by hand.
Each test saves 20 readings through POST /readings in a temporary database, changes
the database directly in SQLite (like someone with access to the file), then asks
GET /verify. The real database is never touched.
Run from the backend folder: python -m unittest discover tests"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import main
from hash_chain import GENESIS_HASH, calculate_hash

READINGS = 20


class TamperDetectionTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.old_db_file = main.DB_FILE
        main.DB_FILE = str(Path(self.folder.name) / "test.db")
        self.client = TestClient(main.app)
        for i in range(READINGS):
            reading = {
                "device_id": "mouldshield-01",
                "timestamp": "2026-10-20T10:%02d:%02dZ" % (48 + i // 4, (i % 4) * 15),
                "temperature_c": round(20.0 + i * 0.1, 1),
                "humidity_pct": round(60.0 + i * 0.5, 1),
            }
            response = self.client.post("/readings", json=reading)
            self.assertEqual(response.status_code, 201)

    def tearDown(self):
        main.DB_FILE = self.old_db_file
        self.folder.cleanup()

    def change(self, sql, values=()):
        # Changes the database directly, outside the API
        conn = sqlite3.connect(main.DB_FILE)
        conn.execute(sql, values)
        conn.commit()
        conn.close()

    def rows(self):
        conn = sqlite3.connect(main.DB_FILE)
        rows = conn.execute(
            "SELECT id, device_id, timestamp, temperature_c, humidity_pct FROM readings ORDER BY id"
        ).fetchall()
        conn.close()
        return rows

    def verify(self):
        return self.client.get("/verify").json()

    def assert_tampered_at(self, reading_id):
        result = self.verify()
        self.assertEqual(result["status"], "Tampered")
        self.assertEqual(result["first_bad_id"], reading_id)
        return result

    # 1. No change: no false alarm
    def test_untouched_chain_is_ok(self):
        self.assertEqual(self.verify(), {"status": "OK", "checked": READINGS})

    # 2 to 4. Humidity changed in the first, a middle and the last reading
    def test_humidity_changed_in_first_reading(self):
        self.change("UPDATE readings SET humidity_pct = 40.0 WHERE id = 1")
        result = self.assert_tampered_at(1)
        self.assertEqual(result["reason"], "reading changed after it was saved")

    def test_humidity_changed_in_middle_reading(self):
        self.change("UPDATE readings SET humidity_pct = 40.0 WHERE id = 10")
        self.assert_tampered_at(10)

    def test_humidity_changed_in_last_reading(self):
        self.change("UPDATE readings SET humidity_pct = 40.0 WHERE id = 20")
        self.assert_tampered_at(20)

    # 5 to 7. Other fields of a reading
    def test_temperature_changed(self):
        self.change("UPDATE readings SET temperature_c = 15.0 WHERE id = 7")
        self.assert_tampered_at(7)

    def test_timestamp_changed(self):
        self.change("UPDATE readings SET timestamp = '2026-10-01T09:00:00Z' WHERE id = 13")
        self.assert_tampered_at(13)

    def test_device_id_changed(self):
        self.change("UPDATE readings SET device_id = 'other-device' WHERE id = 5")
        self.assert_tampered_at(5)

    # 8. The value AND its own hash changed: the link to the next reading breaks
    def test_value_and_own_hash_changed(self):
        _, device, time, temp, _ = self.rows()[9]
        conn = sqlite3.connect(main.DB_FILE)
        prev_hash = conn.execute("SELECT prev_hash FROM readings WHERE id = 10").fetchone()[0]
        conn.close()
        new_hash = calculate_hash(prev_hash, device, time, temp, 40.0)
        self.change("UPDATE readings SET humidity_pct = 40.0, hash = ? WHERE id = 10", (new_hash,))
        result = self.assert_tampered_at(11)
        self.assertEqual(result["reason"], "chain broken between reading 10 and reading 11")

    # 9. A reading in the middle deleted
    def test_middle_reading_deleted(self):
        self.change("DELETE FROM readings WHERE id = 10")
        result = self.assert_tampered_at(11)
        self.assertEqual(result["reason"], "chain broken between reading 9 and reading 11")

    # 10. A reading replaced by a fake one with a correct hash of its own
    def test_reading_replaced_by_fake_one(self):
        conn = sqlite3.connect(main.DB_FILE)
        prev_hash = conn.execute("SELECT hash FROM readings WHERE id = 9").fetchone()[0]
        conn.close()
        fake = ("mouldshield-01", "2026-10-20T10:50:15Z", 20.9, 45.0)
        fake_hash = calculate_hash(prev_hash, *fake)
        self.change("DELETE FROM readings WHERE id = 10")
        self.change(
            "INSERT INTO readings (id, device_id, timestamp, temperature_c, humidity_pct, prev_hash, hash) "
            "VALUES (10, ?, ?, ?, ?, ?, ?)", fake + (prev_hash, fake_hash))
        self.assert_tampered_at(11)

    # 11. The value put back: OK again
    def test_value_put_back_is_ok_again(self):
        original = self.rows()[2][4]
        self.change("UPDATE readings SET humidity_pct = 40.0 WHERE id = 3")
        self.assert_tampered_at(3)
        self.change("UPDATE readings SET humidity_pct = ? WHERE id = 3", (original,))
        self.assertEqual(self.verify(), {"status": "OK", "checked": READINGS})

    # 12 and 13. Known limits (tamper-evident, not tamper-proof): these are NOT detected
    def test_limit_deleting_the_newest_reading_is_not_detected(self):
        self.change("DELETE FROM readings WHERE id = 20")
        self.assertEqual(self.verify(), {"status": "OK", "checked": READINGS - 1})

    def test_limit_recalculating_every_hash_is_not_detected(self):
        self.change("UPDATE readings SET humidity_pct = 40.0 WHERE id = 3")
        prev_hash = GENESIS_HASH
        for row_id, device, time, temp, hum in self.rows():
            new_hash = calculate_hash(prev_hash, device, time, temp, hum)
            self.change("UPDATE readings SET prev_hash = ?, hash = ? WHERE id = ?",
                        (prev_hash, new_hash, row_id))
            prev_hash = new_hash
        self.assertEqual(self.verify(), {"status": "OK", "checked": READINGS})


if __name__ == "__main__":
    unittest.main()
