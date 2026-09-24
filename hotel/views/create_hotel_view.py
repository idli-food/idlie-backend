from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..authentication.services.jwt.jwt_utils import create_access_token, create_refresh_token
from ..serializers.hotel_serializer import CreateHotelSerializer
from core.utils.api_response import success_response, error_response
from otp.exceptions import OTPError
from otp.tokens import consume_verification_token



class CreateHotelView(APIView):



    def post(self, request):

        try:
            request_id = request.data.get("request_id")
            phone_number = request.data.get("phone_number")
            try:
                consume_verification_token(
                    request_id, expected_purpose="hotel_signup", expected_phone=phone_number
                )
            except OTPError as exc:
                return error_response(message=exc.message, code=exc.code)

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