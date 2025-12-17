import os

CONFIG = {
    "HUBSPOT_ACCESS_TOKEN": os.getenv("HUBSPOT_ACCESS_TOKEN"),
    "source_property": "19 Castle Rd, Narragansett, RI",
    "buyer_profile": "empty_nester",
    "allowed_origins": ["https://gilded-seahorse-172ddf.netlify.app/"]  # Replace "*" with your Netlify URL in production
}
