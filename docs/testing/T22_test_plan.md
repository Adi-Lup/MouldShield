# T22 - Test plan

**Project:** MouldShield, THE SHARKS
**Owner:** Claudiu Stratulat
**Release:** 20261028-t20-t22
**Date:** 28 October 2026

## Goal

Check the dashboard, mobile page and PDF report against the project requirements. Record what passed and what still needs a real device, phone or teammate. T19 is already reported ready by Claudiu.

## Safe test setup

- Use fixture readings for failure, tampering and sample-data tests. Never change the real database to test tampering.
- The automated Python proxy tests use a local fixture server. The backend risk and hash-chain checks use read-only reference copies of the team's pure functions. They do not run AWS services.
- Use only clearly labelled example reports for public test evidence. Do not use personal addresses, tenant photos, passwords or certificates.
- Live smoke checks use GET only. No real report-generation, photo-upload, landlord-message or database-write requests were made.

## Test cases

| ID | Test | Expected result | Evidence |
|---|---|---|---|
| 01 | Start the newly extracted project | Dashboard opens; no missing event targets or stale scripts | release tests, preview tests, clean ZIP run |
| 02 | Read latest, verify and forecast endpoints | HTTP 200 JSON with expected field names | live-get-checks.json |
| 03 | Check 60%, 60.1%, 70% and 70.4% | LOW, MODERATE, MODERATE, HIGH; round only for display | core and backend reference tests |
| 04 | Change a copy of a hash-chain reading or link | First changed row is reported as Tampered | test_backend_reference.py |
| 05 | Use demo, empty chain or unavailable verification | Samples remain labelled; no false Data verified badge | API, phone and PDF tests |
| 06 | Select English, Romanian or Polish explanation | API request contains the selected language and reading ID | API and PDF flow tests |
| 07 | Generate a PDF in all three languages | Correct Unicode text, reading, risk, explanation and letter | PDF tests and rendered example reports |
| 08 | Export a long letter | Pages continue; no content is cut off | PDF pagination tests |
| 09 | Edit the letter before export | Edited text is used; no automatic landlord message | PDF flow test and Chrome UI check |
| 10 | Change language while the report request is pending | Old response cannot produce a PDF in the wrong language | PDF flow test |
| 11 | Simulate explanation failure | Clear error; no made-up explanation is exported | PDF flow test |
| 12 | Simulate missing verification | PDF says unavailable/neutral, not Data verified | PDF flow test |
| 13 | Add selected clean photo evidence | Only selected report images and visible descriptions are included | PDF image fixture test; real T18 integration still manual |
| 14 | Check 15-second current data / 5-minute history | Current values refresh normally; no duplicate full-history request | history and phone tests |
| 15 | Run Lighthouse on dashboard, report, mobile and QR | No automated accessibility failures | Lighthouse HTML/JSON reports |
| 16 | Open on Windows and save the PDF | PDF exists and opens; fonts, final letter and page ends are correct | Manual checklist |
| 17 | Use keyboard, zoom and a screen reader | Controls usable; focus visible; report understandable | Manual checklist |
| 18 | Physical sensor and AWS path | Readings change after a real sensor test and reach the database/API | Manual checklist |
| 19 | iPhone/Android PDF and QR use | HTTPS link opens; PDF can be saved/opened | Manual checklist |

## Run the automated checks

From the project folder, with Node.js installed:

```text
node --test tests/core.test.js tests/api.test.js tests/i18n.test.js tests/live-source-ui.test.js tests/t19-update.test.js tests/release.test.js tests/pdf-report.test.js tests/pdf-flow.test.js
```

Python:

```text
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

On macOS/Linux use `python3` instead of `py -3`. No npm or pip install is needed for these shipped tests or for running the dashboard. Lighthouse was run as a separate development tool, not a dashboard dependency.

## Definition of Done

The team backlog requires code/documents on GitHub, passing tests, one teammate's review and commits linked to the issue. The manual checks are recorded as PASS based on the user’s confirmation. Attach device details and screenshots if required by the course. T22 still needs issue-linked GitHub commits and a teammate review before the team Definition of Done.
