from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.agent import BuyerAcquisitionAgent
from app.config import CONFIG

app = FastAPI()
agent = BuyerAcquisitionAgent()

# Enable CORS so Netlify can post
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG["allowed_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/event")
async def receive_lead(request: Request):
    data = await request.json()
    payload = data.get("payload")
    if not payload:
        return {"error": "No payload received"}
    processed = agent.process_lead(payload)
    return processed
