from django.db import models
from user_manager.models import CustomUser

class Device(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    device_token = models.CharField(max_length=255, unique=True)
