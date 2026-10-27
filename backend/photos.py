# photos.py - T18: photo evidence of damp and mould
# A tenant uploads a photo from the report page. The server turns it into a clean JPEG
# with no hidden data, keeps a few details as evidence, asks Claude Haiku 4.5 on
# Amazon Bedrock for a short description, and saves the JPEG in a private S3 bucket.
# It only runs on the EC2 server (see server.py), because it needs the AWS role of the server.

import hashlib
import io
import json
import os
import sqlite3
import time
from datetime import datetime, timezone

import boto3
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

# Lets Pillow open HEIC photos, the default format on iPhones
register_heif_opener()

DB_FILE = "mouldshield.db"
BUCKET = os.environ.get("MOULDSHIELD_PHOTOS_BUCKET", "mouldshield-photos")
REGION = "eu-west-2"
MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PHOTOS_PER_DAY = 12
MAX_SIDE = 1568
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "HEIF"}

# Refuse very large images, so one upload cannot use up the memory of our small server
Image.MAX_IMAGE_PIXELS = 60_000_000

PROMPT = (
    "This photo was uploaded by a tenant as evidence for a damp and mould report. "
    "Answer with JSON only, in this form: "
    '{"damp_visible": true or false, "description": "..."}. '
    "damp_visible is true only if you can see damp, mould, condensation, water stains or peeling paint. "
    "The description is 2 or 3 short sentences of plain British English that describe only what you can see "
    "and where it is (for example wall, ceiling or window frame). Do not guess the cause, do not give a "
    "diagnosis and do not mention health. If the photo does not show a room or a surface, or you cannot see "
    "any damp or mould, say so clearly in the description."
)

# When AI sees no damp, the photo waits here until the tenant decides. If they press
# "Yes, add it", we use this result again, so we do not pay Bedrock twice for one photo.
PENDING_MINUTES = 15
pending = {}

router = APIRouter()

# The AWS clients are made the first time they are needed. The tests put fake ones here,
# so they never call the real AWS.
clients = {}


def s3():
    if "s3" not in clients:
        clients["s3"] = boto3.client("s3", region_name=REGION)
    return clients["s3"]


def bedrock():
    if "bedrock" not in clients:
        clients["bedrock"] = boto3.client("bedrock-runtime", region_name=REGION)
    return clients["bedrock"]


