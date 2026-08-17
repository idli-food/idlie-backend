from rest_framework.views import APIView

from ...authentication.services.otp_services import OTPServices
from core.utils.api_response import success_response, error_response




class SignupView(APIView):

    def post(slef,request):

        phone_number = request.data.get("phone_number")
        print(phone_number)
        if not OTPServices.validate_phonenumber(phone_number):
            return error_response(
                message="invalid phone number pls check",
                data=phone_number
            )
        if not OTPServices.is_phone_number_available(phone_number):
            return error_response(
                message="phone number already taken",
                data="login"
            )
        otp_response = OTPServices.generate_opt(phone_number)
        print(otp_response)

        if otp_response["otp"] is None:
            return error_response(
                message="Unexpected error occured"
            )
        return success_response(message="otp send",request_id=otp_response["request_id"])
        

