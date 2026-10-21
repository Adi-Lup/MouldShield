# Risk register

MouldShield, team THE SHARKS. Kept by the Scrum Master (Adrian) and checked at every sprint review. Last updated: 21 October 2026.

The first risks come from our proposal and Formative 1. New risks are added when we find them. Closed risks stay in the table, so we can see how they were handled.

## Open risks

| ID | Risk | Level | Owner | What we do |
|----|------|-------|-------|------------|
| R1 | The device breaks before the viva | Medium | Sergiu | The data simulator (T09) sends realistic readings, so the dashboard and the demo still work |
| R2 | The university Wi-Fi blocks the device | Low | Adrian | We decided not to use the university Wi-Fi. The device always connects through Adrian's phone hotspot, which worked in class on 15 Oct. Adrian keeps the phone charged, and we check the connection again the day before the viva |
| R3 | We fall behind | High | Adrian | We follow MoSCoW and cut from the bottom of the backlog (Should items first). Progress is checked at every sprint review |
| R6 | A firmware update breaks the TLS clock workaround (found 13 Oct) | Medium | Adrian | We stay on firmware v2.5.3. After any update, we test the AWS connection again (part of T21). Bug reported to M5Stack as [uiflow-micropython#120](https://github.com/m5stack/uiflow-micropython/issues/120) |
| R7 | The AWS credit runs out, for example if the server is left running | Medium | Adrian | Free plan (cannot be charged), budget alert at $20 a month, and the EC2 server is started only in Sprint 3 |
| R9 | Readings are lost when part of the system is down. Found in the R8 tests on 21 Oct (4 to 9 readings lost each time the connection dropped) | Low | Adrian | Device side fixed on 21 Oct: the device keeps up to one hour of readings in memory and sends them in order when the connection is back (tested: 4 readings kept during a 1 minute drop, all saved, `GET /verify` OK with 131 readings). Still open: a reading that reaches the subscriber while the API is stopped is lost, and the waiting readings are lost if the device is switched off |

## Closed risks

| ID | Risk | How it ended | Closed |
|----|------|--------------|--------|
| C1 | The AWS credit does not cover Amazon Bedrock | Bedrock tested on our account with Claude Haiku 4.5 and it works. The template letter stays as a backup | 11 Oct 2026 |
| C2 | The hardware arrives late | It arrived on 13 October, at the start of Sprint 1 as planned | 13 Oct 2026 |
| C3 | The device cannot connect to AWS IoT Core ("certificate has expired") | We tested the idea that the firmware reads the clock 30 years ahead, and it was right. Fixed by moving the clock back only during the connection, with full certificate checking kept (see `device/README.md`). Follow-up risk: R6 | 13 Oct 2026 |
| C4 | The Sprint 1 goal ("first reading saved in the database") is not met | Met: Sergiu built `POST /readings` saving to SQLite, and it works. Agreed at the Sprint 1 review | 19 Oct 2026 |
| C5 | Sergiu and Claudiu cannot program the device from their own laptops | No longer relevant: Claudiu programmed it over USB from his own laptop, and Sergiu used the device for his part of T08 (T08c). Agreed at the Sprint 1 review | 19 Oct 2026 |
| C6 | The device freezes when the connection drops (found on 18 Oct) | Fixed on 18 Oct (`umqtt.simple`, 10 second timeout, Wi-Fi check). Tested three times on 21 Oct by turning the hotspot off for 1 to 3 minutes: each time the screen showed OFFLINE straight away and kept working, and the device reconnected by itself within about 20 seconds. `GET /verify` was still OK afterwards | 21 Oct 2026 |
