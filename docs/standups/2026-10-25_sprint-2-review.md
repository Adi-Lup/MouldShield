# Sprint 2 review 2026-10-25

**Sprint:** Sprint 2 (19 to 25 October)
**Planned:** Sunday 25 October, 20:00, on WhatsApp
**Notes by:** Adrian Lupescu (Scrum Master)

## Status

The Sprint 2 review did not take place on 25 October. It moves to a date still to be agreed by the team, before the end of Sprint 3, together with the Sprint 3 planning.

## Where Sprint 2 stands on GitHub (checked 27 October)

| Task | Owner | Status |
|------|-------|--------|
| T27 MQTT subscriber | Adrian | Done 20 Oct |
| T12 Hash chain and `GET /verify` | Adrian | Done 21 Oct |
| T14 Dashboard | Claudiu | Done 23 Oct |
| T15 Use Case and Data Flow diagrams | Claudiu | Done 23 Oct |
| T10 Risk calculation | Sergiu | Not on GitHub yet |
| T13 AI explanation and landlord letter | Sergiu | Not on GitHub yet |

The last commit is `5ec5a91` (23 October). T10 and T13 stay open until the review, where the team decides if they move to Sprint 3.

## To decide at the review

- T10 and T13: progress and whether they move to Sprint 3.
- No PUT, PATCH or DELETE on readings.
- `POST /readings` returning 201 and `GET /readings/latest` returning 404 when empty.
- Data for the 7-day graph at the viva (device running for a week or the simulator).
- Dashboard served by FastAPI on the same EC2 as the API.
- Retrospective and the Sprint 3 plan.
