from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError  
from core.utils.api_response import success_response, error_response
from ..services.otp_services import OTPServices
from ..services.hotel_creation import HotelCreation

class ValidateOTPView(APIView):

    def post(self,request):

        otp = request.data["otp"]
        phone_number = request.data["phone_number"]

        if not otp:
            return error_response(message="OTP not provided")
        
        response = OTPServices.validate_OTP(otp)
        request_id = HotelCreation.generate_request_id(phone_number)

        
        if not response :
            return error_response(message="Wrong OTP")
        return success_response(message="OTP verfied",request_id=request_id) 
        