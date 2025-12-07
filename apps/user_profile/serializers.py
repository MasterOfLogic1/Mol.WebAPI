from rest_framework import serializers
from .models import UserProfile
from apps.account.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'firstname', 'lastname', 'middlename', 'phonenumber']
        read_only_fields = ['id']  # This ensures 'id' is set internally

class UserWithProfileSerializer(serializers.ModelSerializer):
    """Serializer for user details with profile information"""
    profile = UserProfileSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login', 'profile']
        read_only_fields = ['id', 'email', 'username', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login', 'profile']
