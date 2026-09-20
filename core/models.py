from django.db import models


class Waitlister(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"
