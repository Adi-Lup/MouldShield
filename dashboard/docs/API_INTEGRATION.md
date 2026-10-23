# Dashboard integration — 23 October 2026

## Confirmed in the team repository

Repository: Adi-Lup/MouldShield, main branch retrieved on 23 October 2026.

`GET /readings/latest` returns `id`, `device_id`, `timestamp`, `temperature_c`, `humidity_pct`, or `{ "message": "no readings yet" }`.

`GET /verify` returns:

```json
{"status":"OK","checked":131}
```

or:

```json
{"status":"Tampered","first_bad_id":17,"reason":"reading changed after it was saved","checked":16}
```

The dashboard calls this endpoint, shows green **Data verified** only for OK with a positive checked count, and red **Tampered** for a Tampered response. Empty chains, errors, invalid responses and timeouts are neutral. This is tamper-evident integrity, not proof that measurements or property conditions are accurate.

## Front-end-only rounding

`Math.round` is used at display time. `humidity_pct` remains unchanged in memory, API request bodies and CSV. The dashboard never writes rounded values to the database. Risk uses the exact number, so a displayed 70% can be high if the original reading was 70.4%.

## T13 — agree this contract with Sergiu

The repository lists `POST /report` as planned; no request model was present in the retrieved main.py. The adapter currently sends:

```json
{"id":9,"device_id":"mouldshield-01","timestamp":"2026-10-23T12:00:00Z","temperature_c":20.1,"humidity_pct":68.4,"language":"ro"}
```

Language codes: `en`, `ro`, `pl`. The field name is configurable through `reportLanguageField` in config.js. The interface uses the top-right EN / RO selection. This also sets the report explanation default to en or ro; the report selector can independently choose pl. The returned explanation receives the matching HTML `lang` attribute. The adapter expects:

```json
{"explanation":"Explicația în limba română...","letter":"Dear landlord..."}
```

The letter stays editable and English as in the proposal. Existing locally edited drafts are not overwritten by a service response. Failed or out-of-order responses are handled. Demo mode uses clearly labelled local sample explanations and does not call the service.

## T17 — display-only forecast contract to agree

No T17 endpoint was found in retrieved main.py. Set `endpoints.forecast` to the exact route Sergiu provides. The proposed adapter input is:

```json
{
  "available":true,
  "condensation":{"warning":"High condensation risk tonight","horizon_hours":48},
  "outside":{"now_c":9,"tonight_min_c":4,"tomorrow_c":10},
  "weather_code":61,
  "updated_at":"2026-10-23T12:00:00Z"
}
```

The front end displays these values. It does not calculate condensation risk or fetch Open-Meteo directly. Set `available:false` and a `reason` when the back-end cannot provide the forecast. Missing or malformed results remain unavailable. The panel includes the horizon, warning, weather words and all three outside temperatures.

Weather code descriptions follow the official WMO table at https://open-meteo.com/en/docs . Motion is a gentle 3-pixel translation, 2.5 s × 2, inside a single page-opening window of at most 5 seconds. Lightning is static; there is no flashing. Reduced-motion users receive no animation.

## Seven-day history — Should

The repository currently has no GET history endpoint. Set `endpoints.history` after the route is agreed. The adapter accepts a list of the same exact-precision reading objects, or `{ "readings": [...] }`, covering seven days in chronological order. Missing days are displayed as No data.

Each day's bar shows the arithmetic mean of valid readings. Hours above 70% use a bounded sample-coverage interval, capped at the configured expected cadence (15 seconds for the device). Missing intervals are never assumed to be humid. Coverage is reported beside the hours so gaps are visible. Local calendar days use Europe/London, including midnight boundaries; duplicate timestamps do not inflate exposure.

## Local connection

Run the team's FastAPI app at http://127.0.0.1:8000 using its own README. Run this project's `py run.py` at http://127.0.0.1:8080, then click Connect to API. The local preview forwards `/api/*` to the fixed API base. No CORS change or browser secret is needed.

Different base: `py run.py --api-url https://your-team-api.example` (replace this illustrative URL). Do not put credentials in that URL or in front-end files. The preview only binds to 127.0.0.1 and is not a production proxy.

The hosted static preview continues to use sample data; a real deployed API URL and appropriate access control are needed before real tenant data can be connected.
