from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..serializers.post_serializer import CreatePostSerializer
from core.utils.api_response import success_response, error_response
from ..services import post_service
from ..services.celery_task import generate_thumbnail

class CreatePostView(APIView):

    permission_classes = [IsAuthenticated]
    

    def post(self, request):

        try:
            print("Request data:", request.data)

            serializer = CreatePostSerializer(
                data=request.data,
                context={
                    "request": request
                }
            )

            if serializer.is_valid():
                post = serializer.save()
                print("Post created successfully:", post)

                post_output = CreatePostSerializer(post).data
                post_service.set_media_url(post)
                post_service.set_post_location_from_hotel(post)
                if post_output['media_type'] == 'video':
                    generate_thumbnail.delay(post_id=post.id)
                elif post_output['media_type'] == 'image':
                    post_service.set_thumbnail_url_image(post.id)                    

                return success_response(
                    message="Post uploaded successfully",
                    data={
                        "post": post_output
                    },
                    code=status.HTTP_201_CREATED
                )
            else:
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
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