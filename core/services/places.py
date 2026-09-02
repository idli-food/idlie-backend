"""Thin proxy over the Google Places API (New).

The mobile app never sees the key: it calls our /places/ endpoints, which call
Google with settings.GOOGLE_MAPS_API_KEY.
"""

import requests
from django.conf import settings

AUTOCOMPLETE_URL = "https://places.googleapis.com/v1/places:autocomplete"
DETAILS_URL = "https://places.googleapis.com/v1/places/{place_id}"

_TIMEOUT = 15


def autocomplete(query, *, lat=None, lng=None, session_token=None):
    """Return [{"place_id", "description"}] predictions for `query`."""
    body = {
        "input": query,
        "includedRegionCodes": ["in"],
    }
    if lat is not None and lng is not None:
        body["locationBias"] = {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 50000.0,
            }
        }
    if session_token:
        body["sessionToken"] = session_token

    resp = requests.post(
        AUTOCOMPLETE_URL,
        json=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": (
                "suggestions.placePrediction.placeId,"
                "suggestions.placePrediction.text"
            ),
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()

    results = []
    for suggestion in resp.json().get("suggestions", []):
        prediction = suggestion.get("placePrediction")
        if not prediction:
            continue
        results.append(
            {
                "place_id": prediction.get("placeId"),
                "description": prediction.get("text", {}).get("text", ""),
            }
        )
    return results


def details(place_id, *, session_token=None):
    """Resolve a place_id to {"place_id", "name", "address", "latitude", "longitude"}."""
    params = {}
    if session_token:
        params["sessionToken"] = session_token

    resp = requests.get(
        DETAILS_URL.format(place_id=place_id),
        params=params,
        headers={
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "id,displayName,formattedAddress,location",
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()

    data = resp.json()
    location = data.get("location", {})
    return {
        "place_id": data.get("id"),
        "name": data.get("displayName", {}).get("text", ""),
        "address": data.get("formattedAddress", ""),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
    }
