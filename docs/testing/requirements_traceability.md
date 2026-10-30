# MouldShield · Requirements and tests

This table links every user story in `../agile/product_backlog.md` to the tests that show it works. "Automated" means the test runs again every time with `python -m unittest discover tests` or `node --test tests/*.test.js`. "Real system" means the test used the real device or the live server (`system_tests.md`). "Manual" means a person checked it by hand (`T22_manual_checklist.csv`).

Last checked: 29 October 2026. All automated tests pass: 69 back-end (`backend-results.txt`), 53 dashboard JavaScript (`javascript-results.txt`) and 19 dashboard Python (`python-results.txt`).

## User stories

| Story | What it needs | How it was tested | Result |
|---|---|---|---|
| US1 Temperature, humidity and a risk level (Must) | Real readings reach the dashboard, with LOW, MODERATE or HIGH | Automated: `backend/tests/test_risk.py` (4 tests, including 60% and 70% exactly and 70.4% not rounded down), `dashboard/tests/core.test.js` (risk uses the exact value, not the rounded one). Real system: R1 (36 readings in a row), breath test, M2 (median 1.7 s from device to database) | Pass |
| US2 Tamper-evident readings (Must) | A change to an old reading is found | Automated: `backend/tests/test_tamper_detection.py` (13 tests: 9 different kinds of change all found at the right reading, no false alarm, 2 known limits), `dashboard/tests/api.test.js` (Tampered is shown in red). Real system: I1 (reading 3 changed in SQLite, found at reading 3), L1 (3,116 live readings OK) | Pass. Limit: tamper-evident, not tamper-proof |
| US3 Explanation and letter in the tenant's language (Must) | Explanation in English, Romanian or Polish and a letter built only from saved readings, also as a PDF | Automated: `backend/tests/test_report.py` (12 tests, including numbers in the request not being used and the fixed text when Bedrock fails), `dashboard/tests/pdf-report.test.js` and `pdf-flow.test.js` (PDF in all three languages, a failed report never downloads made-up text). Manual: PDF saved and opened on Windows, iPhone and Android | Pass |
| US4 Test readings without the device (Must) | Realistic readings when the device is not connected | Real system: `backend/simulator.py` sent readings to the API during development and is kept as the viva backup (reviewed by Adrian on 18 Oct). No automated test | Pass (manual only) |
| US5 Condensation warning (Must) | A warning before water forms on the coldest wall | Automated: `backend/tests/test_condensation.py` (10 tests, including known dew point values) and `test_forecast.py` (9 tests, Open-Meteo asked at most once in 30 minutes, the location is not sent back) | Pass |
| US6 Photo with a short description (Should) | Upload a photo, keep it private and describe it without a diagnosis | Automated: `backend/tests/test_photos.py` (17 tests, including iPhone HEIC, GPS kept private, a photo over 15 MB refused and the limit of 20 a day). Manual: a real T18 photo included in the PDF report | Pass |
| US7 Live dashboard on a phone with a QR code (Should) | The QR code opens the live mobile page | Automated: `dashboard/tests/t19-update.test.js` (the mobile page is live by default and never shows example readings as real ones). Manual: QR code and page checked on iPhone (Safari) and Android (Chrome) | Pass |

## Other requirements

| Requirement | How it was tested | Result |
|---|---|---|
| Nobody outside can add, change or delete readings | Real system: PUT, DELETE and POST on `/api/readings` from the internet all return 403 (`../security/T21_security_check.md`) | Pass |
| Photos cannot be used to fill the server | Real system: a 16 MB photo returns 413 (`../security/T21_security_check.md`). Automated: `test_photos.py` | Pass |
| No reading is lost during a short Wi-Fi drop | Real system: R2 (19 readings lost before the fix), R3 (0 lost with the offline buffer, chain OK with 131 readings) | Pass for a one-minute drop. Limit: readings are still lost if the device is switched off or the server restarts |
| The dashboard is accessible | Lighthouse accessibility 100 on the dashboard, mobile, report and QR pages (`lighthouse/`). Manual: keyboard, 200% zoom and screen reader | Pass |
