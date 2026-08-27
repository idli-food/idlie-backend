from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg

from user.models import User
from hotel.models import Hotel, HotelRating, HotelReview
from hotel.serializers.rating_serializer import HotelRatingSerializer, HotelReviewSerializer
from core.utils.api_response import success_response, error_response


class CreateHotelRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        average_rating = hotel.ratings.aggregate(average=Avg("rating_count"))["average"]

        user_rating = None
        if isinstance(request.user, User):
            rating = hotel.ratings.filter(user=request.user).first()
            if rating is not None:
                user_rating = HotelRatingSerializer(rating).data

        return success_response(
            message="Ratings fetched successfully",
            data={
                "average_rating": average_rating,
                "rating_count": hotel.ratings.count(),
                "user_rating": user_rating,
            }
        )

    def post(self, request, hotel_id):
        if not isinstance(request.user, User):
            return error_response(
                message="Only users can rate hotels",
                code=status.HTTP_403_FORBIDDEN
            )

        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = HotelRatingSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            rating, created = HotelRating.objects.update_or_create(
                user=request.user,
                hotel=hotel,
                defaults={"rating_count": serializer.validated_data["rating_count"]}
            )

            return success_response(
                message="Rating saved successfully",
                data=HotelRatingSerializer(rating).data,
                code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        except ValidationError as e:
            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message="An error occurred",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateHotelReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        reviews = hotel.reviews.all().order_by("-created_at")

        user_review = None
        if isinstance(request.user, User):
            review = reviews.filter(user=request.user).first()
            if review is not None:
                user_review = HotelReviewSerializer(review).data

        return success_response(
            message="Reviews fetched successfully",
            data={
                "reviews": HotelReviewSerializer(reviews, many=True).data,
                "user_review": user_review,
            }
        )

    def post(self, request, hotel_id):
        if not isinstance(request.user, User):
            return error_response(
                message="Only users can review hotels",
                code=status.HTTP_403_FORBIDDEN
            )

        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = HotelReviewSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            review, created = HotelReview.objects.update_or_create(
                user=request.user,
                hotel=hotel,
                defaults={"review_text": serializer.validated_data["review_text"]}
            )

            return success_response(
                message="Review saved successfully",
                data=HotelReviewSerializer(review).data,
                code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        except ValidationError as e:
            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message="An error occurred",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
