from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'firstname', 'lastname', 'middlename', 'phonenumber']
        read_only_fields = ['id']  # This ensures 'id' is set internally
