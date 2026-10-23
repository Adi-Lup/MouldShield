# MouldShield — Visual Studio Code project

THE SHARKS · Claudiu Stratulat

Your dashboard code and separate system diagram files in one editable project. This is a browser dashboard written in HTML, CSS and JavaScript. The optional local preview uses Python 3. No pip or npm packages are required to run it.

## Start here

1. Right-click the ZIP and choose **Extract All**. Do not run files inside the ZIP.
2. Open the extracted **MouldShield** folder.
3. Double-click **START_HERE.html** for an immediate, self-contained demo in Chrome or Edge. No Python, npm, extension or internet connection is required for this preview. It includes your logo and the EN / RO interface. All system diagram files are kept separately in `diagrams/`.
4. To edit the project, open this folder in **Visual Studio Code**. Edit `index.html`, `style.css` or `app.js` and save with **Ctrl+S**.
5. For the editable multi-file version and API connection, double-click **START_WINDOWS.bat**. It detects Python 3.8+ and starts the local server. Open the exact address printed in its window if the browser does not open. Keep that window open while using the dashboard; **Ctrl+C** stops it.
6. Refresh the browser after saving your changes. If you want your changes in the single-file demo too, run `py scripts/build_standalone.py` to rebuild `START_HERE.html`.

If Python is unavailable, the Windows launcher opens the sample-only single-file preview. Live API mode requires the local server and the team's back-end. Browser-local draft storage may depend on your browser's local-file rules.

### VS Code shortcuts and other platforms

- **Ctrl+Shift+B** starts the included preview task. Click its printed address.
- **F5** starts the preview on port 8080 and launches Chrome using the included configuration. Chrome and Python must be installed. Close any previous preview on 8080 before using F5.
- Windows terminal: `py -3 run.py`. If the launcher is unavailable but Python is installed, use `python run.py`.
- macOS/Linux terminal: `python3 run.py`.
- A normal launch automatically tries the next free port if 8080 is busy. F5 uses a fixed port so Chrome opens the correct server.
- A visible startup message identifies missing JavaScript files instead of leaving a blank page. Send its exact text if startup fails.

## What to edit

| File / folder | Purpose |
|---|---|
| `index.html` | Dashboard structure, labels and report sections |
| `style.css` | Colours, fonts, spacing and responsive layout |
| `app.js` | Rendering, history, CSV export, report and diagram switching |
| `core.js` / `config.js` | Tested transforms and API settings |
| `i18n.js` | English/Romanian interface labels and accessible names |
| `diagrams/T15_use_case.png` | Your exact supplied UML use case image |
| `diagrams/T15_data_flow.png` | Your exact supplied context data flow image |
| `diagrams/T15_data_flow_level1.png` / `.svg` | Added Level 1 diagram: PNG plus editable SVG |
| `scripts/create_level1.py` | Standard-library source that regenerates the Level 1 SVG |
| `START_HERE.html` | Self-contained demo; rebuild after editing source files |
| `START_WINDOWS.bat` / `run.py` | Local preview launcher and API proxy |
| `scripts/build_standalone.py` | Rebuild the single-file demo without extra packages |
| `docs/API_INTEGRATION.md` | Back-end contracts and pending integrations |
| `.vscode/` | Preview task and Chrome launch configuration |

Your two supplied PNGs are preserved unchanged. The added Level 1 diagram is available as PNG and editable SVG; its scope and flows are explained in `docs/T15_diagrams.md`. They describe the proposed full system; device authentication, photo analysis and delivery to a landlord are back-end workflows and are not simulated as working live services in this front end. The report can be edited, printed or saved as PDF; it is never automatically sent.

## Updated requirements

- The supplied team logo is in `assets/logo-by-the-sharks.svg`.
- The top-right EN / RO control replaces the mode/profile label, changes the interface language and remembers the choice. It sets the report language default; the separate report selector can still choose Polski.
- System diagrams are kept in the `diagrams/` folder only. They are not a dashboard page and are not embedded in the single-file preview.
- Humidity is shown as a whole percent. Original-precision data is retained in payloads and CSV.
- Live integrity uses the real `GET /verify` response: green Data verified, red Tampered, neutral for errors/empty data.
- The report page includes English, Română and Polski. In live mode the selected language is sent to POST /report; the interface follows the top-right EN / RO choice.
- The forecast panel displays T17's warning and outside temperatures (now, tonight's minimum, tomorrow), with weather words and a code-based icon.
- The graph switches between 24 h and seven daily bars, with averages, hours strictly above 70%, and a coverage table.
- Weather motion lasts at most five seconds once per page opening. No lightning flashing; reduced motion is supported.
- Main text/status colours meet the tested 7:1 target. Keyboard focus, risk words/icons and a larger type scale are included.

## Connect the real back-end

1. Keep the team's FastAPI app running at **http://127.0.0.1:8000** using its own instructions.
2. Start this dashboard with **`py run.py`**. It uses **http://127.0.0.1:8080** so the ports do not conflict.
3. Click **Connect to API**. The local server proxies `/api` to the back-end; `/readings/latest` and `/verify` match the repository's existing code.
4. For a different API base, run `py run.py --api-url https://YOUR-API-HOST` with the real host.
5. Configure the exact history and T17 endpoint paths in `config.js` when Sergiu supplies them. T13's request/response schema also needs agreement. See `docs/API_INTEGRATION.md`.

The retrieved team repository still marked T13 as planned and had no T17/history route. Their display adapters are implemented, but a working live service must be supplied before they can pass end-to-end testing. Demo mode remains explicitly labelled and never claims real verification.

## Tests and accessibility

With Node.js installed, run:

```bash
node --test tests/core.test.js tests/api.test.js tests/i18n.test.js
```

Local preview/proxy fixture tests:

```bash
py -m unittest discover -s tests -p "test_*.py" -v
```

All 31 automated cases (23 JavaScript and 8 Python) passed during preparation, including selected text contrast ratios from 8.78:1 to 12.74:1. The complete test plan and honest results are in `docs/testing/`.

**Lighthouse accessibility audit completed:** all three pages scored **100/100** at desktop 1440×1000 and mobile 390×844 sizes, with no failed automated audits or run warnings. Both EN and RO were checked, giving 12 reports. Reports are in `docs/testing/lighthouse/`; results and remaining manual checks are in T22. The run used Lighthouse 13.5.0 with headless Chromium 153 on Linux. A score is not a full WCAG conformance claim; screen-reader, zoom and native Windows checks remain for the team review.

To repeat with your installed Chrome (Node.js required only for this optional audit):

```bash
npm install --no-save lighthouse@13.5.0
node scripts/run_lighthouse.mjs
```

The script starts and stops its own local dashboard server and writes twelve HTML/JSON report pairs. `--python python` selects that command if `py` is not available on Windows. None of these audit dependencies are required to run the dashboard.

## Main editable files

`index.html` is the interface; `style.css` is the layout; `app.js` handles rendering and API calls; `core.js` holds tested transforms; `config.js` holds endpoints. `run.py` is the local server/proxy. The two supplied diagrams and the added Level 1 diagram are in the separate `diagrams/` folder. Open the PNG or SVG files directly; there is no diagrams page in the dashboard.

No pip/npm packages are needed to run the front end. Node.js is only needed for its automated tests. No extra packages are needed to run the dashboard or regenerate the Level 1 SVG. The included Level 1 PNG is already rendered.
