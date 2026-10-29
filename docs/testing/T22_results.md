# T22 - Test results

**Project:** MouldShield · THE SHARKS  
**Build tested:** `20261029-t20-t22-fixes`  
**Results updated:** 29 October 2026

## Test results

| Check | Result | Evidence |
|---|---|---|
| JavaScript automated tests | PASS - 53 tests | `javascript-results.txt` |
| Python automated tests | PASS - 19 tests | `python-results.txt` |
| Dashboard startup and data-source switching | PASS | `full-app-smoke.json` |
| Live API readings, verification and forecast | PASS - endpoints returned HTTP 200 | `live-get-checks.json` |
| Risk calculation and altered hash-chain detection | PASS | Reference fixtures and Python tests |
| PDF English, Romanian and Polish text and layout | PASS | PDF tests and sample report |
| Edited landlord letter and language handling | PASS | `pdf-flow.test.js` |
| Selected photo in PDF | PASS | `pdf-report.test.js` |
| Chrome report controls | PASS | `chrome-checks.json` |
| Lighthouse: dashboard, mobile, report and QR page | PASS - 100/100 each on the previous visual build; this correction changes copy and test coverage only | `lighthouse/` reports |
| Windows PDF save and open | PASS - manual check reported complete | Manual result confirmed by user |
| iPhone/Safari and Android/Chrome QR and PDF | PASS - manual checks reported complete | Manual result confirmed by user |
| Keyboard, 200% zoom, screen reader and PDF reading order | PASS - manual checks reported complete | Manual result confirmed by user |
| Physical sensor, display/beeps, Wi-Fi/MQTT and API/database reading | PASS - manual check reported complete | Manual result confirmed by user |
| Selected real T18 photo in report | PASS - manual check reported complete | Manual result confirmed by user |

**72 automated tests passed (53 JavaScript and 19 Python).** The Lighthouse scores are automated checks; manual accessibility checks are also recorded above. Manual results reflect the user's confirmation. The checklist does not include device details or screenshots, so attach those separately if the course requires evidence.

## Fixes retested

- PDF export includes the reading time, exact humidity, risk, verification result, selected-language explanation and edited landlord letter.
- Bundled Unicode fonts support Romanian and Polish. Page numbers and a separate letter page are included, and sample data is labelled on every page.
- The report request timeout allows time for the explanation service. A visible Save PDF link remains available if the browser does not start a download automatically.
- The dashboard keeps the live-reading message, clear example-data banner and five-minute history refresh.

## Still required for the team Definition of Done

Upload the files with commits linked to the relevant GitHub issues and ask a teammate to review the T20/T22 evidence. These are collaboration/release steps, not failed manual tests.

## Reflection

I built the PDF report and checked that it keeps the selected language and edited landlord letter. The automated and manual checks passed. The tests helped me find a timeout problem and improve the PDF saving message. I also recorded what the team still needs to do before closing the task.
