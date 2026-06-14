
from ..models import User,UserProfile


















def get_avatar_url(user_id):

    user_profile = UserProfile.objects.filter(user_id=user_id).first()

    if user_profile and user_profile.avatar:
        return str(user_profile.avatar)
    return None