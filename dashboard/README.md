# MouldShield dashboard

**THE SHARKS · Claudiu Stratulat · T14 / T19**

The updated tenant dashboard, mobile page and branded QR code, ready to edit in **Visual Studio Code**. Built with HTML, CSS and JavaScript, with a small Python server for the local preview.

## Open and run

**Release 20261029-t20-t22-fixes:** close any older MouldShield/Python server windows first. Open the repository’s `dashboard` folder in Visual Studio Code and run its launcher. Use the browser address printed by that window; an earlier server may still occupy port 8080.

1. Open the `dashboard` folder in Visual Studio Code, or double-click `MouldShield.code-workspace`.
2. Double-click **START_MOULDSHIELD.bat**. Keep its window open.
3. The dashboard opens at the local address printed in that window, normally `http://127.0.0.1:8080/`.

Python 3.8 or newer and an internet connection are needed for live readings. No pip or npm packages are needed to run the project. The launcher checks for Python automatically. If Python is missing, it opens the clearly labelled sample preview, `START_HERE.html`.

You can also run this in the VS Code terminal:

```text
py -3 run.py
```

On macOS or Linux: `python3 run.py`. Press **Ctrl+C** in the server window to stop it. Save edits with **Ctrl+S** and refresh the browser.

The included VS Code configuration also supports **F5** to open Chrome. The F5 preview uses port 8080; close any existing preview first.

## Live readings and example data

The normal dashboard starts in **live mode**. The local server forwards `/api` requests to the existing team API at `https://d15ad8kcnyn7ke.cloudfront.net/api`. You do not need to start a second backend on your laptop for this configuration. Live readings still depend on the team's API and sensor being available.

- Current readings and data verification refresh every **15 seconds**.
- The seven-day history is downloaded every **5 minutes**. In-flight history requests are not duplicated. A failed history update keeps the previous history and shows a message.
- “Live readings from your sensor” appears beside the reading time. Missing or old readings show a clear waiting or outdated message.
- **See example data** appears discreetly at the bottom of the dashboard.
- Example mode has a large banner that clearly says the data is not real. Use **Connect to live readings** to return to the API.
- Humidity is rounded only on screen; original decimal values remain in the source data and CSV export.
- Risk uses the original humidity value: low up to 60%, moderate above 60% up to 70%, high above 70%. These are project warning bands, not an official HHSRS assessment.

To use a backend running locally instead:

```text
py -3 run.py --api-url http://127.0.0.1:8000
```

Never put passwords, certificates, keys or database files in this front end.

## QR code and mobile page

Click **Open QR code** at the top of the dashboard, or open **MouldShield_QR.html** directly. **MouldShield_QR.png** and **MouldShield_QR.svg** are included for printing and presentations.

The QR contains exactly:

```text
https://d15ad8kcnyn7ke.cloudfront.net/
```

It uses navy rounded dots, blue finder centres, the team logo in the middle, H error correction and a four-module quiet zone. The logo and its white background cover about 7.9% of the data square.

The QR opens the **published site**. It does not open your laptop or automatically publish your local edits. Your phone can use Wi-Fi or mobile data to reach the hosted site.

The included **mobile.html** is also available locally at `http://127.0.0.1:8080/mobile.html`. It always uses live readings, updates every 15 seconds and never silently substitutes example values when the API fails. It includes EN / RO and a link back to the main dashboard. Publishing this page requires uploading it and its source assets to the team's hosting.

## Files

| File or folder | Purpose |
|---|---|
| `index.html`, `style.css`, `app.js` | Main dashboard and report page |
| `core.js`, `config.js`, `i18n.js` | Data handling, settings and English/Romanian text |
| `mobile.html`, `mobile.js`, `phone.css`, `phone-core.js` | Mobile page and editable source |
| `MouldShield_QR.html`, `.png`, `.svg` | Branded QR code pointing to the hosted home page |
| `assets/logo-by-the-sharks.svg` | Team logo |
| `diagrams/T15_use_case.png` | Separate use case diagram |
| `diagrams/T15_data_flow.png` | Separate level 0 context DFD |
| `run.py`, `START_MOULDSHIELD.bat` | Local preview and API proxy |
| `.vscode/`, `MouldShield.code-workspace` | VS Code run settings |
| `tests/`, `../docs/testing/` | Automated checks and their results |

The diagrams are separate files and do not appear inside the dashboard. No level 1 diagram is included.

## Reports and forecast

**T20:** open My report, choose the explanation language, edit the letter and click Download PDF. If saving does not start automatically, use Save PDF. The existing print option remains. See `docs/T20_PDF_REPORT.md`.

**T22:** test plan, results, Lighthouse reports and manual checklist are in the repository-level `../docs/testing/` folder. Manual checks are recorded as PASS based on user confirmation; GitHub issue-linked commits and a teammate review remain for the team Definition of Done.

The report page has English, Romanian and Polish explanation language choices. The selected language is sent to `POST /report`. The editable landlord letter can be downloaded as PDF directly or printed from the browser. Nothing is sent to the landlord automatically.

The forecast and history use the team's `/forecast` and `/readings/history` endpoints. Forecast calculations come from the backend; the page displays them. The 7-day graph shows daily average humidity and the recorded time above 70%.

## Tests

With Node.js installed:

```text
node --test tests/core.test.js tests/api.test.js tests/i18n.test.js tests/t19-update.test.js tests/live-source-ui.test.js tests/release.test.js tests/pdf-report.test.js tests/pdf-flow.test.js
```

Python preview and proxy tests:

```text
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

The package passed **53 JavaScript tests and 19 Python tests**. The real HTTPS API returned successful JSON responses for the latest reading and verification through the local proxy. QR decoding passed 12 size/rotation checks. The full pages were also exercised in Chrome with controlled test data: dashboard startup, EN/RO, 24 h / 7 days, live/demo/live, report source changes, mobile-to-dashboard navigation and the QR page. Cached-script upgrade regression checks passed. Native Windows execution, physical phone scans and final WCAG checks remain to be completed by the team.

## Rebuild generated files

After editing the dashboard source, regenerate its sample-only offline preview:

```text
py -3 scripts/build_standalone.py
```

To regenerate the QR HTML and SVG with the bundled encoder (Node.js required, no npm install):

```text
node scripts/build_qr.js
```

The PNG is a pre-rendered copy of the included QR design.

This package contains the front end and local preview. It does not contain the team's backend, device firmware or credentials, and it does not change GitHub or CloudFront automatically.

PDF export uses bundled jsPDF and DejaVu Sans. Licences are in `vendor/`. Manual PDF save/open checks are recorded as PASS in `../docs/testing/T22_results.md`. This package is ready for you to upload to GitHub; deployment to CloudFront is a separate step.
