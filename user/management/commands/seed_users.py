


import random
import string

from django.core.management.base import BaseCommand
from faker import Faker

from ...models import User   

fake = Faker()


def generate_phone():
    return str(random.choice([6, 7, 8, 9])) + ''.join(
        random.choices(string.digits, k=9)
    )


# non profile completed users 

class Command(BaseCommand):
    help = "Create fake users"

    def handle(self, *args, **kwargs):

        for _ in range(20):

            username = fake.unique.user_name()

            user = User.objects.create(
                phone=generate_phone(),
                username=username,
            )

            user.set_password(fake.password(length=10))
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f"Created user: {username}")
            )

        self.stdout.write(
            self.style.SUCCESS("50 fake users created successfully")
        )