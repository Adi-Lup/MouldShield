# upload_certs.py - copies the AWS IoT certificate files from the computer to the MouldShield device over USB.
# The files go straight through the USB cable to /flash/certs on the device.
# They never go through UiFlow2 or any cloud, and they are never in the GitHub repo.
#
# Run from the project folder:  python device/upload_certs.py COM7
# Close UiFlow2 in the browser first, so the USB port is free.
import binascii
import sys
import time
from pathlib import Path

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "COM7"
CERTS = Path.home() / "Projects" / "mouldshield-certs"
FILES = {
    "device-cert.pem.crt": "/flash/certs/device-cert.pem.crt",
    "device-private.pem.key": "/flash/certs/device-private.pem.key",
    "AmazonRootCA1.pem": "/flash/certs/AmazonRootCA1.pem",
}


def read_for(port, seconds):
    end = time.time() + seconds
    data = b""
    while time.time() < end:
        chunk = port.read(port.in_waiting or 1)
        if chunk:
            data += chunk
    return data


def read_until(port, marker, seconds):
    end = time.time() + seconds
    data = b""
    while time.time() < end:
        chunk = port.read(port.in_waiting or 1)
        if chunk:
            data += chunk
            if data.endswith(marker):
                break
    return data


def run_raw(port, code):
    # Raw REPL: send the code, then Ctrl+D to run it. The device answers OK, the output, then \x04, errors, \x04 and >
    data = code.encode()
    for i in range(0, len(data), 256):
        port.write(data[i:i + 256])
        time.sleep(0.02)
    port.write(b"\x04")
    reply = read_until(port, b"\x04>", 10)
    if not reply.startswith(b"OK"):
        raise RuntimeError("Device did not accept the code: " + repr(reply[:200]))
    output, _, errors = reply[2:].partition(b"\x04")
    errors = errors.rstrip(b"\x04>")
    if errors:
        raise RuntimeError("Error on the device: " + errors.decode(errors="replace"))
    return output.decode(errors="replace").strip()


# Check that all files exist on the computer before touching the device
for name in FILES:
    if not (CERTS / name).exists():
        sys.exit("Missing file on the computer: " + str(CERTS / name))

port = serial.Serial()
port.port = PORT
port.baudrate = 115200
port.timeout = 0.1
port.dtr = False  # do not send the reset signals when the port opens
port.rts = False
port.open()
print("Port", PORT, "open. Output from the device for 2 seconds:")
print(read_for(port, 2).decode(errors="replace"))

print("Stopping the running program (Ctrl+C), up to 20 seconds...")
received = b""
for _ in range(40):
    port.write(b"\r\x03")
    received += read_for(port, 0.5)
    if b">>>" in received or b"raw REPL" in received:
        break
print(received.decode(errors="replace")[-400:])

# The device may now be in the normal REPL (>>>) or already in raw REPL (>).
# Ctrl+B always brings it back to the normal REPL, so we start from a known state.
port.write(b"\x02")
received += read_for(port, 1)
if b">>>" not in received:
    port.close()
    sys.exit("RESULT: no Python prompt from the device. Nothing was copied.")

port.write(b"\r\x01")  # Ctrl+A = raw REPL
reply = read_until(port, b"raw REPL; CTRL-B to exit\r\n>", 3)
if b"raw REPL" not in reply:
    port.close()
    sys.exit("RESULT: could not enter raw REPL. Nothing was copied. Reply: " + repr(reply[-200:]))

run_raw(port, "import os\ntry:\n    os.mkdir('/flash/certs')\nexcept OSError:\n    pass\n")

for name, destination in FILES.items():
    content = (CERTS / name).read_bytes()
    encoded = binascii.b2a_base64(content).decode().strip()
    code = (
        "import binascii\n"
        "f = open('" + destination + "', 'wb')\n"
        "f.write(binascii.a2b_base64('" + encoded + "'))\n"
        "f.close()\n"
        "print(len(open('" + destination + "', 'rb').read()))\n"
    )
    size_on_device = int(run_raw(port, code))
    status = "OK" if size_on_device == len(content) else "SIZE MISMATCH"
    print(destination, ":", size_on_device, "bytes on the device,", len(content), "on the computer ->", status)

print("Files in /flash/certs:", run_raw(port, "import os\nprint(os.listdir('/flash/certs'))\n"))
port.write(b"\x02")  # Ctrl+B = leave raw REPL
port.close()
print("RESULT: done. Restart the device with a short press on the side button.")
