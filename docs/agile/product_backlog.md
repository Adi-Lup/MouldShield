# Product backlog and sprint plan

MouldShield, team THE SHARKS. Kept by the Scrum Master (Adrian). Last updated: 16 October 2026.

The backlog is ordered by value, and we prioritise it with MoSCoW, as we said in our proposal and in Formative 1. The team orders it together (we have no separate Product Owner). It changes when we learn something new, so this file and the Scrum board are updated every week.

On the Scrum board (GitHub Projects) every issue has:
- a **MoSCoW label** (`Must` or `Should`) if it builds a feature, and
- a **Sprint** value: Planning, Sprint 1, Sprint 2, Sprint 3 or Final.

## User stories (product backlog, in priority order)

| ID | User story | MoSCoW | Tasks (issues) |
|----|------------|--------|----------------|
| US1 | As a tenant, I want to see the temperature, the humidity and a green, amber or red risk level, so that I know when my room is getting too damp. | Must | T04, T05, T06, T07, T08, T10, T11, T14, T16 |
| US2 | As a tenant, I want my readings to be tamper-evident, so that my landlord can trust that the old data was not changed. | Must | T12 |
| US3 | As a tenant, I want a simple explanation of the risk in my own language and a draft letter to my landlord, so that I can ask for repairs with clear evidence. | Must | T13, T20 |
| US4 | As a member of the team, I want realistic test readings when the device is not connected, so that we can build and demo the system without the hardware. | Must | T09 |
| US5 | As a tenant, I want a warning about condensation before it happens, so that I can heat or air the room in time. | Must | T17 |
| US6 | As a tenant, I want to upload a photo of the damp and get a short description, so that my report also has visual evidence. | Should | T18 |
| US7 | As a person watching the demo, I want to open the live dashboard on my phone with a QR code, so that I can follow the readings without a laptop. | Should | T19 |

**Could have:** nothing at the moment.

**Will not have (for now):** email, SMS or push alerts; Amazon RDS; anchoring the hash chain in S3 Object Lock; flash encryption or a secure element for the device key. These are future work.

Tasks that are not features (planning, documentation, testing and the viva) have no MoSCoW label: T01, T02, T03, T15, T21, T22, T23, T24, T25, T26. They are still needed to finish the project.

## Sprints

Each sprint is one week. Stand-ups are in class on Thursday and Friday and on Teams on the other days. At the end of each sprint we hold a short sprint review (what works now) and a retrospective (what went well, what did not, what we change next time), and we write both down in `docs/standups/`.

| Sprint | Week | Sprint goal | Sprint backlog |
|--------|------|-------------|----------------|
| Planning | Week 1 (5 to 11 Oct) | Plan agreed | T01, T02, T03 |
| Sprint 1 | Week 2 (12 to 18 Oct) | First reading saved in the database | T04, T05, T06, T07, T08, T09, T11 |
| Sprint 2 | Week 3 (19 to 25 Oct) | Working prototype | T10, T12, T13, T14, T15 |
| Sprint 3 | Week 4 (26 Oct to 1 Nov) | All Must features done and on AWS | T16, T17, T18, T19, T20, T21, T22, T23 |
| Final | Week 5 (2 to 6 Nov) | Live demo at the viva | T24, T25, T26 |

For Sprint 1, a simple version of T06 and T07 is enough to meet the goal: `POST /readings` saves one reading in SQLite on a laptop. The full back-end is finished in Sprint 2.

## Definition of Done

A task is Done when:
1. the code or document is on GitHub,
2. it has been tested (for code: it runs and gives the expected result),
3. one teammate has checked it, and
4. the issue is linked to the commits (commit message starts with `#N`).

## Changes to the backlog

| Date | Change | Why |
|------|--------|-----|
| 13 Oct 2026 | T08 split into 8a (Adrian), 8b (Claudiu) and 8c (Sergiu) | So that each of us has a hands-on part with the device |
| 13 Oct 2026 | Flow changed to device, AWS IoT Core, subscriber script, FastAPI | The device can use its own certificate with MQTT over TLS |
| 13 Oct 2026 | S3 Object Lock anchoring moved to "Will not have (for now)" | Not needed for a student prototype; written up as future work |
| 13 Oct 2026 | Deploy on AWS (T16) moved from Sprint 2 to Sprint 3 | The server costs credit per hour, so we start it only when the back-end is ready |
| 15 Oct 2026 | The risk levels are called LOW, MODERATE and HIGH everywhere; T10 renamed to "(low, moderate, high)" | Team decision in class, so the device, the dashboard and the report use the same words |
| 16 Oct 2026 | New device screen design approved by the team: a blue status bar at the top with a cloud icon (SYNCED or OFFLINE) and an arrow above the current risk box | The tenant can see if the last reading reached AWS, and the arrow is clearer than the small marker. The arrow goes in with the T08b screen code; the status bar is planned for Sprint 2, after the device to AWS connection (T11) is joined with the sensor code |
