# MouldShield dashboard

**THE SHARKS · Claudiu Stratulat (T14)**

A tenant dashboard built with HTML, CSS and JavaScript. It shows temperature, humidity, the risk level and the data integrity result, with an English and Romanian interface.

## Open in Visual Studio Code

Choose **File → Open Folder** and select the `dashboard` folder of the repository. Edit the source files and press **Ctrl+S** to save.

## Run the dashboard

Install Python 3.8 or newer, then double-click **START_WINDOWS.bat**. Keep its window open and use the local address it prints, normally [**http://127.0.0.1:8080**](http://127.0.0.1:8080 "http://127.0.0.1:8080/"). Save your changes and refresh the browser. Press **Ctrl+C** in the server window to stop it.

You can also use the VS Code terminal:

```
py -3 run.py
```

On macOS or Linux, use `python3 run.py`. No pip or npm packages are needed to run the dashboard. If Python is missing, the Windows launcher opens the sample-only preview instead.

**START_HERE.html is a generated demo.** To update it after editing the source files, run:

```
py -3 scripts/build_standalone.py
```

## Project files

| File or folder                  | Purpose                                               |
| ------------------------------- | ----------------------------------------------------- |
| `index.html`                    | Dashboard and report structure                        |
| `style.css`                     | Layout, colours and responsive styling                |
| `app.js`                        | Dashboard behaviour and API calls                     |
| `core.js`                       | Reading, risk and integrity logic                     |
| `config.js`                     | API endpoints and refresh settings                    |
| `i18n.js`                       | English and Romanian interface text                   |
| `assets/logo-by-the-sharks.svg` | Team logo                                             |
| `diagrams/T15_use_case.png`     | Use case diagram (T15)                                |
| `diagrams/T15_data_flow.png`    | Level 0 (context) data flow diagram (T15)             |
| `docs/API_INTEGRATION.md`       | Confirmed API formats and integrations still to agree |
| `tests/`                        | Automated JavaScript and Python tests                 |
| `run.py` / `START_WINDOWS.bat`  | Local preview and API proxy                           |

The two diagrams are separate files and are not shown in the dashboard.

## Features

- Temperature, and humidity as a whole percent. The exact value stays in the API data and the CSV export.
- Risk shown with words and icons as well as colour: low up to 60% RH, moderate above 60% up to 70%, high above 70%. These are the same limits as on the device (T04). They are prototype warning levels, not an official HHSRS assessment.
- **EN / RO** interface selector in the top-right corner, which remembers the choice.
- Integrity badge from **GET /verify**: "Data verified", "Tampered", or a neutral state when there is no data or the API cannot be reached.
- Report language: English, Română or Polski. The letter to the landlord is an editable draft and can be printed or saved as PDF from the browser. Nothing is sent automatically.
- Forecast panel and a 24 h / 7 days graph, ready for the back-end endpoints.

Demo mode uses clearly labelled sample data. It does not read the real database and never shows sample data as verified.

## Connect to the back-end

1. Start the FastAPI back-end at [**http://127.0.0.1:8000**](http://127.0.0.1:8000 "http://127.0.0.1:8000/"), following `backend/README.md`.
2. Start this dashboard with **START_WINDOWS.bat** or `py -3 run.py`.
3. Click **Connect to API** in the dashboard. The local server forwards `/api` requests to the back-end.

| Integration                | Status (23 October 2026)                                                         |
| -------------------------- | -------------------------------------------------------------------------------- |
| `GET /readings/latest`     | Working; the reading fields match the dashboard                                  |
| `GET /verify`              | Working; the OK and Tampered responses match the dashboard                       |
| `POST /report`             | Planned (T13); request and response format to agree with Sergiu                  |
| Forecast and 7-day history | Not in the back-end yet (T17); set the routes in `config.js` when they are ready |

The standalone demo cannot connect to the API. Reports, the forecast and the history only work once those back-end endpoints exist. Never put passwords, device certificates, keys or database files in the front-end or on GitHub.

For a different back-end address, use `py -3 run.py --api-url `[`https://YOUR-API-HOST`](https://YOUR-API-HOST "https://your-api-host/") with the real host. Do not put credentials in the URL.

## Tests

JavaScript tests (Node.js needed):

```
node --test tests/core.test.js tests/api.test.js tests/i18n.test.js
```

Local preview and proxy tests:

```
py -3 -m unittest discover -s tests -p "test_*.py" -v
```

There are 31 automated tests (23 JavaScript and 8 Python). The accessibility target is WCAG 2.2 AA. Manual checks (screen reader, zoom, Windows browsers) are still to do as part of T22.
