from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'email', 'phone_number', 'is_active', 'is_block', 'end_date_sub', 'subscription']
        extra_kwargs = {'password': {'write_only': True}}
