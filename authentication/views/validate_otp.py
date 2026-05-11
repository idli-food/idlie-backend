from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError  
from ..service.ownership import is_phone_number_available
from ..utils.api_response import success_response, error_response
from ..service.OTPservices import OTPServices


class ValidateOTPView(APIView):


    def post(self,request):

        otp = request.data["otp"]
        request_id = request.data["otp"]

        if not otp:
            return error_response(message="OTP not provided")
        
        response = OTPServices.validate_OTP(otp)
        
        if not response :
            return error_response(message="Wrong OTP")
        return success_response(message="OTP verfied") 
        
        

        