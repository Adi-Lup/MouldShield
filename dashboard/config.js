// No passwords or API keys belong in this public front-end configuration.
window.MOULDSHIELD_CONFIG = {
  mode: 'demo', // Change to 'live' for the project API.
  apiBaseUrl: '/api', // Local VS Code preview uses '/api' through run.py.
  endpoints: {
    latest: '/readings/latest',
    verify: '/verify', // Confirmed in Adi-Lup/MouldShield/backend/main.py.
    history: '/readings/history', // T17: the readings of the last 7 days.
    report: '/report', // T13: explanation and letter (backend/README.md).
    forecast: '/forecast' // T17: condensation warning and outside temperatures.
  },
  timeZone: 'Europe/London',
  refreshIntervalMs: 15000,
  requestTimeoutMs: 8000,
  expectedReadingIntervalSeconds: 15,
  reportLanguageField: 'language'
};
