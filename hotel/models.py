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
    avatar = models.URLField(blank=True, null=True)
    nof_post = models.IntegerField(default=0)





class FoodType(models.TextChoices):

    
    VEG = "veg", "Veg"
    NON_VEG = "non_veg", "Non-Veg"
    EGG = "egg", "Egg"

class Menu(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="menus")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class MenuCategory(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)

class FoodItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True) # S3-backed
    food_type = models.CharField(max_length=10, choices=FoodType.choices)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

class FoodItemVariant(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="variants")
    portion_name = models.CharField(max_length=50, default="Regular")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)