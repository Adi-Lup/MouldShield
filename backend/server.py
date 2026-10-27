# server.py - T16: how the back-end runs on the EC2 server.
# It does not change main.py. It puts the API under /api, serves the
# dashboard from the same address, and blocks changes coming from outside.
# On our own computers we still use "uvicorn main:app" as before.

import re
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from main import app as api

DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard"

# Requests from these addresses come from inside the server (the subscriber)
INSIDE = {"127.0.0.1", "::1"}

# Methods anyone may use from outside: only reading, never changing data.
# This also blocks POST /api/report for now. When T13 is ready we allow that
# one route here, with a limit, because every report calls Bedrock and costs money.
READ_ONLY = {"GET", "HEAD"}

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def outside_can_only_read(request: Request, call_next):
    # A reading can only be saved by the subscriber on this server.
    # From the internet, only GET and HEAD are allowed, so nobody can add fake readings.
    client = request.client.host if request.client else ""
    if request.method not in READ_ONLY and client not in INSIDE:
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


# The API from main.py, under /api (the dashboard already calls /api/...)
app.mount("/api", api)

# The dashboard pages, last, so they do not hide the routes above
app.mount("/", StaticFiles(directory=DASHBOARD, html=True), name="dashboard")
