from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.login_auth import validate_phone_number
from core.utils.api_response import success_response, error_response
from ...authentication.services.otp_services import OTPServices
from ...services.hotel_services import get_hotel_id_by_phone_number
from ...authentication.services.jwt.jwt_utils import create_access_token, create_refresh_token

class SendLoginOTPView(APIView):




    def post (self, request):

            phone_number = request.data.get("phone_number")

            print(phone_number)

            if not OTPServices.validate_phonenumber(phone_number):
                return error_response(
                    message="invalid phone number pls check",
                    data=phone_number
                )

        
            if not validate_phone_number(phone_number):
                return Response({"message": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

            otp_response = OTPServices.generate_opt(phone_number)

            print(otp_response)

            if otp_response["otp"] is None:
                return error_response(
                    message="Unexpected error occured"
                )

            return success_response(message="otp send")







class ValidateLoginOTPView(APIView):


    def post(self, request) : 

        otp = request.data.get("otp")
        phone_number = request.data.get("phone_number")
        
        if not otp:
            return error_response(message="OTP not provided")
        
        response = OTPServices.validate_OTP(otp)
        
        if not response :
            return error_response(message="Wrong OTP")

        hotel_id = get_hotel_id_by_phone_number(phone_number)

        if hotel_id is None:
            return error_response(message="Hotel not found for this phone number")

        access_token = create_access_token(hotel_id)
        refresh_token = create_refresh_token(hotel_id)

        return success_response(
            message="Login successful",
            data={
                "phone_number": phone_number,
                "id": hotel_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )