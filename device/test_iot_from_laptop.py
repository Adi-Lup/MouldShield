# test_iot_from_laptop.py - checks that the MouldShield certificate and IoT policy work,
# by connecting to AWS IoT Core from the computer in the same way the device will.
#
# Positive test (allowed topic, should be accepted):
#   python device/test_iot_from_laptop.py
# Negative test (topic not in the policy, should be refused):
#   python device/test_iot_from_laptop.py mouldshield/other-device/readings
#
# The certificate files are NOT in the repo. They stay in C:\Users\<you>\Projects\mouldshield-certs
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt

ENDPOINT = "a3vw3358s3u78v-ats.iot.eu-west-2.amazonaws.com"
PORT = 8883
CLIENT_ID = "mouldshield-01"
DEFAULT_TOPIC = "mouldshield/mouldshield-01/readings"
CERTS = Path.home() / "Projects" / "mouldshield-certs"

topic = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOPIC
connected = False


def on_connect(client, userdata, flags, reason_code, properties):
    global connected
    print("Connect result:", reason_code)
    connected = not reason_code.is_failure


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print("Disconnected by AWS or by the script:", reason_code)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.tls_set(
    ca_certs=str(CERTS / "AmazonRootCA1.pem"),
    certfile=str(CERTS / "device-cert.pem.crt"),
    keyfile=str(CERTS / "device-private.pem.key"),
)

print("Connecting to", ENDPOINT, "as", CLIENT_ID)
client.connect(ENDPOINT, PORT)
client.loop_start()

for _ in range(50):
    if connected:
        break
    time.sleep(0.1)

if not connected:
    print("Could not connect. Check the endpoint, the certificate files and the IoT policy.")
else:
    reading = {
        "device_id": CLIENT_ID,
        "temperature": 21.5,
        "humidity": 55.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "laptop test",
    }
    print("Publishing to", topic)
    info = client.publish(topic, json.dumps(reading), qos=1)
    try:
        info.wait_for_publish(timeout=5)
    except (RuntimeError, ValueError) as error:
        print("Publish error:", error)
    if info.is_published():
        print("RESULT: AWS accepted the message on", topic)
    else:
        print("RESULT: AWS did NOT accept the message on", topic, "(blocked by the IoT policy)")

client.loop_stop()
client.disconnect()
