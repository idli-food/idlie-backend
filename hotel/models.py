from django.db import models
from django.contrib.gis.db import models as gis_models
from rest_framework_gis.fields import GeometryField

# Create your models here.





class Hotel(models.Model):

    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = gis_models.PointField(geography=True, null=True, blank=True)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.name

    





class HotelProfile(models.Model):
    Hotel = models.OneToOneField(Hotel, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    nof_post = models.IntegerField(default=0)