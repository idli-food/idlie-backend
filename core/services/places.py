"""Thin proxy over the Google Places API (New).

The mobile app never sees the key: it calls our /places/ endpoints, which call
Google with settings.GOOGLE_MAPS_API_KEY.
"""

import re
from urllib.parse import unquote_plus

import requests
from django.conf import settings

AUTOCOMPLETE_URL = "https://places.googleapis.com/v1/places:autocomplete"
DETAILS_URL = "https://places.googleapis.com/v1/places/{place_id}"
SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"

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


def from_maps_link(link):
    """Resolve a Google Maps place link (short or full) to hotel fields.

    Returns None when the link has no place name or Google finds no match.
    """
    # Short maps.app.goo.gl links redirect to the full /maps/place/ URL
    url = requests.get(link, allow_redirects=True, timeout=_TIMEOUT).url

    name_match = re.search(r"/maps/place/([^/]+)", url)
    if not name_match:
        return None
    name = unquote_plus(name_match.group(1))

    body = {"textQuery": name, "maxResultCount": 1}
    # !3d<lat>!4d<lng> is the place's pin; @lat,lng is only the map centre
    coords = re.search(r"!3d(-?[\d.]+)!4d(-?[\d.]+)", url) or re.search(r"@(-?[\d.]+),(-?[\d.]+)", url)
    if coords:
        body["locationBias"] = {
            "circle": {
                "center": {"latitude": float(coords.group(1)), "longitude": float(coords.group(2))},
                "radius": 200.0,
            }
        }

    resp = requests.post(
        SEARCH_TEXT_URL,
        json=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,"
                "places.addressComponents,places.location,"
                "places.internationalPhoneNumber,"
                "places.regularOpeningHours.periods,"
                "places.editorialSummary"
            ),
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()

    results = resp.json().get("places", [])
    if not results:
        return None
    data = results[0]

    city = ""
    for component in data.get("addressComponents", []):
        if "locality" in component.get("types", []):
            city = component.get("longText", "")
            break

    # "+91 80 6555 1111" -> "+918065551111", matching how hotel phones are stored
    phone = re.sub(r"[^\d+]", "", data.get("internationalPhoneNumber", "")) or None

    # Google days are 0=Sunday..6=Saturday; ours are 0=Monday..6=Sunday.
    # A single period with no "close" means open 24/7.
    sessions = []
    for period in data.get("regularOpeningHours", {}).get("periods", []):
        start = period["open"]
        end = period.get("close")
        if not end:
            sessions = [{"day": day, "start_time": "00:00", "end_time": "23:59"} for day in range(7)]
            break
        sessions.append({
            "day": (start.get("day", 0) + 6) % 7,
            "start_time": f"{start.get('hour', 0):02d}:{start.get('minute', 0):02d}",
            "end_time": f"{end.get('hour', 0):02d}:{end.get('minute', 0):02d}",
        })

    location = data.get("location", {})
    return {
        "place_id": data.get("id"),
        "name": data.get("displayName", {}).get("text", ""),
        "address": data.get("formattedAddress", ""),
        "city": city,
        "phone_number": phone,
        "location": {
            "type": "Point",
            "coordinates": [location.get("longitude"), location.get("latitude")],
        },
        "location_link": link,
        "sessions": sessions,
        "description": data.get("editorialSummary", {}).get("text") or None,
    }
