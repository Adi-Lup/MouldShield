<p align="center">
  <img src="assets/logo-by-the-sharks.svg" alt="MouldShield logo" width="460">
</p>

# MouldShield

Early warning for damp and mould in rented homes, with tamper-evident readings.

CPU4106 Group Project, Fly-Tech internship scenario. Team **THE SHARKS**.

## What it does

- A small device (M5StickS3 with an ENV III sensor) measures temperature and humidity in a room.
- The readings are sent to the cloud and a web dashboard shows the risk as green, amber or red.
- AI explains the risk in plain words and writes a draft letter to the landlord.
- Every reading is linked to the one before it with a SHA-256 hash. If someone changes old data, the chain breaks and the dashboard shows "Tampered".

## SDGs

- SDG 3: Good health and well-being
- SDG 10: Reduced inequalities
- SDG 11: Sustainable cities and communities

## How it works

```
Device (M5StickS3 + ENV III)
        |  Wi-Fi, MQTT
        v
AWS IoT Core
        |
        v
FastAPI back-end + SQL database (on AWS)  <---  Open-Meteo forecast
        |                    ^
        |                    |
        |              Amazon Bedrock (explanation, letter, photo description)
        v
Web dashboard (laptop and phones, QR code)  --->  PDF report + letter to landlord
```

## Repository structure

| Folder | What goes in it |
|--------|-----------------|
| `backend/` | FastAPI app, database, risk calculation, hash chain, AI and forecast logic, data simulator |
| `device/` | MicroPython code for the M5StickS3 (UiFlow2 firmware) |
| `dashboard/` | Web dashboard and mobile page |
| `docs/` | Product backlog, stand-up records, sprint reviews, diagrams (Use Case, DFD), test plan and results |

## Tech stack

- Device: MicroPython on UiFlow2 firmware
- Back-end: Python, FastAPI, SQL database
- Cloud: AWS IoT Core, Amazon Bedrock, Amazon S3
- Weather: Open-Meteo
- Project management: GitHub Projects (Scrum board)

## Running the back-end locally

The back-end code is added in task 7. Once `backend/main.py` exists:

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead.

Then open http://127.0.0.1:8000/docs to test the endpoints.

Copy `.env.example` to `.env` in the project root and fill in your own values. The `.env` file is never committed.

## Planned endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/readings` | Save a new reading and calculate the risk level |
| GET | `/readings/latest` | Return the most recent reading |
| POST | `/report` | Create the AI explanation and the landlord letter |
| GET | `/verify` | Check the hash chain and report "OK" or "Tampered" |

## Team

| Name | Role |
|------|------|
| Adrian Lupescu | Scrum Master, developer (cloud and security) |
| Sergiu Girnita | Developer (back-end and AI) |
| Claudiu Stratulat | UI/UX Designer, developer (front-end and testing) |

## How we work

- Tasks live on the GitHub Projects board: To do, In progress, Done. Each feature task has a MoSCoW label (Must or Should) and a Sprint value.
- The product backlog (user stories, MoSCoW, sprint goals and Definition of Done) is in `docs/agile/product_backlog.md`, and the risk register in `docs/agile/risk_register.md`.
- Each task is done on its own branch, for example `task-7-fastapi`.
- Changes go into `main` through a pull request, checked by one teammate.
- Commit messages are short and mention the task number, for example `#7 add POST /readings`.
- A task is Done when the code is on GitHub, tested, and checked by one teammate.
- Stand-up notes (attendance and decisions), sprint reviews and retrospectives are kept in `docs/standups/`.

## Security

- Keys, passwords and device certificates are never committed. They stay in `.env` or in ignored files (see `.gitignore`).
- Each team member has their own IAM user on AWS with MFA. The root account is not used for daily work.
- A budget alert is set on the AWS account.

## Limitations

- Letters created by MouldShield are drafts, not legal advice.
- AI describes photos of damp and mould. It does not diagnose anything.

## Credits

Weather data by [Open-Meteo.com](https://open-meteo.com/) (CC BY 4.0).
