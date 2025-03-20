from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name','email', 'date_of_birth', 'phone', 'age', 'salary_per_hr', 'isAdmin', 'enq_taker', 'organization_id']


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_of_birth', 'phone', 'age', 'salary_per_hr', 'isAdmin', 'enq_taker', 'organization_id']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'phone', 'age', 'isAdmin', 'salary_per_hr', 'enq_taker', 'organization_id']  # Include fields you want to expose