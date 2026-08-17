from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..authentication.services.jwt.jwt_utils import create_access_token, create_refresh_token
from ..serializers.hotel_serializer import CreateHotelSerializer
from core.utils.api_response import success_response, error_response
from ..authentication.services.hotel_creation import HotelCreation



class CreateHotelView(APIView):
    

    
    def post(self, request):

        try:
            request_id = request.data.get("request_id")
            if not request_id or not HotelCreation.is_request_id_valid(request_id):
                return error_response(
                    message="request_id not provided or not valid",
                    code=status.HTTP_400_BAD_REQUEST
                )

            serializer = CreateHotelSerializer(
                data=request.data,
                context={
                    "request": request
                }
            )

            if serializer.is_valid():
                hotel = serializer.save()

                hotel_output = CreateHotelSerializer(hotel).data
                access_token = create_access_token(hotel.id)
                refresh_token = create_refresh_token(hotel.id)
                return success_response(
                    message="Hotel created successfully",
                    data={
                        "hotel": hotel_output,
                        "access_token": access_token,
                        "refresh_token": refresh_token  
                    },
                    code=status.HTTP_201_CREATED
                )
            else:
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e: 
            return error_response(
                message="An error occurred",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )