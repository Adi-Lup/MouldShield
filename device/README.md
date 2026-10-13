# Device (M5StickS3 + ENV III)

This folder has the code that runs on the MouldShield device. The device measures temperature and humidity in a room and sends the readings to AWS IoT Core.

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

## Boot splash screen

When the device is switched on, it shows "MouldShield", "prototype v0.1" and "by THE SHARKS" for 3 seconds, and then the normal UiFlow2 menu with WiFi, server status and Access Code.

| File | What it does |
|------|--------------|
| `splash.py` | The start screen. On the device it is saved as `/flash/splash.py` |
| `install_splash.py` | Run once from UiFlow2 to install the start screen on the device |

How it works: every time the device starts, it runs `/flash/boot.py`, which then shows the UiFlow2 menu. The installer adds a few lines at the top of `boot.py` that call `splash.show()`. These lines are inside `try/except`, so if the start screen ever fails, the device still starts normally. A copy of the original file is kept on the device as `/flash/boot_backup.py`.

The start screen is separate from the main program, so it does not change when someone runs a new program from UiFlow2. Flashing the firmware again removes it, so run `install_splash.py` again after that.

## Who does what (T08)

| Part | Who | What |
|------|-----|------|
| 8a | Adrian | Flash the firmware, connect the device to Wi-Fi and to UiFlow2 (done 13 October 2026) |
| 8b | Claudiu | Plug in the ENV III sensor and show temperature and humidity on the screen |
| 8c | Sergiu | Turn the readings into JSON in the same format that `POST /readings` will receive |

## Connection to AWS IoT Core (T11)

Task on the Scrum board: **T11 Connect the device to AWS IoT Core** (issue #11). Connection working since 13 October 2026.

| File | What it does |
|------|--------------|
| `test_iot_from_laptop.py` | Tests the IoT policy from a laptop: one message on our own topic (accepted) and one on another topic (refused) |
| `upload_certs.py` | Copies the certificate files from the laptop to `/flash/certs` on the device over USB |
| `test_iot_from_device.py` | Sends a test message from the device to AWS IoT Core |

How it works:
- The device is the Thing `mouldshield-01` in AWS IoT Core (region eu-west-2, London).
- It connects with MQTT over TLS on port 8883, using its own X.509 certificate and private key. The server certificate is fully checked (`CERT_REQUIRED`) against Amazon Root CA 1.
- It publishes to the topic `mouldshield/mouldshield-01/readings` (project / device / data type).
- The IoT policy `mouldshield-device-policy` only lets this device connect as `mouldshield-01` and publish on its own topic (least privilege). Our negative test from the laptop showed that AWS refuses any other topic.

### Certificates

The certificate files are kept outside the repository and are never committed (`.gitignore` blocks `*.pem`, `*.key`, `*.crt` and `certs/`). They are copied to the device only over the USB cable with `upload_certs.py`, so the private key never goes through UiFlow2 or any cloud service. Close UiFlow2 in the browser before running the script, so the USB port is free.

### Firmware clock workaround

On UiFlow2 v2.5.3 (MicroPython v1.27.0) the TLS library reads the clock 30 years ahead of the real device clock:
- with the correct time, TLS said the AWS certificate "has expired";
- with the clock at 1970, it said the certificate "starts in the future".

We tested this idea by moving the clock back exactly 30 years (946,684,800 seconds) and the connection worked with full certificate checking. So `tls_connect()` moves the clock back only during the TLS handshake and puts the real time back straight away, even if the connection fails. The messages still have the correct UTC timestamp. Every new MQTT connection on the device must use `tls_connect()`.

We reported this to M5Stack on 13 October 2026: [m5stack/uiflow-micropython#120](https://github.com/m5stack/uiflow-micropython/issues/120). The offset is exactly the difference between the 1970 and 2000 epochs, so it may be an epoch mismatch inside the firmware.

If the firmware is updated, check again whether this workaround is still needed (part of T21, security check).

## Next step

Join the sensor reading (8b) and the JSON message (8c) with the MQTT publish, so the device sends real readings to AWS IoT Core every few minutes.
