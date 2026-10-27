"""T17 tests for the condensation calculation. Plain Python, no server needed.
Run from the backend folder: python -m unittest discover tests"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from condensation import assess, dew_point, surface_temperature, tonight_end, tonight_minimum

LONDON = ZoneInfo("Europe/London")
NOW = datetime(2026, 10, 27, 18, 30, tzinfo=LONDON)


def forecast(night_low, day_high=12.0):
    # 48 hours: cold at night (00:00 to 08:00), warmer in the day
    hours = []
    start = NOW.replace(minute=0)
    for i in range(49):
        moment = start + timedelta(hours=i)
        temp = night_low if moment.hour < 8 else day_high
        hours.append((moment, temp))
    return hours


class DewPointTest(unittest.TestCase):
    def test_known_values(self):
        # Checked against published dew point tables (within 0.2 C)
        self.assertAlmostEqual(dew_point(20, 60), 12.0, delta=0.2)
        self.assertAlmostEqual(dew_point(20, 70), 14.4, delta=0.2)
        self.assertAlmostEqual(dew_point(18, 80), 14.4, delta=0.2)

    def test_surface(self):
        # fRsi 0.75: a quarter of the way from inside to outside
        self.assertEqual(surface_temperature(20, 4), 16.0)


class AssessTest(unittest.TestCase):
    def test_high_tonight(self):
        # 20 C and 75 %: dew point 15.4 C. Outside 0 C: surface 15 C, below the dew point
        result = assess(20, 75, forecast(night_low=0), NOW)
        self.assertEqual(result["level"], "HIGH")
        self.assertEqual(result["warning"], "High condensation risk tonight")

    def test_some_risk_tonight(self):
        # 20 C and 70 %: dew point 14.4 C. Outside 4 C: surface 16 C, 1.6 C above it
        result = assess(20, 70, forecast(night_low=4), NOW)
        self.assertEqual(result["level"], "MODERATE")
        self.assertEqual(result["warning"], "Some condensation risk tonight on cold windows")

    def test_low(self):
        # 20 C and 50 %: dew point 9.3 C. Outside 6 C: surface 16.5 C, far above it
        result = assess(20, 50, forecast(night_low=6), NOW)
        self.assertEqual(result["level"], "LOW")
        self.assertEqual(result["warning"], "Low condensation risk in the next 48 hours")

    def test_later_when_tonight_is_mild(self):
        hours = forecast(night_low=10)
        # Only the second night is cold
        hours = [(t, 0.0 if t > NOW + timedelta(hours=24) and t.hour < 8 else temp) for t, temp in hours]
        result = assess(20, 75, hours, NOW)
        self.assertEqual(result["level"], "HIGH")
        self.assertEqual(result["warning"], "High condensation risk in the next 48 hours")

    def test_no_forecast(self):
        with self.assertRaises(ValueError):
            assess(20, 60, [], NOW)


class TonightTest(unittest.TestCase):
    def test_tonight_ends_at_nine_tomorrow(self):
        self.assertEqual(tonight_end(NOW), datetime(2026, 10, 28, 9, 0, tzinfo=LONDON))

    def test_early_morning_ends_at_nine_today(self):
        early = datetime(2026, 10, 28, 5, 0, tzinfo=LONDON)
        self.assertEqual(tonight_end(early), datetime(2026, 10, 28, 9, 0, tzinfo=LONDON))

    def test_tonight_minimum(self):
        self.assertEqual(tonight_minimum(forecast(night_low=3), NOW), 3)


if __name__ == "__main__":
    unittest.main()
