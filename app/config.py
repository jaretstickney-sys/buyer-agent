import os

CONFIG = {
    "HUBSPOT_ACCESS_TOKEN": os.getenv("HUBSPOT_ACCESS_TOKEN", "pat-na2-94786176-2082-4c20-bc28-9aeef427e6e4"),
    "source_property": "19 Castle Rd, Narragansett, RI",
    "buyer_profile": "empty_nester",
    "allowed_origins": ["https://gilded-seahorse-172ddf.netlify.app/"]  # Replace "*" with your Netlify URL in production
}
