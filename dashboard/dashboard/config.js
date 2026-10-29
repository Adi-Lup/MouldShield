// No passwords or API keys belong in this public front-end configuration.
window.MOULDSHIELD_CONFIG = {
  mode: 'live', // Real readings by default; use See example data for samples.
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
  historyRefreshIntervalMs: 300000, // Download the 7-day history every 5 minutes.
  requestTimeoutMs: 8000,
  expectedReadingIntervalSeconds: 15,
  reportLanguageField: 'language'
};
