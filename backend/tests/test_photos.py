"""T18 tests for the photo evidence. They use fake S3 and Bedrock clients, so they never
call the real AWS, and a temporary database, so they never touch the real one.
Run from the backend folder: python -m unittest discover tests"""

import hashlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
register_heif_opener()

# Test location: somewhere in Watford. It must never come back from the API.
LAT, LON = 51.656789, -0.398765


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.objects[Key] = Body

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.objects[Key])}


class FakeBedrock:
    # By default it "sees" mould. A test can change self.answer to try other replies.
    def __init__(self):
        self.calls = 0
        self.answer = '{"damp_visible": true, "description": "Dark spots of mould in the top corner of the wall."}'

    def converse(self, **kwargs):
        self.calls += 1
        return {"output": {"message": {"content": [{"text": self.answer}]}}}


def dms(value):
    value = abs(value)
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = round(((value - degrees) * 60 - minutes) * 60, 4)
    return (degrees, minutes, seconds)


def make_photo(fmt="JPEG", size=(3000, 2000), gps=True, orientation=None, taken="2026:10:20 09:30:00"):
    img = Image.new("RGB", size, (120, 140, 110))
    exif = Image.Exif()
    exif[271] = "Apple"
    exif[272] = "iPhone 15"
    if orientation:
        exif[274] = orientation
    exif.get_ifd(0x8769)[36867] = taken
    if gps:
        g = exif.get_ifd(0x8825)
        g[1], g[2] = "N", dms(LAT)
        g[3], g[4] = "W", dms(LON)
    out = io.BytesIO()
    img.save(out, fmt, exif=exif.tobytes())
    return out.getvalue()


