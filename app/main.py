# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import requests

app = FastAPI()

# === CORS SETUP ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return min(score, 100)

# === HubSpot Submission ===
def send_to_hubspot(lead: dict):
    properties = {
        "firstname": lead.get("first_name"),
        "lastname": lead.get("last_name", ""),
        "email": lead.get("email"),
        "city": lead.get("city"),
        "state": lead.get("state", ""),
        "homeowner_status": "Homeowner" if lead.get("homeowner") else "Renter"
    }
    payload = {"properties": properties}

    try:
        response = requests.post(HUBSPOT_CONTACT_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return {"hubspot": "success"}
    except Exception as e:
        print("HubSpot error:", e, getattr(e, "response", None))
        return {"hubspot": "error", "details": str(e)}

# === FastAPI Endpoint ===

@app.post("/event")
async def receive_lead(request: Request):
    data = await request.json()
    payload = data.get("payload")
    if not payload:
        return JSONResponse(content={"error": "No payload received"}, status_code=400)

    payload["score"] = score_lead(payload)

    try:
        hubspot_result = send_to_hubspot(payload)
        payload.update(hubspot_result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content=payload)




