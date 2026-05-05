from django.db import models

# Create your models here.

class User(models.Model):
    phone = models.CharField(max_length=15)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    credibility_score = models.FloatField(default=0.5)
    avatar_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)