# simulator.py - sends realistic test readings to the back-end
# Used when the device is not connected

import random
import time
from datetime import datetime, timezone

import requests

API_URL = "http://127.0.0.1:8000/readings"

humidity = 60.0

while True:
    humidity = max(35.0, min(95.0, humidity + random.uniform(-2, 3)))
    now = datetime.now(timezone.utc)
    reading = {
        "device_id": "simulator-01",
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temperature_c": round(random.uniform(17, 22), 1),
        "humidity_pct": round(humidity, 1),
    }
    answer = requests.post(API_URL, json=reading)
    print(reading, "->", answer.json())
    time.sleep(5)
