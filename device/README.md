# Device (M5StickS3 + ENV III)

This folder has the code that runs on the MouldShield device. The device measures temperature and humidity in a room and will send the readings to our back-end.

Task on the Scrum board: **T08 Set up the device and read the sensor** (issue #8).

## Hardware

| Part | What it does |
|------|--------------|
| M5StickS3 | Small computer with Wi-Fi, colour screen, buttons and speaker (ESP32-S3 chip) |
| ENV III unit | Temperature and humidity sensor, plugs into the Grove port with the cable in the box |

Total cost was about £36 including delivery.

## Firmware

- UiFlow2 firmware **v2.5.3** ("UIFlow2.0 StickS3", official), flashed on 13 October 2026 with M5Burner.
- Timezone is set to **GMT0 (UTC)** on purpose. The device sends time in UTC and the dashboard shows UK time, so the clock change at the end of October does not mix up the readings.
- Boot option: show startup menu and network setup.

## Wi-Fi

The device connects to a phone hotspot, not to the university Wi-Fi, because university networks often block small IoT devices. The hotspot name is `MouldShield` and it uses 2.4 GHz, because the StickS3 does not work on 5 GHz.

The Wi-Fi password is **not** written here on purpose. Ask Adrian.

## How to program the device

We use the UiFlow2 web editor, so there is nothing to install. Use Chrome or Edge.

1. Turn on the `MouldShield` hotspot and power on the device.
2. Check that the screen shows **WiFi OK** and **SERVER OK**.
3. Open https://uiflow2.m5stack.com and choose **StickS3** as the controller.
4. Connect in one of two ways:
   - **Cloud Access Code:** the code is on the device screen. The device is registered as **MouldShield**.
   - **USB:** plug the device into your laptop with a USB-C data cable and choose **USB** as the connection.
5. Press **Run Once** to test a program, or **Run Always** to keep it on the device after a restart.

Do not share the Access Code in screenshots, because anyone with the code can send programs to the device.

## Who does what (T08)

| Part | Who | What |
|------|-----|------|
| 8a | Adrian | Flash the firmware, connect the device to Wi-Fi and to UiFlow2 (done 13 October 2026) |
| 8b | Claudiu | Plug in the ENV III sensor and show temperature and humidity on the screen |
| 8c | Sergiu | Turn the readings into JSON in the same format that `POST /readings` will receive |

## Next step

T11: connect the device to AWS IoT Core with MQTT and its own certificate. Certificates and keys must never be uploaded to GitHub.
