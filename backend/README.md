# Back-end

FastAPI app for MouldShield. Owner: Sergiu (tasks 6, 7, 9, 10, 13, 17).

Sprint 1 version: a simple API on a laptop that saves readings in a SQLite file (`mouldshield.db`). No AWS needed. The full back-end comes in Sprint 2.

## Files

- `main.py`: the API (T06 database, T07 FastAPI back-end)
- `simulator.py`: sends a realistic test reading every 5 seconds (T09)
- `hash_chain.py`: the SHA-256 hash chain that makes the readings tamper-evident (T12, Adrian)
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

- `POST /readings` saves a reading, links it to the one before it, and returns `{"saved": true, "id": ..., "hash": ...}`
- `GET /readings/latest` returns the last saved reading
- `GET /verify` checks the hash chain and returns `OK`, or `Tampered` with the id of the first reading that was changed (T12)

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
