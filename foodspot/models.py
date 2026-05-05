from django.db import models
from django.contrib.gis.db import models as gis_models

class FoodSpot(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    location = gis_models.PointField(geography=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='food_spots'
    )
    google_place_id = models.CharField(null=True,blank=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name