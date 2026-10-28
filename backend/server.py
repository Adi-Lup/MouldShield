# server.py - T16: how the back-end runs on the EC2 server.
# It does not change main.py. It puts the API under /api, serves the
# dashboard from the same address, and blocks changes coming from outside.
# On our own computers we still use "uvicorn main:app" as before.

import re
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from main import app as api
from photos import router as photos_router

# T18: the photo routes join the API from main.py, so they are under /api too
api.include_router(photos_router)

DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard"

# Link preview: what Teams, WhatsApp or LinkedIn show when someone shares our link.
# The tags are added to the page here, like photos.js, so the dashboard's index.html is not changed.
# The image must be a full https address, and PNG, because link previews do not show SVG.
SITE = "https://d15ad8kcnyn7ke.cloudfront.net"
PREVIEW_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "og-image.png"
PREVIEW_TITLE = "MouldShield · Your home, in view"
PREVIEW_TEXT = ("Live damp and mould readings from a low-cost sensor, with tamper-evident "
                "evidence for tenants. A student project by THE SHARKS.")
PREVIEW_TAGS = (
    f'<meta property="og:type" content="website">'
    f'<meta property="og:url" content="{SITE}/">'
    f'<meta property="og:title" content="{PREVIEW_TITLE}">'
    f'<meta property="og:description" content="{PREVIEW_TEXT}">'
    f'<meta property="og:image" content="{SITE}/og-image.png">'
    f'<meta property="og:image:width" content="1200">'
    f'<meta property="og:image:height" content="630">'
    f'<meta property="og:image:alt" content="MouldShield logo, by THE SHARKS">'
    f'<meta name="twitter:card" content="summary_large_image">'
)

# Requests from these addresses come from inside the server (the subscriber)
INSIDE = {"127.0.0.1", "::1"}

# Methods anyone may use from outside: only reading, never changing data.
READ_ONLY = {"GET", "HEAD"}

# The only POST requests allowed from outside:
# - a tenant adding a photo (T18). photos.py checks the file and keeps to 20 photos in 24 hours.
# - a tenant asking for the report (T13). It saves no readings, and report.py keeps to
#   50 calls to Bedrock in 24 hours (after that it uses the fixed text), so it cannot be
#   used to spend our credit.
OPEN_FOR_WRITING = {("POST", "/api/photos"), ("POST", "/api/report")}

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def outside_can_only_read(request: Request, call_next):
    # A reading can only be saved by the subscriber on this server.
    # From the internet, only GET and HEAD are allowed (plus the photo upload above),
    # so nobody can add fake readings.
    client = request.client.host if request.client else ""
    allowed = request.method in READ_ONLY or (request.method, request.url.path) in OPEN_FOR_WRITING
    if not allowed and client not in INSIDE:
        return JSONResponse({"detail": "Read only from outside the server"}, status_code=403)
    return await call_next(request)


@app.get("/config.js", include_in_schema=False)
def dashboard_config():
    # Same config.js as in the dashboard folder, but the dashboard starts in live mode,
    # so people who open the page see the real readings, not the sample data.
    # The pattern still works if the spaces or quotes in config.js change.
    text = (DASHBOARD / "config.js").read_text(encoding="utf-8")
    text = re.sub(r"mode\s*:\s*['\"]demo['\"]", "mode: 'live'", text, count=1)
    return Response(text, media_type="application/javascript")


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
@app.api_route("/index.html", methods=["GET", "HEAD"], include_in_schema=False)
def dashboard_page():
    # Same index.html as in the dashboard folder, plus photos.js for the photo evidence
    # on the report page (T18). The dashboard files themselves are not changed.
    html = (DASHBOARD / "index.html").read_text(encoding="utf-8")
    html = html.replace("</body>", '<script src="photos.js"></script></body>', 1)
    # The old description says "sample data", but this page shows the live readings
    html = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{PREVIEW_TEXT}">', html, count=1)
    html = html.replace("</head>", PREVIEW_TAGS + "</head>", 1)
    return HTMLResponse(html)


@app.api_route("/og-image.png", methods=["GET", "HEAD"], include_in_schema=False)
def preview_image():
    # The picture shown in link previews: our logo on a white background, 1200 x 630
    return FileResponse(PREVIEW_IMAGE, media_type="image/png")


# The API from main.py, under /api (the dashboard already calls /api/...)
app.mount("/api", api)

# The dashboard pages, last, so they do not hide the routes above
app.mount("/", StaticFiles(directory=DASHBOARD, html=True), name="dashboard")
