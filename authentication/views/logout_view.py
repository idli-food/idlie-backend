from rest_framework.views import APIView

from core.utils.api_response import success_response

from ..jwt.cookies import clear_auth_cookies


class LogoutView(APIView):

    def post(self, request):
        response = success_response(message="Logged out")
        clear_auth_cookies(response)
        return response
