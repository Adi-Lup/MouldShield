# Deploy on AWS EC2 (T16)

This folder has what we need to run the MouldShield back-end on an EC2 server, so it works without our own computers being on.

| File | What it does |
|------|--------------|
| `mouldshield-api.service` | Runs `backend/server.py` on port 80: the dashboard at `/` and the API from `main.py` under `/api` |
| `mouldshield-subscriber.service` | Runs the MQTT subscriber, which takes readings from AWS IoT Core and sends them to the back-end |

Both run as the normal `ubuntu` user, start by themselves when the server boots and start again if they stop.

## The server

- EC2 `t3.micro`, Ubuntu 26.04 LTS, region eu-west-2 (London), the same region as IoT Core
- Fixed address (Elastic IP): `3.9.91.235`, so the address and the QR code stay the same after a stop and start
- Security group `mouldshield-sg`: SSH (port 22) only from the IP address of the Scrum Master, and HTTP (port 80) only from CloudFront (the AWS prefix list `com.amazonaws.global.cloudfront.origin-facing`)
- Python 3.14, the same version we use on our own computers

## One-time setup (already done on 27 October)

1. Update the server and install Python venv and Git: `sudo apt update`, `sudo apt upgrade -y`, `sudo apt install -y python3-venv git`.
2. Clone the repository to `~/mouldshield`, then create `backend/.venv` and run `pip install -r requirements.txt`.
3. Create `~/Projects/mouldshield-certs` (`chmod 700`) and copy only the three subscriber files into it with `scp`: `AmazonRootCA1.pem`, `subscriber-cert.pem.crt` and `subscriber-private.pem.key` (`chmod 600`). The device files never go on the server.

## HTTPS with CloudFront

People open the dashboard at **https://d15ad8kcnyn7ke.cloudfront.net**. CloudFront gives us HTTPS with a free AWS certificate, so Chrome does not show the "not secure" warning, and we do not need to buy a domain.

| Setting | Our choice | Why |
|---------|------------|-----|
| Billing | Pay-as-you-go | Always-free tier (1 TB and 10 million requests a month), no monthly fee |
| Origin | `ec2-3-9-91-235.eu-west-2.compute.amazonaws.com`, HTTP only, port 80 | The server only speaks HTTP. HTTPS is between the user and CloudFront |
| Viewer protocol | Redirect HTTP to HTTPS | Nobody uses the dashboard without HTTPS |
| Allowed methods | GET, HEAD | Same rule as `server.py`: from outside you can only read |
| Cache policy | CachingDisabled | The readings change every 15 seconds, so nothing is cached |
| Response headers | SecurityHeadersPolicy | Adds browser security headers (for example HSTS) for free |
| WAF | Not enabled | It would cost about $14 a month. Logged as a risk and as future work |

Because port 80 on the server only accepts CloudFront, `http://3.9.91.235` does not open from the internet any more. This was tested on 27 October.

## What people can do from outside

Anyone can open the dashboard and read the data (`/api/readings/latest`, `/api/verify`, Swagger at `/api/docs`). Anything that would change data (POST, PUT, DELETE) is blocked by `backend/server.py` unless it comes from inside the server.

So a reading can only get into the database one way: device, then AWS IoT Core, then the subscriber on the server. Nobody on the internet can add fake readings to the hash chain.

For now this also blocks `POST /api/report`, so the report button will not work on the server yet. When T13 is ready we need two changes: allow that route in `server.py` with a limit (every report calls Bedrock and costs money), and change the allowed methods in CloudFront to include POST.

`main.py` is not changed, so on our own computers we still run `uvicorn main:app` and the dashboard with `run.py`, as before.

## Install the services

On the server:

```
sudo cp ~/mouldshield/deploy/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mouldshield-api mouldshield-subscriber
```

`daemon-reload` tells Linux to read the new files, and `enable --now` starts the services now and at every boot.

## Check that it works

Open https://d15ad8kcnyn7ke.cloudfront.net in a browser. The dashboard should show the latest real reading, not sample data.

On the server:

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

## Backup if the device breaks (risk R1)

Only if the device really stops working, run the data simulator on the server through SSH:

```
cd ~/mouldshield/backend
MOULDSHIELD_API_URL=http://127.0.0.1/api/readings .venv/bin/python simulator.py
```

It sends a reading every 5 seconds as `simulator-01`, and the dashboard shows them straight away. Press Ctrl+C to stop it. Do not run it just to test: its readings go into the same database and hash chain as the real ones, and they cannot be taken out.

## Important

- **Only one subscriber at a time.** All copies use the same client ID, and AWS IoT Core disconnects the old one when a new one connects. While the server runs, do not start `mqtt_subscriber.py` on a laptop or PC. To test locally, stop the server one first with `sudo systemctl stop mouldshield-subscriber`.
- **Stop the server when we do not need it** (risk R7). The Elastic IP keeps the same address after a stop and start.
- No AWS access keys and no `.env` with secrets on the server. When the back-end needs Bedrock or S3, the server gets an IAM role instead.
