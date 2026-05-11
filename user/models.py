from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=15)

    credibility_score = models.FloatField(default=0.5)

    avatar_url = models.URLField(blank=True, null=True)

    dob = models.DateField(null=True, blank=True)

    bio = models.TextField(blank=True)

    DIET_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
    ]

    diet = models.CharField(
        max_length=20,
        choices=DIET_CHOICES,
        blank=True
    )

    food_preference = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    profile_status = models.BooleanField(default=False)

    def __str__(self):
        return self.username