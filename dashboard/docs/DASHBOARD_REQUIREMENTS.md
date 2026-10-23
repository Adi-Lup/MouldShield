# Updated dashboard requirements — implementation check

23 October 2026 · THE SHARKS · Claudiu Stratulat

These changes are in the dashboard implementation. Wireframes remain unchanged.

| Requirement | Dashboard implementation | Validation / dependency |
|---|---|---|
| 1. Team logo | `assets/logo-by-the-sharks.svg` used in navigation and report | Supplied asset preserved |
| 2. Integer humidity on page | `core.js` formats humidity using Math.round at render time | Exact numeric values retained in state, CSV and report payload; no database write by this front end |
| 3. Integrity badge | Calls GET /verify; green Data verified or red Tampered from the response | Existing repository schema confirmed; errors/empty chains remain neutral |
| 4. Report language | English, Română, Polski selector; sends en/ro/pl with the exact reading to T13 | API adapter tested with fixtures; actual T13 route/model not yet in retrieved main.py; interface follows the top-right EN / RO choice |
| 5. Forecast Must | Main panel displays T17 warning/horizon and outside now, tonight minimum and tomorrow temperatures | Display-only adapter; no client condensation calculation; configure the agreed T17 endpoint |
| 6. Seven-day Should | 24 h / 7 days switch, seven daily average bars, hours strictly above 70%, and coverage table | Missing intervals are not counted; history route still required for live data |
| 7. Weather Could | WMO weather_code icon plus weather words; gentle movement for at most five seconds after page opening | Reduced motion supported, no flashing lightning, refresh does not restart animation |
| 8. Accessibility target | Large type, visible focus, named form controls, risk/integrity words and icons, tested main-text contrast above 7:1 | Full WCAG 2.2 AA review remains a team target, not a certification claim |
| 9. Lighthouse and T22 | Actual desktop and mobile audits of all three pages in both EN and RO | 12/12 reports score 100/100 automated accessibility; HTML/JSON evidence in docs/testing/lighthouse |
| Added Level 1 DFD | Separate PNG and editable SVG files in diagrams/; no dashboard view | Original use case and context images unchanged; see T15_diagrams.md |

The team repository was checked again on 23 October 2026 (`backend/main.py`, SHA `12bca447901f8c811b46778334ac358a5ad29c5d`). It exposes `/readings/latest` and `/verify`; `/report`, forecast and history routes were not present. Their front-end adapters are ready for Sergiu's agreed endpoints and response models; live integration is not reported as passed.

## Requested interface revision

The top-right mode/profile label (Live API / T) has been replaced with an accessible EN / RO selector. It switches interface text and accessible names, updates the document language and remembers the choice. Report explanation language remains a separate control; switching the header sets its default to EN or RO. Exact sensor readings, CSV data, returned explanations and user-edited letters are preserved. The mode notice and connection button remain in the dashboard banner.

The System diagrams navigation item and page were removed. All original and Level 1 diagram files remain unchanged in the separate `diagrams/` folder. The standalone HTML embeds no diagram images.
