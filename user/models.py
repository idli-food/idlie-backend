from django.db import models
from django.contrib.gis.db import models as gis_models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=15,unique=True,blank=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # last_login = models.DateTimeField()
    def __str__(self):
        return self.username
    


class UserProfile(models.Model):

    DIET_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=150, blank=True)
    avatar = models.URLField(max_length=2000, null=True, blank=True)
    bio = models.TextField(blank=True)
    dob = models.DateField(null=True, blank=True)
    credibility_score = models.FloatField(default=0.5)
    diet = models.CharField(max_length=20,choices=DIET_CHOICES,blank=True)
    food_preference = models.CharField(max_length=100,blank=True)
    is_verified = models.BooleanField(default=False)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    def _field_checks(self) -> dict[str, bool]:
        return {
            'name': bool(self.name.strip()),
            'avatar': bool(self.avatar),
            'bio': bool(self.bio.strip()),
            'location': bool(self.location),
            'diet': bool(self.diet.strip()),
            'dob': bool(self.dob),
            'food_preference': bool(self.food_preference.strip()),
        }

    @property
    def completion_percentage(self) -> int:
        checks = self._field_checks()
        completed = sum(checks.values())
        return int((completed / len(checks)) * 100)

    @property
    def incomplete_fields(self) -> list[str]:
        return [field for field, done in self._field_checks().items() if not done]

    @property
    def is_profile_complete(self) -> bool:
        return self.completion_percentage == 100