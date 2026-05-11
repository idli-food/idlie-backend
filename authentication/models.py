from django.db import models

# Create your models here.




class UserAuthentication(models.Model):
    phonenumber = models.CharField(blank=False,null= False)
    is_verified = models.BooleanField(blank=False,null=False,default=False)

    expires_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attempt_count = models.IntegerField(default=0)

class DevOTP(models.Model):
    phonenumber = models.CharField(blank=False,null= False)
    otp = models.CharField(blank=False,null= False)

class OTPrequest(models.Model):
    phonenumber = models.CharField(blank=False,null= False)
    request_id = models.CharField(blank=False,null= False)
    