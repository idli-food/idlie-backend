import requests
from rest_framework.views import APIView
from rest_framework import status

from core.services import places
from core.utils.api_response import success_response, error_response


class PlacesAutocompleteView(APIView):
    # No auth: the hotel signup location picker runs before the account exists.

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return error_response(
                message="'q' query parameter is required",
                code=status.HTTP_400_BAD_REQUEST,
            )

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        try:
            lat = float(lat) if lat else None
            lng = float(lng) if lng else None
        except ValueError:
            return error_response(
                message="'lat' and 'lng' must be numbers",
                code=status.HTTP_400_BAD_REQUEST,
            )

        session_token = request.query_params.get("session_token") or None

        try:
            results = places.autocomplete(
                query, lat=lat, lng=lng, session_token=session_token
            )
        except requests.RequestException:
            return error_response(
                message="Place search failed",
                code=status.HTTP_502_BAD_GATEWAY,
            )

        return success_response(message="Places fetched", data=results)


class PlaceDetailsView(APIView):
    # No auth: see PlacesAutocompleteView.

    def get(self, request):
        place_id = request.query_params.get("place_id", "").strip()
        if not place_id:
            return error_response(
                message="'place_id' query parameter is required",
                code=status.HTTP_400_BAD_REQUEST,
            )

        session_token = request.query_params.get("session_token") or None

        try:
            result = places.details(place_id, session_token=session_token)
        except requests.RequestException:
            return error_response(
                message="Place details failed",
                code=status.HTTP_502_BAD_GATEWAY,
            )

        return success_response(message="Place details fetched", data=result)
