# Back-end

FastAPI app for MouldShield. Owner: Sergiu (tasks 6, 7, 9, 10, 13, 17).

The API saves the readings in a SQLite file (`mouldshield.db`). On our own computers it runs without AWS. On the EC2 server it runs through `server.py` (T16).

## Files

- `main.py`: the API (T06 database, T07 FastAPI back-end)
- `simulator.py`: sends a realistic test reading every 5 seconds (T09)
- `hash_chain.py`: the SHA-256 hash chain that makes the readings tamper-evident (T12, Adrian)
- `mqtt_subscriber.py`: brings the real device readings from AWS IoT Core into the API (T27, Adrian)
- `risk.py`: the risk level of a reading, LOW, MODERATE or HIGH (T10)
- `report.py` and `report_text.py`: `POST /report`, the explanation and the letter to the landlord (T13)
- `forecast.py` and `condensation.py`: `GET /forecast`, the condensation warning for the next 48 hours (T17)
- `photos.py`: `POST /photos` and `GET /photos`, the photo evidence with an AI description (T18, Adrian)
- `server.py`: how the back-end runs on the EC2 server: the API under `/api`, the dashboard from the same address, read only from outside, and the link preview (T16, Adrian)

## Database (T06)

One table, `readings`, created automatically the first time the API runs:

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key, auto-increment |
| device_id | TEXT | For example `mouldshield-01` or `simulator-01` |
| timestamp | TEXT | UTC time, for example `2026-10-15T10:30:00Z` |
| temperature_c | REAL | Degrees Celsius |
| humidity_pct | REAL | Relative humidity in % |
| prev_hash | TEXT | Hash of the reading before it (T12); 64 zeros for the first reading |
| hash | TEXT | SHA-256 of `prev_hash` and this reading (T12) |

The database file is not committed (it is in `.gitignore`).

## Run it (Windows PowerShell)

Set up once:

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start the API:

