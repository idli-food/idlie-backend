#!/usr/bin/env python3
"""
Build a dataset of hotels or restaurants in Thiruvananthapuram (Trivandrum)
using the Google Places API (New).

WHY A GRID: Places API (New) Nearby Search returns at most 20 results per
call and has no pagination token. A single search over a whole city will
silently drop everything past the first 20 closest results. To approximate
full coverage, this script tiles the city into a grid of small overlapping
search circles, queries each tile, and deduplicates by place_id across
tiles. This gets you close to exhaustive coverage of what's in Google's
index -- it is still not a mathematical guarantee (a tile that legitimately
has >20 places within its radius will still lose the excess; shrink
TILE_RADIUS_M or GRID_STEP_KM to reduce that risk further).

SETUP
  1. In Google Cloud Console, enable "Places API (New)" for your project
     and make sure billing is enabled.
  2. Export your API key as an environment variable (never hardcode it):
       export GOOGLE_MAPS_API_KEY="your-key-here"
  3. pip install requests --break-system-packages

USAGE
  python3 trivandrum_places.py --type restaurant --out restaurants.csv
  python3 trivandrum_places.py --type hotel --out hotels.csv

  Optional tuning:
    --tile-radius 800      # meters, search radius per grid tile (default 800)
    --grid-step 1.2        # km between grid centers (default 1.2, i.e. overlap)
    --min-lat 8.40 --max-lat 8.62 --min-lng 76.88 --max-lng 77.05
        (default box covers Trivandrum city + close suburbs; widen if you
         want to include areas like Kovalam, Attingal, etc.)

OUTPUT
  A CSV with columns: name, address, phone, longitude, latitude, place_id,
  google_maps_url. Also prints a summary of how many tiles hit the 20-result
  cap (a signal that you should shrink --tile-radius in that area).
"""

import argparse
import csv
import math
import os
import sys
import time

import requests

SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"

TYPE_MAP = {
    "hotel": ["lodging"],
    "restaurant": ["restaurant"],
}

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.internationalPhoneNumber",
    "places.nationalPhoneNumber",
    "places.primaryType",
    "places.businessStatus",
])


def build_grid(min_lat, max_lat, min_lng, max_lng, step_km):
    """Generate grid center points covering the bounding box, step_km apart."""
    lat_step = step_km / 111.0  # ~111 km per degree latitude
    points = []
    lat = min_lat
    while lat <= max_lat:
        # longitude degrees per km shrinks with latitude
        lng_step = step_km / (111.320 * math.cos(math.radians(lat)))
        lng = min_lng
        while lng <= max_lng:
            points.append((round(lat, 6), round(lng, 6)))
            lng += lng_step
        lat += lat_step
    return points


def search_tile(api_key, lat, lng, radius_m, included_types):
    body = {
        "includedTypes": included_types,
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius_m,
            }
        },
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    resp = requests.post(SEARCH_URL, json=body, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"  [warn] tile ({lat},{lng}) failed: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return []
    return resp.json().get("places", [])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type", choices=TYPE_MAP.keys(), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tile-radius", type=float, default=800)
    ap.add_argument("--grid-step", type=float, default=1.2)
    ap.add_argument("--min-lat", type=float, default=8.40)
    ap.add_argument("--max-lat", type=float, default=8.62)
    ap.add_argument("--min-lng", type=float, default=76.88)
    ap.add_argument("--max-lng", type=float, default=77.05)
    args = ap.parse_args()

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("ERROR: set GOOGLE_MAPS_API_KEY environment variable first.", file=sys.stderr)
        sys.exit(1)

    included_types = TYPE_MAP[args.type]
    grid = build_grid(args.min_lat, args.max_lat, args.min_lng, args.max_lng, args.grid_step)
    print(f"Grid has {len(grid)} tiles (radius {args.tile_radius}m, step {args.grid_step}km)")

    seen = {}
    capped_tiles = 0
    for i, (lat, lng) in enumerate(grid, 1):
        places = search_tile(api_key, lat, lng, args.tile_radius, included_types)
        if len(places) >= 20:
            capped_tiles += 1
            print(f"  [!] tile {i}/{len(grid)} at ({lat},{lng}) hit the 20-result cap -- consider shrinking --tile-radius here")
        for p in places:
            pid = p.get("id")
            if pid and pid not in seen:
                seen[pid] = p
        if i % 10 == 0 or i == len(grid):
            print(f"  tile {i}/{len(grid)} done, {len(seen)} unique places so far")
        time.sleep(0.05)  # gentle pacing

    print(f"\nTotal unique places found: {len(seen)}")
    if capped_tiles:
        print(f"WARNING: {capped_tiles} tile(s) returned the max 20 results -- likely under-counting in dense areas. Re-run with a smaller --tile-radius (e.g. half the current value) to improve coverage there.")

    rows = []
    for pid, p in seen.items():
        name = p.get("displayName", {}).get("text", "")
        address = p.get("formattedAddress", "")
        phone = p.get("internationalPhoneNumber") or p.get("nationalPhoneNumber") or ""
        loc = p.get("location", {})
        lat_v = loc.get("latitude", "")
        lng_v = loc.get("longitude", "")
        status = p.get("businessStatus", "")
        maps_url = f"https://www.google.com/maps/place/?q=place_id:{pid}"
        rows.append([name, address, phone, lng_v, lat_v, pid, status, maps_url])

    rows.sort(key=lambda r: r[0].lower())

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "address", "phone", "longitude", "latitude", "place_id", "business_status", "google_maps_url"])
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()