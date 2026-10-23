# MouldShield dashboard.

**THE SHARKS · Claudiu Stratulat**

A tenant dashboard built with HTML, CSS and JavaScript. It shows temperature, humidity, risk status and data integrity, with an English/Romanian interface. This is a local project; opening or editing it does not change GitHub.

## Open in Visual Studio Code

Choose **File â†’ Open Folder** and select the **MouldShield** project folder. Edit the source files and press **Ctrl+S** to save.

## Run the editable dashboard

Install Python 3.8 or newer, then double-click **START_WINDOWS.bat**. Keep its window open and use the local address it prints, normally **http://127.0.0.1:8080**. Save source changes and refresh the browser. Press **Ctrl+C** in the server window to stop it.

Alternatively, use the VS Code terminal:

```powershell
py -3 run.py
```

On macOS/Linux, use `python3 run.py`. No pip or npm packages are required to run the dashboard. If Python is missing, the Windows launcher opens the sample-only preview instead.

**START_HERE.html is a generated demo.** To update it after editing the source, run:

```powershell
py -3 scripts/build_standalone.py
```

## Project files

| File or folder | Purpose |
|---|---|
| `index.html` | Dashboard and report structure |
| `style.css` | Layout, colours and responsive styling |
| `app.js` | Dashboard behaviour and API calls |
| `core.js` | Reading, risk and integrity transforms |
| `config.js` | API endpoints and refresh settings |
| `i18n.js` | English/Romanian interface text |
| `assets/logo-by-the-sharks.svg` | Team logo |
| `diagrams/T15_use_case.png` | Original use case diagram |
| `diagrams/T15_data_flow.png` | Original context data flow diagram |
| `docs/API_INTEGRATION.md` | Confirmed API formats and pending integrations |
| `docs/testing/` | T22 test plan, results and Lighthouse evidence |
| `run.py` / `START_WINDOWS.bat` | Local preview and API proxy |

The two original diagrams remain separate files and are not shown in the dashboard.

## Features

- Temperature and whole-percent humidity; original precision stays in API payloads and CSV.
- Risk words and icons alongside colour: low at â‰¤60% RH, moderate at >60â€“70%, high at >70%. These are the team's prototype warning bands, not an HHSRS assessment.
- Top-right **EN / RO** interface selector that remembers the choice.
- Integrity badge from **GET /verify**: Data verified, Tampered, or a neutral unavailable/empty state.
- Report language selection: English, RomÃ¢nÄƒ or Polski; editable draft letter and browser print/save as PDF. Nothing is sent automatically.
- Forecast panel and 24 h / 7 days graph, ready for the team's backend integrations.

Demo mode uses clearly labelled sample data. It does not read the real database or claim that sample data is verified.

## Connect to the team's backend

Reference repository: [Adi-Lup/MouldShield](https://github.com/Adi-Lup/MouldShield). The repository was checked on **23 October 2026**; no GitHub files were changed.

1. Start the team's FastAPI backend at **http://127.0.0.1:8000**, following its `backend/README.md`.
2. Start this dashboard with **START_WINDOWS.bat** or `py -3 run.py`.
3. Click **Connect to API** in the dashboard. The local server forwards `/api` requests to the backend.

| Integration | Current repository status |
|---|---|
| `GET /readings/latest` | Implemented; reading fields match the dashboard |
| `GET /verify` | Implemented; OK/Tampered responses match the dashboard |
| `POST /report` | Planned; agree request and response formats with Sergiu |
| Forecast and history | Routes not present in the checked backend; configure them when supplied |

The standalone demo cannot connect to the API. Live reports, forecasts and history require the missing services; their adapters alone do not make those services available. Keep passwords, device certificates, keys and database files out of the frontend and GitHub.

For a different backend address, use `py -3 run.py --api-url https://YOUR-API-HOST` with the real host. Do not include credentials in the URL.

## Validation

Run JavaScript tests with Node.js installed:

```powershell
node --test tests/core.test.js tests/api.test.js tests/i18n.test.js
```

Run local preview/proxy tests:

```powershell
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

The existing validation includes 31 passing automated tests and 12 Lighthouse accessibility reports scoring 100/100 across desktop/mobile and EN/RO. These audits do not certify full WCAG compliance. Native Windows, screen-reader and manual accessibility checks remain for team review. See `docs/testing/` for evidence and limitations.
