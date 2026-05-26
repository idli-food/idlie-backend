
from ..models import UserProfile


def create_user_profile(user):
    profile = UserProfile.objects.create(user = user)
    print(profile)
