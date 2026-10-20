# Sprint review and retrospective: Sprint 1 (2026-10-19)

**Sprint goal:** First reading saved in the database
**Goal met:** Yes. A reading is saved in SQLite through `POST /readings`. The full path from the real device to the database comes with T27 in Sprint 2.
**Where:** WhatsApp call
**Time:** 10:35 to 11:10
**Notes by:** Adrian Lupescu (Scrum Master)

## Attendance

| Name | Present |
|------|---------|
| Adrian Lupescu | Yes |
| Sergiu Girnita | Yes |
| Claudiu Stratulat | Yes |

## Sprint review: what works now (the increment)

We went through the Scrum board together and each of us talked about the work we did in Sprint 1.

| Task | Status | Evidence (commit, screenshot) |
|------|--------|-------------------------------|
| T04 Humidity thresholds research (Claudiu) | Done | `docs/research/T04_humidity_thresholds.md` (1fe8bfa, a53b976) |
| T05 Persona and wireframes (Claudiu) | Done | `docs/design/` (85b9f34, 55c9343) |
| T06 and T07 Back-end and database (Sergiu) | Done | `backend/main.py`: `POST /readings`, `GET /readings/latest`, SQLite table `readings` (2742ee5) |
| T08 Sensor reading on the device (all three) | Done | `device/sensor_screen.py` (Claudiu, 3fb0aef, 9618e81), `device/reading_json.py` (Sergiu, f4b1660) |
| T09 Data simulator (Sergiu) | Done | `backend/simulator.py` (a689c04) |
| T11 Real readings from the device to AWS IoT Core (Adrian) | Done | `device/mouldshield_device.py` (8642bc3), `W2_iot_real_readings.png`, `W2_screen_synced.jpg` |

We also talked about the device screen design that the team approved on 16 October: a blue status bar at the top with a cloud icon (SYNCED or OFFLINE), and an arrow above the current risk box. The status bar was planned for Sprint 2, but it is already working on the device, because it came together with T11.

## Decisions

1. New task T27 "Build the MQTT subscriber (AWS IoT Core to POST /readings)" is added to Sprint 2, owner Adrian (Must, US1). Everyone agreed. With T27, each of us has two tasks in Sprint 2.
2. The dashboard uses the team logo made by Adrian. Adrian has sent it to Claudiu for his next tasks.
3. The dashboard shows the humidity without decimals, the same as the device screen. The raw value (with decimals) is still sent to AWS and saved.
4. T10 uses the same limits as the device: MODERATE from 60% and HIGH from 70%.
5. Risks R4 and R5 are closed. A new risk is added for the device freezing when the connection drops (see the risk register).

## Retrospective

| What went well | What did not go well | What we change next sprint |
|----------------|----------------------|----------------------------|
| All Sprint 1 tasks are Done, and each one was checked by a teammate | It was not clear to everyone at first where files go in the repository | Add a short "Where to put your files" section to the README (Adrian) |
| The offline test found a real bug (the device froze when the hotspot was turned off), and it was fixed before Sprint 2 | In UiFlow2, Run uses the saved code, so changes that were not saved did not run | Always press Ctrl+S before Run in UiFlow2 |

## Changes to the backlog

- T27 added to Sprint 2 (Adrian).
- The device status bar is done in Sprint 1, earlier than planned.

## Next meetings

| Meeting | When | Where |
|---------|------|-------|
| Stand-up | Thursday 22 October | In class |
| Sprint 2 review and retrospective | Sunday 25 October, 20:00 | WhatsApp call |
