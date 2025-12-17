from app.crm.hubspot import HubSpotClient
from app.config import CONFIG

hubspot = HubSpotClient(CONFIG["HUBSPOT_ACCESS_TOKEN"])

class BuyerAcquisitionAgent:
    def score_lead(self, lead: dict):
        score = 0
        if lead.get("homeowner"):
            score += 30
        if lead.get("timeline_months") <= 6:
            score += 40
        if lead.get("city") in ["Boston", "Cambridge", "Newton", "Wellesley"]:
            score += 30
        return min(score, 100)

    def process_lead(self, lead: dict):
        lead["score"] = self.score_lead(lead)
        if lead["score"] >= 60:
            hubspot.create_or_update_contact(lead)
        return lead
