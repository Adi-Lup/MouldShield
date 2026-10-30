# Gantt chart and milestones

MouldShield, team THE SHARKS. Kept by the Scrum Master (Adrian). Last updated: 30 October 2026.

The chart shows the five weeks of the project: one planning week, three one-week sprints and a final week for the viva. Each bar is a task (issue number = task number) and ends on the day it was Done on the Scrum board. The sprint plan and the reasons for each change are in `product_backlog.md`.

```mermaid
gantt
    title MouldShield plan, 5 October to 6 November 2026
    dateFormat YYYY-MM-DD
    axisFormat %d %b

    section Planning
    T01 Order the hardware              :done, t01, 2026-10-05, 2026-10-11
    T02 GitHub repository and Scrum board :done, t02, 2026-10-05, 2026-10-12
    T03 AWS set-up and budget alert     :done, t03, 2026-10-05, 2026-10-11
    Plan agreed                         :milestone, m1, 2026-10-11, 0d

    section Sprint 1
    T04 Research on humidity levels     :done, t04, 2026-10-12, 2026-10-18
    T05 Persona and wireframes          :done, t05, 2026-10-12, 2026-10-18
    T06 Database design                 :done, t06, 2026-10-12, 2026-10-18
    T07 FastAPI back-end                :done, t07, 2026-10-12, 2026-10-18
    T08 Device and sensor               :done, t08, 2026-10-12, 2026-10-18
    T09 Data simulator                  :done, t09, 2026-10-12, 2026-10-18
    T11 Device to AWS IoT Core          :done, t11, 2026-10-12, 2026-10-18
    First reading saved                 :milestone, m2, 2026-10-18, 0d

    section Sprint 2
    T27 MQTT subscriber                 :done, t27, 2026-10-19, 2026-10-20
    T12 Hash chain and GET /verify      :done, t12, 2026-10-19, 2026-10-21
    T14 Dashboard                       :done, t14, 2026-10-19, 2026-10-23
    T15 Use Case and DFD                :done, t15, 2026-10-19, 2026-10-23
    T10 Risk level (moved to Sprint 3)  :done, t10, 2026-10-19, 2026-10-27
    T13 AI report and letter (moved to Sprint 3) :done, t13, 2026-10-19, 2026-10-27
    Working prototype                   :milestone, m3, 2026-10-25, 0d

    section Sprint 3
    T16 Deploy on AWS                   :done, t16, 2026-10-26, 2026-10-27
    T17 Condensation forecast           :done, t17, 2026-10-26, 2026-10-27
    T18 AI photo evidence               :done, t18, 2026-10-26, 2026-10-27
    T21 Security check                  :done, t21, 2026-10-26, 2026-10-28
    T19 Mobile page and QR code         :done, t19, 2026-10-26, 2026-10-29
    T20 PDF report                      :done, t20, 2026-10-26, 2026-10-29
    T22 Testing and results             :done, t22, 2026-10-26, 2026-10-30
    T23 Slides                          :active, t23, 2026-10-26, 2026-11-01
    Live on AWS                         :milestone, m4, 2026-10-27, 0d

    section Final
    T24 Final code on GitHub            :t24, 2026-11-02, 1d
    T25 Rehearse the demo               :t25, 2026-11-02, 2026-11-05
    T26 Live viva                       :t26, 2026-11-06, 1d
    Viva                                :milestone, m5, 2026-11-06, 0d
```

## Milestones

| Milestone | Planned | Reached | Evidence |
|-----------|---------|---------|----------|
| Plan agreed | 11 Oct (end of Week 1) | 11 Oct | Proposal, backlog and Scrum board |
| First reading saved in the database | 18 Oct (end of Sprint 1) | 18 Oct | `POST /readings` with SQLite, agreed at the Sprint 1 review (`../standups/2026-10-19_sprint-1-review.md`) |
| Working prototype | 25 Oct (end of Sprint 2) | 25 Oct, without T10 and T13 | Device, subscriber, hash chain and dashboard working together; T10 and T13 moved to Sprint 3 |
| Live on AWS | Sprint 3 | 27 Oct | T16: back-end and dashboard on EC2 with HTTPS through CloudFront |
| Final code on GitHub | 2 Nov | | T24 |
| Viva | 6 Nov (Week 5, Session 2) | | T26 |

## Changes to the plan

- T10 (risk level) and T13 (AI report and letter) were planned for Sprint 2. They moved into Sprint 3 and were Done on 27 October.
- T16 (deploy on AWS) was moved from Sprint 2 to Sprint 3 on 13 October, so the server only runs (and costs credit) when the back-end is ready.
- T27 (MQTT subscriber) was added to Sprint 2 on 19 October.
