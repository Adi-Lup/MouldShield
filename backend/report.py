# report.py - T13: POST /report, the explanation and the letter to the landlord
#
# The dashboard sends the id of a reading and a language (en, ro or pl). We answer with:
#   explanation  a short explanation of the risk in that language (Claude Haiku on Bedrock)
#   letter       the letter to the landlord, in English, filled in from the database
#
# The numbers always come from our database, never from the request, so the letter
# cannot be filled in with made-up readings.
#
# If Bedrock is not available (on our own computers without AWS, or if it fails), or the
# daily limit is reached, the explanation is a fixed text in the same language, so the
# report always works.

import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from hash_chain import verify_chain
from report_text import (LANGUAGES, TIME_FORMAT, build_letter, clean_answer,
                         explanation_prompt, fixed_explanation, parse_time, week_stats)
from risk import risk_level

DB_FILE = "mouldshield.db"
REGION = "eu-west-2"
MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"

# At most this many calls to Bedrock in any 24 hours, so nobody can use the
# report to spend our AWS credit. After that the fixed text is used.
MAX_AI_PER_24H = 50

router = APIRouter()

# The Bedrock client is made the first time it is needed. The tests put a fake one here.
clients = {}


def bedrock():
    if "bedrock" not in clients:
        import boto3
        from botocore.config import Config
        clients["bedrock"] = boto3.client(
            "bedrock-runtime", region_name=REGION,
            config=Config(connect_timeout=5, read_timeout=20, retries={"max_attempts": 1}),
        )
    return clients["bedrock"]


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS report_explanations (
            reading_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            explanation TEXT NOT NULL,
            PRIMARY KEY (reading_id, language)
        )
        """
    )
    conn.execute("CREATE TABLE IF NOT EXISTS report_ai_calls (at TEXT NOT NULL)")
    return conn


class ReportError(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def ask_ai(latest, stats, language):
    answer = bedrock().converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": explanation_prompt(latest, stats, language)}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.2},
    )
    return clean_answer(answer["output"]["message"]["content"][0]["text"])


def explanation_for(conn, latest, stats, language):
    # 1. Already made for this reading and language? Then we do not pay for it again
    #    (the dashboard asks again each time the tenant changes the language).
    saved = conn.execute(
        "SELECT explanation FROM report_explanations WHERE reading_id = ? AND language = ?",
        (latest["id"], language),
    ).fetchone()
    if saved:
        return saved[0], "ai"

    # 2. Daily limit on calls to Bedrock
    now = datetime.now(timezone.utc)
    since = (now - timedelta(hours=24)).strftime(TIME_FORMAT)
    calls = conn.execute("SELECT COUNT(*) FROM report_ai_calls WHERE at > ?", (since,)).fetchone()[0]
    if calls < MAX_AI_PER_24H:
        conn.execute("INSERT INTO report_ai_calls (at) VALUES (?)", (now.strftime(TIME_FORMAT),))
        conn.commit()
        try:
            text = ask_ai(latest, stats, language)
        except Exception:
            text = None
        if text:
            conn.execute(
                "INSERT OR REPLACE INTO report_explanations (reading_id, language, explanation) "
                "VALUES (?, ?, ?)", (latest["id"], language, text))
            conn.commit()
            return text, "ai"

    # 3. Fixed text in the same language
    return fixed_explanation(latest["humidity_pct"], language), "fixed"


def make_report(reading_id, language, today=None):
    if language not in LANGUAGES:
        raise ReportError(422, "language must be en, ro or pl")

    conn = get_db()
    try:
        try:
            row = conn.execute(
                "SELECT id, device_id, timestamp, temperature_c, humidity_pct FROM readings WHERE id = ?",
                (reading_id,),
            ).fetchone()
        except sqlite3.OperationalError:
            # A new database with no readings table yet
            row = None
        if row is None:
            raise ReportError(404, "reading not found")
        latest = dict(zip(("id", "device_id", "timestamp", "temperature_c", "humidity_pct"), row))

        # The 7 days up to this reading, for the same device
        end = parse_time(latest["timestamp"])
        start = (end - timedelta(days=7)).strftime(TIME_FORMAT)
        week = conn.execute(
            "SELECT timestamp, humidity_pct FROM readings "
            "WHERE device_id = ? AND timestamp > ? AND timestamp <= ?",
            (latest["device_id"], start, latest["timestamp"]),
        ).fetchall()
        stats = week_stats(week, end)

        # The same check as GET /verify, so the letter only says "unchanged" when it is true
        chain = conn.execute(
            "SELECT id, device_id, timestamp, temperature_c, humidity_pct, prev_hash, hash "
            "FROM readings ORDER BY id"
        ).fetchall()
        check = verify_chain(chain)

        explanation, source = explanation_for(conn, latest, stats, language)
    finally:
        conn.close()

    return {
        "explanation": explanation,
        "explanation_source": source,
        "letter": build_letter(latest, stats, check, today or datetime.now(timezone.utc)),
        "risk": risk_level(latest["humidity_pct"]),
        "reading_id": latest["id"],
    }


class ReportRequest(BaseModel):
    # The dashboard also sends the reading itself; we only use its id and read the rest
    # from the database. Other fields are ignored.
    id: int
    language: str = "en"


@router.post("/report")
def create_report(request: ReportRequest):
    try:
        return make_report(request.id, request.language)
    except ReportError as error:
        raise HTTPException(status_code=error.status, detail=error.detail)