def get_db():
    # Same database file as the readings, but a separate table
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uploaded_at TEXT NOT NULL,
            s3_key TEXT NOT NULL,
            original_sha256 TEXT NOT NULL,
            jpeg_sha256 TEXT NOT NULL,
            taken_at TEXT,
            camera TEXT,
            gps_lat REAL,
            gps_lon REAL,
            description TEXT NOT NULL,
            record_hash TEXT NOT NULL
        )
        """
    )
    # Every call to Bedrock is counted here, also for photos the tenant does not keep,
    # so the daily limit really protects our AWS credit
    conn.execute("CREATE TABLE IF NOT EXISTS photo_attempts (at TEXT NOT NULL)")
    return conn


class PhotoOut(BaseModel):
    # The ONLY fields the API ever sends back. The GPS location is private evidence:
    # it is saved in the database but must never be added here (the tests check this).
    id: int
    uploaded_at: str
    taken_at: str | None
    camera: str | None
    description: str
    days_before_upload: int | None
    jpeg_sha256: str
    image_url: str


def gps_to_decimal(values, ref):
    # EXIF keeps GPS as degrees, minutes and seconds. We turn it into one number.
    try:
        degrees, minutes, seconds = (float(v) for v in values)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    number = degrees + minutes / 60 + seconds / 3600
    if ref in ("S", "W"):
        number = -number
    return round(number, 6)


def read_details(img):
    # Reads the date, the phone and the location from the hidden data in the photo (EXIF).
    # Anyone can edit EXIF, so this is only context. The strong evidence is the
    # SHA-256 of the uploaded file and the upload time from our own server.
    exif = img.getexif()
    parts = [str(exif.get(tag, "")).replace("\x00", "").strip() for tag in (271, 272)]
    camera = " ".join(p for p in parts if p) or None

    taken = exif.get_ifd(0x8769).get(36867) or exif.get(306)
    taken_at = None
    if taken:
        try:
            taken_at = datetime.strptime(str(taken).strip(), "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            taken_at = None

    gps = exif.get_ifd(0x8825)
    lat = gps_to_decimal(gps.get(2), gps.get(1)) if gps else None
    lon = gps_to_decimal(gps.get(4), gps.get(3)) if gps else None
    return taken_at, camera, lat, lon


def clean_jpeg(img):
    # Turns the photo the right way up, makes it smaller and saves it as a JPEG.
    # We do not pass the EXIF on, so the saved file has no hidden data at all.
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=85)
    return out.getvalue()


def read_answer(text):
    # The model should answer with JSON. If it does not, we keep its text and treat the
    # photo as relevant, so a tenant is never blocked because of a badly formatted answer.
    start, end = text.find("{"), text.rfind("}")
    try:
        data = json.loads(text[start:end + 1])
        description = str(data["description"]).strip()
        if description:
            return bool(data["damp_visible"]), description
    except (ValueError, KeyError, TypeError):
        pass
    return True, text.strip()


def describe(jpeg):
    answer = bedrock().converse(
        modelId=MODEL_ID,
        messages=[{
            "role": "user",
            "content": [
                {"image": {"format": "jpeg", "source": {"bytes": jpeg}}},
                {"text": PROMPT},
            ],
        }],
        inferenceConfig={"maxTokens": 300, "temperature": 0},
    )
    return read_answer(answer["output"]["message"]["content"][0]["text"])


def record_hash(record):
    # Same idea as the readings hash chain: if anyone changes a saved photo record
    # (including the private location), this hash no longer matches.
    text = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def days_before(taken_at, uploaded_at):
    if not taken_at:
        return None
    taken = datetime.strptime(taken_at[:10], "%Y-%m-%d").date()
    uploaded = datetime.strptime(uploaded_at[:10], "%Y-%m-%d").date()
    return (uploaded - taken).days


def to_public(row):
    photo_id, uploaded_at, taken_at, camera, description, jpeg_sha256 = row
    return PhotoOut(
        id=photo_id,
        uploaded_at=uploaded_at,
        taken_at=taken_at,
        camera=camera,
        description=description,
        days_before_upload=days_before(taken_at, uploaded_at),
        jpeg_sha256=jpeg_sha256,
        image_url=f"/photos/{photo_id}/image",
    )


PUBLIC_COLUMNS = "id, uploaded_at, taken_at, camera, description, jpeg_sha256"


def analyse(body):
    # Everything slow happens here (image work and the Bedrock call), outside the web loop
    try:
        img = Image.open(io.BytesIO(body))
        img.load()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
        raise HTTPException(status_code=415, detail="Please upload a photo (JPG, PNG, WebP or HEIC).")
    if img.format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=415, detail="Please upload a photo (JPG, PNG, WebP or HEIC).")

    taken_at, camera, lat, lon = read_details(img)
    jpeg = clean_jpeg(img)

    conn = get_db()
    conn.execute("INSERT INTO photo_attempts (at) VALUES (?)", (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),))
    conn.commit()
    conn.close()
    try:
        damp_visible, description = describe(jpeg)
    except Exception:
        raise HTTPException(status_code=502, detail="The photo description is not available right now. Please try again.")

    return {
        "original_sha256": hashlib.sha256(body).hexdigest(),
        "jpeg": jpeg,
        "taken_at": taken_at,
        "camera": camera,
        "gps_lat": lat,
        "gps_lon": lon,
        "description": description,
        "damp_visible": damp_visible,
    }


def save(result):
    # Puts the clean JPEG in S3 and returns the record for the database
    uploaded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    jpeg_sha256 = hashlib.sha256(result["jpeg"]).hexdigest()
    s3_key = f"photos/{uploaded_at.replace(':', '-')}-{jpeg_sha256[:12]}.jpg"
    s3().put_object(Bucket=BUCKET, Key=s3_key, Body=result["jpeg"], ContentType="image/jpeg")

    record = {
        "uploaded_at": uploaded_at,
        "s3_key": s3_key,
        "original_sha256": result["original_sha256"],
        "jpeg_sha256": jpeg_sha256,
        "taken_at": result["taken_at"],
        "camera": result["camera"],
        "gps_lat": result["gps_lat"],
        "gps_lon": result["gps_lon"],
        "description": result["description"],
    }
    record["record_hash"] = record_hash(record)
    return record


def clean_pending():
    now = time.time()
    for key in [k for k, (expires, _) in pending.items() if expires < now]:
        del pending[key]


@router.post("/photos", status_code=201, response_model=PhotoOut)
async def upload_photo(request: Request, confirm: bool = False):
    # confirm=true means the tenant pressed "Yes, add it" after AI saw no damp
    length = request.headers.get("content-length", "0")
    if not length.isdigit() or int(length) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="The photo is too big (15 MB at most).")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="No photo received.")
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="The photo is too big (15 MB at most).")

    clean_pending()
    original_sha256 = hashlib.sha256(body).hexdigest()
    result = pending.pop(original_sha256, (0, None))[1] if confirm else None

    if result is None:
        # Daily limit on calls to Bedrock, so nobody can use the upload to spend our AWS credit
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM photo_attempts WHERE at LIKE ?", (today + "%",)).fetchone()[0]
        conn.close()
        if count >= MAX_PHOTOS_PER_DAY:
            raise HTTPException(status_code=429, detail=f"The limit of {MAX_PHOTOS_PER_DAY} photos a day has been reached. Please try again tomorrow.")
        result = await run_in_threadpool(analyse, body)

        if not result["damp_visible"] and not confirm:
            # Nothing is saved yet: the tenant decides if this photo should be evidence
            if len(pending) >= 20:
                pending.pop(next(iter(pending)))
            pending[original_sha256] = (time.time() + PENDING_MINUTES * 60, result)
            return JSONResponse({"saved": False, "needs_confirmation": True, "description": result["description"]})

    record = await run_in_threadpool(save, result)
    conn = get_db()
    columns = ", ".join(record)
    marks = ", ".join("?" for _ in record)
    cursor = conn.execute(f"INSERT INTO photos ({columns}) VALUES ({marks})", tuple(record.values()))
    conn.commit()
    row = conn.execute(f"SELECT {PUBLIC_COLUMNS} FROM photos WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return to_public(row)


@router.get("/photos", response_model=list[PhotoOut])
def list_photos():
    conn = get_db()
    rows = conn.execute(f"SELECT {PUBLIC_COLUMNS} FROM photos ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return [to_public(row) for row in rows]


@router.get("/photos/{photo_id}/image")
def photo_image(photo_id: int):
    conn = get_db()
    row = conn.execute("SELECT s3_key, jpeg_sha256 FROM photos WHERE id = ?", (photo_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Photo not found.")
    s3_key, jpeg_sha256 = row
    jpeg = s3().get_object(Bucket=BUCKET, Key=s3_key)["Body"].read()
    # Check the photo in S3 is still exactly the one we saved
    if hashlib.sha256(jpeg).hexdigest() != jpeg_sha256:
        raise HTTPException(status_code=409, detail="This photo was changed after it was uploaded.")
    return Response(content=jpeg, media_type="image/jpeg")
