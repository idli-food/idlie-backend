from django.db import models

# Create your models here.


class GoogleIdentity(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name="google_identity")
    google_sub = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    