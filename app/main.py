# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import os
import requests

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"error": "Too many requests"})

# === CORS SETUP ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gilded-seahorse-172ddf.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# === HubSpot Config ===
HUBSPOT_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
HUBSPOT_CONTACT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

# === Lead Scoring Logic ===
def score_lead(lead: dict):
    score = 0
    if lead.get("homeowner"):
        score += 30
    timeline = lead.get("timeline_months")
    if timeline and timeline <= 6:
        score += 40
    if lead.get("city") in ["Boston", "Cambridge", "Newton", "Wellesley"]:
        score += 30
    return score

# === HubSpot Submission ===
def send_to_hubspot(payload):
    token = os.getenv("HUBSPOT_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    properties = {
        "email": payload["email"],
        "firstname": payload["first_name"],
        "buyer_lead_score": payload["score"],
        "timeline_months": payload["timeline_months"],
        "is_homeowner": payload["homeowner"],
        "target_city": payload["city"],
        "property_interest": "19 Castle Rd, Narragansett RI"
    }

    res = requests.post(
        "https://api.hubapi.com/crm/v3/objects/contacts",
        json={"properties": properties},
        headers=headers
    )

    return res.json()

# === FastAPI Endpoint ===

@app.post("/event")
@limiter.limit("5/minute")
async def receive_lead(request: Request):
    data = await request.json()
    payload = data.get("payload")

    if not payload:
        return {"error": "No payload received"}

    # Honeypot check
    if payload.get("company"):
        return {"status": "ignored"}

    # Required fields
    for field in ["email", "first_name", "city"]:
        if not payload.get(field):
            return {"error": f"Missing field: {field}"}

    payload["score"] = score_lead(payload)
    hubspot_result = send_to_hubspot(payload)

    return {
        "status": "ok",
        "score": payload["score"],
        "hubspot": hubspot_result
    }

@app.get("/")
def health():
    return {"status": "FastAPI agent is running"}




