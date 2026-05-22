from django.db.models import F
from ..models import Post,Like



def check_post_availablity(post_id):
    return not Post.objects.filter(id=post_id,status=Post.Status.PUBLISHED).exists()
    

def update_post_like_count(post_id):
    total_like_count = Like.objects.filter(post_id=post_id).count()
    Post.objects.filter(id=post_id).update(like_count=total_like_count)

