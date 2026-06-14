from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.post_serializer import PostLikeSerializer, PostCommentSerializer, PostSaveSerializer, FeedPostCommentSerializer, SavedPostSerilizer
from feed.serializer.feed_serializer import FeedPostSerializer
from core.utils.api_response import success_response, error_response
from ..services import post_service


class LikePostView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:

            if post_service.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            serializer = PostLikeSerializer(data={
                "user": request.user.id,
                "post": post_id
            })

            serializer.is_valid(raise_exception=True)

            serializer.save()
            post_service.update_post_like_count(post_id=post_id)
            return success_response(
                message="Liked successfully",
                code=status.HTTP_201_CREATED
            )

        except IntegrityError:

            return error_response(
                message="You already liked this post",
                code=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, post_id):

        try:

            if post_service.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            deleted = post_service.delete_post_like(post_id=post_id, user_id=request.user.id)

            if not deleted:
                return error_response(
                    message="You have not liked this post",
                    code=status.HTTP_400_BAD_REQUEST
                )

            post_service.update_post_like_count(post_id=post_id)
            return success_response(
                message="Like removed successfully",
                code=status.HTTP_200_OK
            )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class  PostCommentView(APIView):

    permission_classes = [IsAuthenticated]



    def get(self,request,post_id):

        try:

            print("here")



            if post_service.check_post_availablity(post_id=post_id):
                raise ValidationError("Post not available")
            
            comment = post_service.get_comments(post_id=post_id)
            serializer = FeedPostCommentSerializer(comment, many=True, context={'request': request})
            print(serializer)

            return success_response(
                message="done",
                data=serializer.data
            )


        
        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def post(self, request, post_id):

        try:

            content = request.data["content"]

            if post_service.check_post_availablity(post_id=post_id):
                raise ValidationError("Post not available")

            serializer = PostCommentSerializer(data={
                "user" : request.user.id,
                "post" : post_id,
                "content" : content
            })

            serializer.is_valid(raise_exception=True)
            serializer.save()
            post_service.update_post_comment_count(post_id=post_id)

            return success_response(
                message="Commented successfully",
                code=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, post_id, comment_id):

        try:

            deleted = post_service.delete_comment(comment_id=comment_id, user_id=request.user.id)

            if not deleted:
                return error_response(
                    message="Comment not found or you do not own it",
                    code=status.HTTP_404_NOT_FOUND
                )

            post_service.update_post_comment_count(post_id=post_id)
            return success_response(
                message="Comment deleted successfully",
                code=status.HTTP_200_OK
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SavePostView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:

            if post_service.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            serializer = PostSaveSerializer(data={
                "user": request.user.id,
                "post": post_id
            })

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(
                message="Post saved successfully",
                code=status.HTTP_201_CREATED
            )

        except IntegrityError:

            return error_response(
                message="You have already saved this post",
                code=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, post_id):

        try:

            deleted = post_service.unsave_post(post_id=post_id, user_id=request.user.id)

            if not deleted:
                return error_response(
                    message="You have not saved this post",
                    code=status.HTTP_400_BAD_REQUEST
                )

            return success_response(
                message="Post unsaved successfully",
                code=status.HTTP_200_OK
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class GetSavedPostView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        print("hreer")

        try:
            posts = post_service.get_saved_post(request.user.id)

            if request.query_params.get("view") == "feed":
                serializer = FeedPostSerializer(posts, many=True, context={'request': request})
            else:
                serializer = SavedPostSerilizer(posts, many=True)

            return success_response(
                message="saved post",
                data=serializer.data
            )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


