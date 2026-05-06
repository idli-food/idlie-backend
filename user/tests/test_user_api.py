from rest_framework.test import APITestCase
from rest_framework import status

from user.models import User


class UserCreateAPITest(APITestCase):

    def test_create_user_successfully(self):

        payload = {
            "phone": "9999999999",
            "username": "arjun",
            "first_name": "Arjun"
        }

        response = self.client.post(
            "/api/users/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            User.objects.count(),
            1
        )

        user = User.objects.first()

        self.assertEqual(
            user.username,
            "arjun"
        )


def test_create_user_without_phone(self):

    payload = {
        "username": "arjun"
    }

    response = self.client.post(
        "/api/users/",
        payload,
        format="json"
    )

    self.assertEqual(
        response.status_code,
        400
    )

    self.assertIn(
        "phone",
        response.data
    )

from django.test import TestCase

from user.serivices.add_user import create_user
from user.models import User


class CreateUserServiceTest(TestCase):

    def test_create_user_service(self):

        data = {
            "phone": "9999999999",
            "username": "arjun"
        }

        user = create_user(
            validated_data=data
        )

        self.assertIsInstance(user, User)

        self.assertEqual(
            user.username,
            "arjun"
        )

from django.test import TestCase

from user.serializers.user import AddUserSerializer 


class AddUserSerializerTest(TestCase):

    def test_serializer_valid(self):

        payload = {
            "phone": "9999999999",
            "username": "arjun"
        }

        serializer = AddUserSerializer(
            data=payload
        )

        self.assertTrue(
            serializer.is_valid()
        )