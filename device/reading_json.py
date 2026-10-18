# reading_json.py - builds the reading the device sends
# The field names must be the same on the device, in the API and in the database


def make_reading(temp, hum, timestamp):
    # Builds the message the device sends to AWS and to POST /readings
    return {
        "device_id": "mouldshield-01",
        "timestamp": timestamp,  # UTC time, from the device clock
        "temperature_c": round(temp, 1),
        "humidity_pct": round(hum, 1),
    }
