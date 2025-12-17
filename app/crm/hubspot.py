import requests

class HubSpotClient:
    def __init__(self, access_token):
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def create_or_update_contact(self, lead: dict):
        email = lead.get("email")
        if not email:
            raise ValueError("Lead must contain email")

        payload = {
            "properties": {
                "email": email,
                "firstname": lead.get("first_name"),
                "city": lead.get("city"),
                "buyer_intent_score": lead.get("score"),
                "buyer_timeline": lead.get("timeline_label"),
                "buyer_persona": "Empty Nester",
                "source_property": "19 Castle Rd, Narragansett, RI",
                "lead_priority": self._priority_from_score(lead.get("score"))
            }
        }

        url = f"{self.base_url}/crm/v3/objects/contacts"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code not in [200, 201]:
            raise Exception(f"HubSpot error: {response.text}")
        return response.json()

    def _priority_from_score(self, score):
        if score >= 75:
            return "High"
        if score >= 60:
            return "Medium"
        return "Low"
