
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from ..utils.api_response import success_response, error_response

from ..jwt.jwt_utils import create_access_token,decode_token


class RefreshAccessToken(APIView):


    # DO refresh post request 
    def post(self,request):

        refresh_token = request.data.get("refresh")

        if not refresh_token :
            return error_response(message="Refresh token required",code=status.HTTP_400_BAD_REQUEST)
        
        try:
            payload = decode_token(refresh_token)
            
            if payload["type"] != "refresh":
                return error_response(message="invalid token type",code=status.HTTP_401_UNAUTHORIZED)
            new_access_token = create_access_token(payload["user_id"])

            return Response({
                "access": new_access_token
            })

        except jwt.ExpiredSignatureError:
            return error_response(message="Refresh token expired",code=status.HTTP_401_UNAUTHORIZED)
        
        except jwt.InvalidTokenError:
            return error_response(message="Invalid token",code=status.HTTP_401_UNAUTHORIZED)
        

