from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now


def success_response(
    message="Success",
    data=None,
    code=status.HTTP_200_OK,
    meta=None,
    request_id=None
):
    response = {
        "success": True,
        "message": message,
        "code": code,
        "data": data,
        "request_id": request_id,
        "meta": {
            "timestamp": now().isoformat(),
            "version": "1.0.0"
        }
    }

    if meta:
        response["meta"].update(meta)

    return Response(response, status=code)


def error_response(
    message="Something went wrong",
    errors=None,
    code=status.HTTP_400_BAD_REQUEST,
    data=None
):
    response = {
        "success": False,
        "message": message,
        "code": code,
        "data": data,
        "errors": errors,
        "meta": {
            "timestamp": now().isoformat(),
            "version": "1.0.0"
        }
    }

    return Response(response, status=code)
