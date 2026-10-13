# test_iot_from_device.py - first MQTT message from the MouldShield device to AWS IoT Core.
# Run once from UiFlow2 (Python tab, Custom Edit mode, then Run Once) or paste it in the WebTerminal (Ctrl+E, then Ctrl+D).
# The certificate files are read from /flash/certs on the device (copied over USB with upload_certs.py).
# This file has no secrets in it, only the public endpoint address, so it is safe in UiFlow2 and on GitHub.
#
# FIRMWARE WORKAROUND (found and tested on 13 Oct 2026):
# On this UiFlow2 firmware (v2.5.3, MicroPython v1.27.0) the TLS library reads the clock 30 years ahead
# of the real device clock. With the correct clock, TLS says the AWS certificate "has expired";
# with the clock at 1970, it says "starts in the future". When we moved the clock back by exactly
# 30 years, the connection worked with full server certificate checking (ssl.CERT_REQUIRED).
# So we keep CERT_REQUIRED and move the clock back only while the TLS connection is made,
# then put the correct time back straight away, so our messages still have the right timestamp.
import M5
from M5 import *
import json
import machine
import ntptime
import ssl
import time
from umqtt import MQTTClient

ENDPOINT = "a3vw3358s3u78v-ats.iot.eu-west-2.amazonaws.com"
CLIENT_ID = "mouldshield-01"
TOPIC = "mouldshield/mouldshield-01/readings"
CERT = "/flash/certs/device-cert.pem.crt"
KEY = "/flash/certs/device-private.pem.key"
CA = "/flash/certs/AmazonRootCA1.pem"
TLS_CLOCK_OFFSET = 946684800  # 30 years in seconds (1 Jan 1970 to 1 Jan 2000)


def show(lines, colour):
    Widgets.fillScreen(0x000000)
    y = 60
    for line in lines:
        Widgets.Label(line, 5, y, 1.0, colour, 0x000000, Widgets.FONTS.Montserrat12)
        y += 22


def utc_timestamp():
    t = time.gmtime()
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % t[:6]


def set_clock(seconds):
    t = time.gmtime(seconds)
    # RTC order: year, month, day, weekday, hours, minutes, seconds, subseconds
    machine.RTC().datetime((t[0], t[1], t[2], t[6], t[3], t[4], t[5], 0))


def sync_clock():
    for attempt in range(3):
        try:
            ntptime.settime()
            return True
        except Exception as e:
            print("NTP attempt", attempt + 1, "failed:", e)
            time.sleep(2)
    return False


def tls_connect(client):
    # Move the clock back 30 years only for the TLS handshake (see the note at the top),
    # then put the correct time back, even if the connection fails.
    real_now = time.time()
    set_clock(real_now - TLS_CLOCK_OFFSET)
    try:
        client.connect()
    finally:
        set_clock(time.time() + TLS_CLOCK_OFFSET)


M5.begin()
Widgets.setRotation(0)

show(["Syncing clock..."], 0xFFFFFF)
if not sync_clock():
    show(["Clock sync failed", "Check Wi-Fi and", "run again"], 0xFF0000)
    raise SystemExit
print("Device time (UTC):", utc_timestamp())

show(["Connecting to", "AWS IoT Core...", utc_timestamp()[:10]], 0xFFFFFF)
try:
    # TLS settings: our certificate and private key prove who we are,
    # Amazon Root CA 1 proves the server is really AWS (CERT_REQUIRED checks it).
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_cert_chain(CERT, KEY)
    context.load_verify_locations(cafile=CA)
    context.verify_mode = ssl.CERT_REQUIRED

    client = MQTTClient(CLIENT_ID, ENDPOINT, port=8883, keepalive=60, ssl=context)
    tls_connect(client)
    message = {
        "device_id": CLIENT_ID,
        "timestamp": utc_timestamp(),
        "source": "device test",
        "note": "first message from the M5StickS3, no sensor yet",
    }
    client.publish(TOPIC, json.dumps(message), qos=1)
    client.disconnect()
    print("Published:", message)
    show(["AWS IoT: OK", "Message sent to", "mouldshield-01/", "readings", utc_timestamp()[:10]], 0x00C853)
except Exception as e:
    print("AWS IoT error:", e)
    text = str(e)
    show(["AWS IoT: ERROR", text[:22], text[22:44], text[44:66], "Clock: " + utc_timestamp()[:10]], 0xFF0000)
