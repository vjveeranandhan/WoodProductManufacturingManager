
from django.contrib.auth.models import AbstractUser
from django.db import models
from organization.models import Organization

class UserType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.TextField(max_length=30, blank=False) 
    age = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=False, null=False, verbose_name='Phone Number')
    user_types = models.ManyToManyField(UserType)
    isAdmin = models.BooleanField(default=False)
    enq_taker = models.BooleanField(default=False)
    salary_per_hr = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.username