class PhotoTests(unittest.TestCase):
    def setUp(self):
        self.old_dir = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)  # mouldshield.db is created here, not in the real folder
        import photos
        import server
        from fastapi.testclient import TestClient
        self.photos = photos
        self.s3, self.bedrock = FakeS3(), FakeBedrock()
        photos.clients.clear()
        photos.clients.update({"s3": self.s3, "bedrock": self.bedrock})
        self.client = TestClient(server.app)  # the test client counts as "outside"

    def tearDown(self):
        os.chdir(self.old_dir)
        self.tmp.cleanup()

    def upload(self, data, content_type="image/jpeg"):
        return self.client.post("/api/photos", content=data, headers={"Content-Type": content_type})

    def test_heic_from_iphone_is_accepted_and_stored_as_clean_jpeg(self):
        original = make_photo("HEIF")
        r = self.upload(original, "image/heic")
        self.assertEqual(r.status_code, 201, r.text)
        photo = r.json()
        self.assertEqual(photo["camera"], "Apple iPhone 15")
        self.assertEqual(photo["taken_at"], "2026-10-20T09:30:00")
        stored = list(self.s3.objects.values())[0]
        img = Image.open(io.BytesIO(stored))
        self.assertEqual(img.format, "JPEG")
        self.assertLessEqual(max(img.size), 1568)
        self.assertEqual(len(img.getexif()), 0, "the JPEG in S3 must have no hidden data")
        self.assertEqual(photo["jpeg_sha256"], hashlib.sha256(stored).hexdigest())

    def test_gps_is_saved_privately_but_never_sent_back(self):
        r = self.upload(make_photo("JPEG"))
        self.assertEqual(r.status_code, 201, r.text)
        conn = self.photos.get_db()
        lat, lon = conn.execute("SELECT gps_lat, gps_lon FROM photos").fetchone()
        conn.close()
        self.assertAlmostEqual(lat, LAT, places=4)
        self.assertAlmostEqual(lon, LON, places=4)
        listing = self.client.get("/api/photos")
        schema = self.client.get("/api/openapi.json")
        for text in (r.text, listing.text, schema.text):
            self.assertNotIn("gps", text.lower())
            self.assertNotIn("51.65", text)
            self.assertNotIn("0.39", text)

    def test_png_and_webp_work_and_photo_without_exif_is_fine(self):
        for fmt, mime in (("PNG", "image/png"), ("WEBP", "image/webp")):
            img = Image.new("RGB", (800, 600), (200, 200, 200))
            out = io.BytesIO()
            img.save(out, fmt)
            r = self.upload(out.getvalue(), mime)
            self.assertEqual(r.status_code, 201, r.text)
            self.assertIsNone(r.json()["taken_at"])
            self.assertIsNone(r.json()["days_before_upload"])

    def test_phone_photo_is_turned_the_right_way_up(self):
        r = self.upload(make_photo("JPEG", size=(2000, 1000), orientation=6))
        self.assertEqual(r.status_code, 201, r.text)
        width, height = Image.open(io.BytesIO(list(self.s3.objects.values())[0])).size
        self.assertGreater(height, width)

    def test_old_photo_shows_days_before_upload(self):
        r = self.upload(make_photo("JPEG", taken="2020:01:01 10:00:00"))
        self.assertGreater(r.json()["days_before_upload"], 365)

    def test_not_a_photo_is_refused(self):
        r = self.upload(b"this is not an image", "image/jpeg")
        self.assertEqual(r.status_code, 415)
        self.assertEqual(self.bedrock.calls, 0)

    def test_too_big_is_refused_before_reading(self):
        r = self.client.post("/api/photos", content=b"x", headers={"Content-Length": str(20 * 1024 * 1024)})
        self.assertEqual(r.status_code, 413)

    def test_daily_limit_of_12(self):
        small = io.BytesIO()
        Image.new("RGB", (100, 100)).save(small, "JPEG")
        for _ in range(12):
            self.assertEqual(self.upload(small.getvalue()).status_code, 201)
        r = self.upload(small.getvalue())
        self.assertEqual(r.status_code, 429)
        self.assertEqual(self.bedrock.calls, 12)

    def test_image_route_checks_the_photo_was_not_changed(self):
        r = self.upload(make_photo("JPEG"))
        url = "/api" + r.json()["image_url"]
        self.assertEqual(self.client.get(url).status_code, 200)
        key = list(self.s3.objects)[0]
        self.s3.objects[key] = self.s3.objects[key] + b"changed"
        self.assertEqual(self.client.get(url).status_code, 409)

    def test_outside_can_still_not_add_readings(self):
        reading = {"device_id": "x", "timestamp": "2026-10-27T12:00:00Z", "temperature_c": 1, "humidity_pct": 1}
        self.assertEqual(self.client.post("/api/readings", json=reading).status_code, 403)
        self.assertEqual(self.client.post("/api/photos/", content=b"x").status_code, 403)
        self.assertEqual(self.client.delete("/api/photos").status_code, 403)

    def test_no_damp_asks_the_tenant_and_saves_nothing_yet(self):
        self.bedrock.answer = '{"damp_visible": false, "description": "A sofa. No damp or mould can be seen."}'
        r = self.upload(make_photo("JPEG"))
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json(), {"saved": False, "needs_confirmation": True, "description": "A sofa. No damp or mould can be seen."})
        self.assertEqual(self.s3.objects, {})
        self.assertEqual(self.client.get("/api/photos").json(), [])

    def test_yes_add_it_saves_without_asking_ai_again(self):
        self.bedrock.answer = '{"damp_visible": false, "description": "A clean white wall."}'
        photo = make_photo("JPEG")
        self.assertEqual(self.upload(photo).status_code, 200)
        r = self.client.post("/api/photos?confirm=true", content=photo, headers={"Content-Type": "image/jpeg"})
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["description"], "A clean white wall.")
        self.assertEqual(self.bedrock.calls, 1)
        self.assertEqual(len(self.s3.objects), 1)

    def test_answer_that_is_not_json_is_still_saved(self):
        self.bedrock.answer = "There is condensation on the window."
        r = self.upload(make_photo("JPEG"))
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["description"], "There is condensation on the window.")

    def test_photos_the_tenant_did_not_keep_count_for_the_daily_limit(self):
        self.bedrock.answer = '{"damp_visible": false, "description": "Nothing to see."}'
        small = io.BytesIO()
        Image.new("RGB", (100, 100)).save(small, "JPEG")
        for _ in range(12):
            self.assertEqual(self.upload(small.getvalue()).status_code, 200)
        self.assertEqual(self.upload(small.getvalue()).status_code, 429)

    def test_dashboard_page_gets_photos_script(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn('<script src="photos.js"></script></body>', page.text)
        self.assertEqual(self.client.get("/photos.js").status_code, 200)


if __name__ == "__main__":
    unittest.main()
