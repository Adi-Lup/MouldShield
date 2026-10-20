# Back-end

FastAPI app for MouldShield. Owner: Sergiu (tasks 6, 7, 9, 10, 13, 17).

Sprint 1 version: a simple API on a laptop that saves readings in a SQLite file (`mouldshield.db`). No AWS needed. The full back-end comes in Sprint 2.

## Files

- `main.py`: the API (T06 database, T07 FastAPI back-end)
- `simulator.py`: sends a realistic test reading every 5 seconds (T09)
- `mqtt_subscriber.py`: brings the real device readings from AWS IoT Core into the API (T27, Adrian)

## Database (T06)

One table, `readings`, created automatically the first time the API runs:

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key, auto-increment |
| device_id | TEXT | For example `mouldshield-01` or `simulator-01` |
| timestamp | TEXT | UTC time, for example `2026-10-15T10:30:00Z` |
| temperature_c | REAL | Degrees Celsius |
| humidity_pct | REAL | Relative humidity in % |
| prev_hash | TEXT | Empty for now, filled in Sprint 2 (T12) |
| hash | TEXT | Empty for now, filled in Sprint 2 (T12) |

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

- `POST /readings` saves a reading and returns `{"saved": true, "id": ...}`
- `GET /readings/latest` returns the last saved reading

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
