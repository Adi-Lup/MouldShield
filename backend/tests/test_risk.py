"""T10 tests for the risk level. Plain Python, no server needed.
Run from the backend folder: python -m unittest discover tests"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from risk import risk_level


class RiskLevelTest(unittest.TestCase):
    def test_low(self):
        for humidity in (0, 35.0, 59.9, 60, 60.0):
            self.assertEqual(risk_level(humidity), "LOW", humidity)

    def test_moderate(self):
        for humidity in (60.1, 65, 69.9, 70, 70.0):
            self.assertEqual(risk_level(humidity), "MODERATE", humidity)

    def test_high(self):
        for humidity in (70.1, 70.4, 85, 100):
            self.assertEqual(risk_level(humidity), "HIGH", humidity)

    def test_exact_value_not_rounded(self):
        # The screen shows 70 % for 70.4 %, but the risk uses the exact value
        self.assertEqual(risk_level(70.4), "HIGH")
        self.assertEqual(risk_level(60.4), "MODERATE")


if __name__ == "__main__":
    unittest.main()
