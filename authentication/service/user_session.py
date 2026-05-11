


from ..models import UserAuthentication

class UserSessionService:

    @classmethod
    def store_user_session(phone_number):

        user_auth_obj = UserAuthentication(
            phone_number = phone_number,
            is_verified = True,
            
        )