```
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try it.

- `POST /readings` saves a reading, links it to the one before it, and answers `201` with `{"saved": true, "id": ..., "hash": ..., "risk": ...}`
- `GET /readings/latest` returns the last saved reading with its risk level, or `404` with `no readings yet` when the database is empty
- `GET /verify` checks the hash chain and returns `OK`, or `Tampered` with the id of the first reading that was changed (T12)
- `POST /report` returns the explanation and the letter to the landlord for one reading (T13)
- `GET /forecast` returns the condensation warning for the next 48 hours and the outside temperatures (T17)
- `GET /readings/history` returns the readings of the last 7 days for the dashboard graph (T17)

Example reading (the same field names are used on the device and in the database):

```json
{
  "device_id": "mouldshield-01",
  "timestamp": "2026-10-15T10:30:00Z",
  "temperature_c": 20.4,
  "humidity_pct": 63.2
}
```

## Run the simulator

Keep the API running. In a second PowerShell window:

```
cd backend
.venv\Scripts\activate
python simulator.py
```

A new reading is sent every 5 seconds. Stop it with Ctrl + C.

## Run the MQTT subscriber (T27)

The device sends its readings to AWS IoT Core, not straight to the API. `mqtt_subscriber.py` connects to AWS IoT Core, receives each reading and sends it to `POST /readings`, so the real readings end up in the database:

```
device -> AWS IoT Core (MQTT over TLS) -> mqtt_subscriber.py -> POST /readings -> SQLite
```

It has its own certificate and its own IoT policy (`mouldshield-subscriber-policy`). The policy only allows Connect (as `mouldshield-subscriber`), Subscribe and Receive on `mouldshield/mouldshield-01/readings`. It has no Publish, so the subscriber certificate cannot be used to send fake readings, and the device certificate cannot be used to read them.

The certificate files are not in the repository. They stay in `C:\Users\<you>\Projects\mouldshield-certs` (`AmazonRootCA1.pem`, `subscriber-cert.pem.crt`, `subscriber-private.pem.key`). At the moment only Adrian has them.

Keep the API running. In a second PowerShell window:

```
cd backend
.venv\Scripts\activate
python mqtt_subscriber.py
```

It should print `Connect result: Success` and `Subscription accepted by AWS`, then one `Saved ...` line every 15 seconds while the device is on. Stop it with Ctrl + C.

Negative test (least privilege): `python mqtt_subscriber.py mouldshield/other-device/readings` asks for a topic that is not in the policy. AWS accepts the connection but closes it as soon as the subscription is requested.

Tested on 20 October 2026 with the real device: 36 readings saved in a row, one every 15 seconds, including a breath test (64.2% to 91.7%), and the last reading read back with `GET /readings/latest` in Swagger. The negative test was refused by AWS as expected.

When the back-end runs on AWS (T16), only the API address changes, with the `MOULDSHIELD_API_URL` setting. The code stays the same.

## Hash chain (T12)

Every saved reading is linked to the one before it. `hash_chain.py` calculates a SHA-256 hash from the hash of the previous reading and the reading itself (device, time, temperature, humidity), and `POST /readings` saves both `prev_hash` and `hash`. The first reading is linked to 64 zeros.

`GET /verify` goes through all readings in order, calculates every hash again and compares it with the saved one. If an old reading was changed in the database, the hashes no longer match and it answers `Tampered` with the id where the chain breaks.

Readings are only ever added. There is no endpoint to change or delete a reading, on purpose.

Limitation: the chain is tamper-evident, not tamper-proof. Someone with full access to the database could change a reading and calculate all the hashes after it again, or delete the newest readings. Anchoring the hashes outside the server (for example S3 Object Lock) is future work.

A database made before T12 has readings without hashes, so `GET /verify` answers `Tampered` at reading 1. Delete `mouldshield.db` and start again.

## Risk level (T10)

`risk.py` gives every reading a risk level, with the limits the team agreed at the Sprint 1 review:

| Humidity | Risk |
| --- | --- |
| 60% or less | LOW |
| above 60%, up to 70% | MODERATE |
| above 70% | HIGH |

It uses the exact humidity saved in the database, the same as the dashboard. The device rounds the humidity before it chooses the colour, so for a reading just above a limit, for example 70.3%, the device shows MODERATE and the API and the dashboard say HIGH.

`POST /readings` and `GET /readings/latest` both return the level as `risk`.

## Report: explanation and letter (T13)

The dashboard sends the id of a reading and a language:

```json
{"id": 131, "language": "ro"}
```

It also sends the reading itself, but the API only uses the id and reads the reading from the database, so a letter can never show numbers that are not in our data.

The answer:

```json
{
  "explanation": "Umiditatea este 72%, adică risc RIDICAT. ...",
  "explanation_source": "ai",
  "letter": "[Your name]\n[Your address]\n...",
  "risk": "HIGH",
  "reading_id": 131
}
```

- `explanation`: two or three sentences in English (`en`), Romanian (`ro`) or Polish (`pl`), written by Claude Haiku 4.5 on Amazon Bedrock from the numbers only (no personal data is sent). Each one is saved, so changing the language back and forth does not call Bedrock again.
- If Bedrock is not available (for example on our own computers without AWS), the answer is not plain text, or the limit of 50 calls in 24 hours is reached, the explanation is a fixed text in the same language and `explanation_source` is `fixed`. The report always works.
- `letter`: in English, filled in from the database: the average humidity over the 7 days up to the reading (or since the first reading, if there is less than a week), the time above 70%, the highest reading, the reading itself, and the result of the hash chain check. The sentence about the readings being unchanged is only added when `GET /verify` would answer `OK`. The parts in [brackets] are for the tenant to fill in.
- The letter only describes the readings, asks the landlord to look at the room and asks for a reply within 10 working days. It does not say there is damp or mould, because the sensor measures humidity, not damp. It only says the readings are higher than expected when they are above 60% or went above 70% in the week.
- The 10 working days is a request, not a legal deadline. Awaab's Law sets 10 working days to investigate a damp or mould hazard, but in England it only covers social housing (since 27 October 2025), so the letter does not quote it.
- `404` if the reading does not exist, `422` if the language is not `en`, `ro` or `pl`.

On the EC2 server `POST /api/report` is open from outside (`server.py`), like the photo upload. It saves no readings, and the Bedrock limit stops it being used to spend our credit.

## Condensation forecast (T17)

`GET /forecast` warns the tenant before condensation happens (US5). It takes the last indoor reading from our database and the outside temperature for the next 48 hours from Open-Meteo, and answers in the format the dashboard expects:

```json
{
  "available": true,
  "condensation": {
    "warning": "High condensation risk tonight",
    "horizon_hours": 48,
    "level": "HIGH",
    "advice": "Keep the room heated and open a window for a few minutes after cooking or a shower. ...",
    "dew_point_c": 15.4,
    "coldest_surface_c": 15.0
  },
  "outside": {"now_c": 9, "tonight_min_c": 0, "tomorrow_c": 10},
  "weather_code": 61,
  "indoor_reading": {"id": 131, "timestamp": "2026-10-27T18:30:00Z", "temperature_c": 20.0, "humidity_pct": 75.0},
  "updated_at": "2026-10-27T18:30:05Z",
  "source": "Weather data by Open-Meteo.com"
}
```

How the warning is worked out (`condensation.py`):

1. The dew point of the room, from the last indoor temperature and humidity (Magnus formula). Below this temperature, the air leaves water on a surface.
2. The temperature of the coldest inside surface, from the coldest outside temperature in the next 48 hours: `surface = outside + 0.75 x (inside - outside)`. 0.75 is the temperature factor fRsi that UK guidance (BRE IP1/06) asks a wall to reach to avoid mould.
3. HIGH if that surface is at or below the dew point, MODERATE if it is within 2 °C of it (windows and corners are often colder than a wall), LOW otherwise. "Tonight" means until 09:00 the next morning.

We assume the room stays at the last indoor reading, so this is an estimate for a warning, not a measurement.

The location is London (our device has no GPS). It can be changed on the server with `MOULDSHIELD_LATITUDE` and `MOULDSHIELD_LONGITUDE`, and it is never sent back by the API. The dashboard asks every 15 seconds, so the server keeps the Open-Meteo answer for 30 minutes (and waits 5 minutes after a failure), which keeps us far below the free limit. If there is no indoor reading or no weather data, the answer is `{"available": false, "reason": "..."}`.

`GET /readings/history` returns `{"readings": [...]}`: the readings of the last 7 days (up to the newest one) from the same device as the newest reading, oldest first, with the exact values. A week at one reading every 15 seconds is about 40,000 readings, so big answers are sent compressed (gzip) and an index on `device_id` and `timestamp` keeps the query quick.

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).

## Tests

From the `backend` folder:

```
python -m unittest discover tests
```

`test_risk.py`, `test_report.py`, `test_condensation.py` and `test_forecast.py` use a temporary database, a fake Bedrock and a fake Open-Meteo, so they never touch the real data, AWS or the internet. `test_photos.py` uses a fake S3 and a fake Bedrock, `test_link_preview.py` checks the link preview tags and image, and `test_tamper_detection.py` changes a temporary database by hand in 13 different ways and checks what `GET /verify` finds. On 29 October 2026 all 69 tests pass (results in `docs/testing/backend-results.txt`).
