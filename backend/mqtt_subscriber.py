# mqtt_subscriber.py - brings the real device readings from AWS IoT Core into the back-end (T27)
#
# Flow: device -> AWS IoT Core (MQTT over TLS) -> this script -> POST /readings -> SQLite
#
# It connects to AWS IoT Core with its own certificate, as the client "mouldshield-subscriber".
# Its IoT policy (mouldshield-subscriber-policy) only allows Connect, Subscribe and Receive
# on the device topic. It cannot publish, so a stolen certificate cannot send fake readings.
#
# Run it (keep the API running in another window):
#   python mqtt_subscriber.py
# Stop it with Ctrl + C.
#
# Negative test (a topic that is not in the policy, AWS should refuse the subscription):
#   python mqtt_subscriber.py mouldshield/other-device/readings
#
# The certificate files are NOT in the repo. They stay in C:\Users\<you>\Projects\mouldshield-certs

import json
import os
import sys
from pathlib import Path

import paho.mqtt.client as mqtt
import requests

ENDPOINT = "a3vw3358s3u78v-ats.iot.eu-west-2.amazonaws.com"
PORT = 8883
CLIENT_ID = "mouldshield-subscriber"
DEFAULT_TOPIC = "mouldshield/mouldshield-01/readings"
TOPIC = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOPIC
CERTS = Path.home() / "Projects" / "mouldshield-certs"

# The local API by default. On AWS (T16) we only change this setting, not the code.
API_URL = os.environ.get("MOULDSHIELD_API_URL", "http://127.0.0.1:8000/readings")

# The fields the API expects (same names as make_reading on the device)
FIELDS = ["device_id", "timestamp", "temperature_c", "humidity_pct"]


def on_connect(client, userdata, flags, reason_code, properties):
    print("Connect result:", reason_code)
    if reason_code.is_failure:
        print("Could not connect. Check the certificate files and the IoT policy.")
        return
    # We subscribe here, so after a reconnect the subscription is made again
    client.subscribe(TOPIC, qos=1)
    print("Subscribed to", TOPIC)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    # AWS answers with a failure code if the policy does not allow the subscription
    for code in reason_codes:
        if code.is_failure:
            print("Subscription REFUSED by AWS:", code)
        else:
            print("Subscription accepted by AWS (QoS", code.value, ")")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("Disconnected:", reason_code, "(paho tries to reconnect by itself)")


def on_message(client, userdata, message):
    # 1. Read the JSON from the device
    try:
        data = json.loads(message.payload)
    except ValueError:
        print("Skipped: the message is not valid JSON")
        return

    # 2. Keep only the fields the API expects, and check none is missing
    missing = [name for name in FIELDS if name not in data]
    if missing:
        print("Skipped: missing fields", missing)
        return
    reading = {name: data[name] for name in FIELDS}

    # 3. Send it to the back-end, which saves it in the database
    try:
        answer = requests.post(API_URL, json=reading, timeout=5)
    except requests.RequestException as error:
        print("API not reachable, reading NOT saved:", error)
        return

    if answer.ok:
        print("Saved", reading["timestamp"], reading["humidity_pct"], "% ->",
              answer.status_code, answer.json())
    else:
        print("API refused the reading:", answer.status_code, answer.text)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect
client.on_message = on_message
client.tls_set(
    ca_certs=str(CERTS / "AmazonRootCA1.pem"),
    certfile=str(CERTS / "subscriber-cert.pem.crt"),
    keyfile=str(CERTS / "subscriber-private.pem.key"),
)

print("Connecting to", ENDPOINT, "as", CLIENT_ID)
print("Readings will be sent to", API_URL)
client.connect(ENDPOINT, PORT, keepalive=60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped by the user")
    client.disconnect()
