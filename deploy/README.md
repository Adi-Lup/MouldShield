# Deploy on AWS EC2 (T16)

This folder has what we need to run the MouldShield back-end on an EC2 server, so it works without our own computers being on.

| File | What it does |
|------|--------------|
| `mouldshield-api.service` | Runs the FastAPI back-end (port 8000, only reachable from inside the server for now) |
| `mouldshield-subscriber.service` | Runs the MQTT subscriber, which takes readings from AWS IoT Core and sends them to the back-end |

Both run as the normal `ubuntu` user, start by themselves when the server boots and start again if they stop.

## The server

- EC2 `t3.micro`, Ubuntu 26.04 LTS, region eu-west-2 (London), the same region as IoT Core
- Security group `mouldshield-sg`: only SSH (port 22), only from the IP address of the Scrum Master
- Python 3.14, the same version we use on our own computers

## One-time setup (already done on 27 October)

1. Update the server and install Python venv and Git: `sudo apt update`, `sudo apt upgrade -y`, `sudo apt install -y python3-venv git`.
2. Clone the repository to `~/mouldshield`, then create `backend/.venv` and run `pip install -r requirements.txt`.
3. Create `~/Projects/mouldshield-certs` (`chmod 700`) and copy only the three subscriber files into it with `scp`: `AmazonRootCA1.pem`, `subscriber-cert.pem.crt` and `subscriber-private.pem.key` (`chmod 600`). The device files never go on the server.

## Install the services

On the server:

```
sudo cp ~/mouldshield/deploy/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mouldshield-api mouldshield-subscriber
```

`daemon-reload` tells Linux to read the new files, and `enable --now` starts the services now and at every boot.

## Check that it works

```
systemctl status mouldshield-api mouldshield-subscriber
journalctl -u mouldshield-subscriber -f
```

The second command shows the subscriber log live. With the device on, a "Saved ..." line should appear every 15 seconds. Press Ctrl+C to leave the log (the service keeps running).

## Update the code

```
cd ~/mouldshield
git pull
sudo systemctl restart mouldshield-api mouldshield-subscriber
```

If `requirements.txt` changed, run `backend/.venv/bin/pip install -r backend/requirements.txt` before the restart. If a `.service` file changed, copy it again and run `sudo systemctl daemon-reload`.

## Important

- **Only one subscriber at a time.** All copies use the same client ID, and AWS IoT Core disconnects the old one when a new one connects. While the server runs, do not start `mqtt_subscriber.py` on a laptop or PC. To test locally, stop the server one first with `sudo systemctl stop mouldshield-subscriber`.
- **Stop the server when we do not need it** (risk R7). After a stop and start, AWS gives the server a new public IP address, so the SSH command changes.
- No AWS access keys and no `.env` with secrets on the server. When the back-end needs Bedrock or S3, the server gets an IAM role instead.
