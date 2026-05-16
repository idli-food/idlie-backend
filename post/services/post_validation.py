
from ..models import Post





class PostValidations:

    @classmethod
    def check_post_availablity(cls,post_id):
        return not Post.objects.filter(id=post_id,status=Post.Status.PUBLISHED).exists()
    

