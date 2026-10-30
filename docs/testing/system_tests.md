# MouldShield · System tests with the real device

These tests used the real M5StickS3 with the ENV III sensor, AWS IoT Core and the back-end, not the simulator. They were done by Adrian between 20 and 28 October 2026. The automated tests are in `backend-results.txt`, `javascript-results.txt` and `python-results.txt`, and the security checks are in `../security/T21_security_check.md`.

The screenshots named under "Evidence" are kept by the team and are not in the repository, because some of them show the AWS account.

## Summary

| ID | Test | Date | Result |
|---|---|---|---|
| R1 | Device to database, one reading every 15 s | 20 Oct | 36 readings saved in a row, none lost |
| R1 | Breath test on the sensor | 20 Oct | 64.2% to 71.0% in one reading, 91.7% after 30 s, all saved |
| I1 | One old reading changed by hand in SQLite | 20 Oct | `Tampered` at the exact reading, OK again after the value was put back |
| M2 | Time from the device to the database | 21 Oct | Median 1.7 s (n = 26), min 1.3 s, max 9.0 s |
| R2 | Phone hotspot turned off three times | 21 Oct | Reconnected by itself 3 out of 3 times, but 19 readings lost |
| R3 | Same test with the offline buffer | 21 Oct | 0 readings lost, chain OK with 131 readings |
| L1 | Hash chain on the live server | 28 Oct | `GET /verify` OK, 3,116 readings checked |

## R1 · Device to database and breath test (20 Oct 2026, 11:48 to 11:58 UK time)

- Set-up: the device on Adrian's phone hotspot, AWS IoT Core (eu-west-2), `backend/mqtt_subscriber.py` and the FastAPI back-end with SQLite on Adrian's laptop.
- Result: readings 1 to 36 were saved in a row, one every 15 seconds, with no reading lost and no API error. One gap was 26 seconds instead of 15; the delay was on the device, because the timestamp comes from the device.
- Breath test: humidity went from 64.2% (10:56:29Z) to 71.0% (10:56:44Z) and 91.7% (10:56:59Z), so the risk level went from MODERATE to HIGH within one reading. Every reading was saved.
- Evidence: `W3_subscriber_saved.png`, `W3_swagger_latest_reading.png`.

## I1 · Tamper test with real readings (20 Oct 2026, 12:52 to 13:01 UK time)

- Set-up: a new empty database, real readings arriving from the device every 15 seconds during the whole test.
- Step 1: `GET /verify` with 10 readings returned OK.
- Step 2: the humidity of reading 3 was changed directly in SQLite, from 66.0% to 40.0%, without touching the hashes. `GET /verify` returned `Tampered`, first_bad_id 3, "reading changed after it was saved".
- Step 3: the value was put back to 66.0%. `GET /verify` returned OK, with 38 readings checked (new readings kept arriving).
- Result: the change was found at the exact reading, with no false alarm before or after.
- The same check is now repeated automatically in `backend/tests/test_tamper_detection.py` (13 tests): the first, a middle and the last reading, the temperature, the time and the device ID, a value changed together with its own hash, a deleted reading and a fake reading. All 9 kinds of change are found at the right reading. Two known limits are also tested: deleting the newest reading, or calculating every hash again after a change, is not found. MouldShield is tamper-evident, not tamper-proof.
- Evidence: `W3_verify_ok.png`, `W3_tamper_change.png`, `W3_verify_tampered.png`, `W3_verify_restored.png`.

## M2 · Speed from the device to the database (21 Oct 2026, 11:31 to 11:42 UK time)

- Method: the subscriber takes the time (UTC) when the API confirms the save and subtracts the timestamp in the reading. This measures the whole path: device, AWS IoT Core, subscriber, `POST /readings`, hash and SQLite.
- Values in seconds (readings 50 to 75): 1.3, 1.4, 9.0, 1.3, 1.3, 1.9, 1.5, 1.5, 1.7, 1.7, 1.8, 1.6, 2.0, 2.6, 1.7, 1.8, 1.9, 1.9, 1.8, 3.4, 1.3, 1.5, 1.8, 1.6, 1.4, 1.4.
- Result: median 1.7 s (n = 26), min 1.3 s, max 9.0 s, mean 2.0 s (1.72 s without the 9.0 s value). The 9.0 s value came just before the hotspot was turned off for R2, and 2.6 s and 3.4 s were the first readings after a reconnect.
- Limits: the device timestamp has whole seconds and both clocks use internet time, so each value is accurate to about 1 s. Readings 15 s apart in the same room are not independent, so the median is given. One session, one network.
- Evidence: `W3_r8_reconnect.png`.

## R2 · Connection drops (21 Oct 2026, 11:32 to 11:42 UK time)

- Method: the phone hotspot was turned off and on three times; the device was not touched.

| Round | Last reading before | Hotspot back on | First reading after | Readings lost |
|---|---|---|---|---|
| 1 | 11:32:40 | 11:35 | 11:35:11 | 9 |
| 2 | 11:36:55 | 11:38 | 11:38:11 | 4 |
| 3 | 11:39:25 | 11:41 | 11:41:18 | 6 |

- Result: the screen showed OFFLINE straight away and the device reconnected by itself within about 20 seconds each time. `GET /verify` afterwards: OK, 87 readings. However, 19 readings were lost in total, because the device did not keep the readings it could not send. This was logged as risk R9 and fixed the same day (R3).
- Also learned: two subscribers with the same client ID disconnect each other from AWS IoT Core in a loop, so only one subscriber may run at a time.
- Evidence: `W3_screen_offline.jpg`, `W3_r8_reconnect.png`, `W3_r8_verify_after.png`.

## R3 · Offline buffer on the device (21 Oct 2026, 12:05 to 12:13 UK time)

- Change: readings that cannot be sent now wait in memory (up to 240 readings, one hour) and are sent oldest first when the connection is back, at most 10 per cycle (commit `3ec219d`).
- Method: hotspot off at 12:08 and on again at 12:09.
- Result: the device console showed "NOT sent" with 1, 2, 3 and 4 readings waiting, then "sent". The four waiting readings were saved as readings 111 to 114, in order and with no gap, followed by reading 115. `GET /verify` afterwards: OK, 131 readings. No reading was lost during a one-minute drop.
- Limits: the waiting readings are lost if the device is switched off, and a reading that reaches the subscriber while the API or the server is restarting (about 25 seconds) is still lost. Tested once, with a short drop.
- Evidence: `W3_r9_buffer_device.png`, `W3_r9_buffer.png`, `W3_r9_verify_after.png`.

## L1 · Hash chain on the live server (28 Oct 2026)

- `GET /verify` on the live EC2 server returned OK with 3,116 readings checked. Recorded in `../security/T21_security_check.md`.
