
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError  
from ..service.OTPservices import OTPServices
from ..service.ownership import is_phone_number_available
from ..utils.api_response import success_response, error_response
from ..models import DevOTP
class SendOtpView(APIView):

    def post(self,request):

        phone_number = request.data["phone_number"]
        print(phone_number[3:])
        if not OTPServices.validate_phonenumber(phone_number):
            return error_response(message="invalid phone number pls check",data=phone_number)
        if not is_phone_number_available(phone_number):
            return error_response(message="phone number already taken",data="login")
        response = OTPServices.generate_opt(phone_number)
        if response["otp"] == None:
            return error_response(message="Unexpected error occured")
        print(response["otp"])
        phone_number_obj = DevOTP.objects.create(
        phonenumber = phone_number[3:],
        otp = response["otp"]
        )

        
        
        return success_response(message="otp send",data=response["request_id"])

        
