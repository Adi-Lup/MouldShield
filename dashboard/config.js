// No passwords or API keys belong in this public front-end configuration.
window.MOULDSHIELD_CONFIG = {
  mode: 'demo', // Change to 'live' for the project API.
  apiBaseUrl: '/api', // Local VS Code preview uses '/api' through run.py.
  endpoints: {
    latest: '/readings/latest',
    verify: '/verify', // Confirmed in Adi-Lup/MouldShield/backend/main.py.
    history: null, // Configure when Sergiu provides the history endpoint.
    report: '/report', // T13: route planned in the team's README; schema to agree.
    forecast: null // T17: set the exact endpoint once supplied by Sergiu.
  },
  timeZone: 'Europe/London',
  refreshIntervalMs: 15000,
  requestTimeoutMs: 8000,
  expectedReadingIntervalSeconds: 15,
  reportLanguageField: 'language'
};
