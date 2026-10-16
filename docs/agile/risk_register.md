# Risk register

MouldShield, team THE SHARKS. Kept by the Scrum Master (Adrian) and checked at every sprint review. Last updated: 16 October 2026.

The first risks come from our proposal and Formative 1. New risks are added when we find them. Closed risks stay in the table, so we can see how they were handled.

## Open risks

| ID | Risk | Level | Owner | What we do |
|----|------|-------|-------|------------|
| R1 | The device breaks before the viva | Medium | Sergiu | The data simulator (T09) sends realistic readings, so the dashboard and the demo still work |
| R2 | The university Wi-Fi blocks the device | Low | Adrian | We decided not to use the university Wi-Fi. The device always connects through Adrian's phone hotspot, which worked in class on 15 Oct. Adrian keeps the phone charged, and we check the connection again the day before the viva |
| R3 | We fall behind | High | Adrian | We follow MoSCoW and cut from the bottom of the backlog (Should items first). Progress is checked at every sprint review |
| R4 | The Sprint 1 goal ("first reading saved in the database") is not met, because T06 and T07 have not started yet (found 13 Oct) | Medium | Adrian | Sergiu builds a simple version only (`POST /readings` saving to SQLite). Checked at the stand-up on 14 Oct; if he is blocked, Adrian helps |
| R5 | Sergiu and Claudiu cannot program the device from their own laptops (found 13 Oct) | Low | Adrian | On 15 Oct Claudiu programmed the device over USB from his own laptop, with his own UiFlow2 account, so the USB way works. Sergiu tests the same way when he does T08c. If it does not work, he uses Adrian's laptop |
| R6 | A firmware update breaks the TLS clock workaround (found 13 Oct) | Medium | Adrian | We stay on firmware v2.5.3. After any update, we test the AWS connection again (part of T21). Bug reported to M5Stack as [uiflow-micropython#120](https://github.com/m5stack/uiflow-micropython/issues/120) |
| R7 | The AWS credit runs out, for example if the server is left running | Medium | Adrian | Free plan (cannot be charged), budget alert at $20 a month, and the EC2 server is started only in Sprint 3 |

## Closed risks

| ID | Risk | How it ended | Closed |
|----|------|--------------|--------|
| C1 | The AWS credit does not cover Amazon Bedrock | Bedrock tested on our account with Claude Haiku 4.5 and it works. The template letter stays as a backup | 11 Oct 2026 |
| C2 | The hardware arrives late | It arrived on 13 October, at the start of Sprint 1 as planned | 13 Oct 2026 |
| C3 | The device cannot connect to AWS IoT Core ("certificate has expired") | We tested the idea that the firmware reads the clock 30 years ahead, and it was right. Fixed by moving the clock back only during the connection, with full certificate checking kept (see `device/README.md`). Follow-up risk: R6 | 13 Oct 2026 |
