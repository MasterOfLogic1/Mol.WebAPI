from rest_framework import serializers
from .models import UserProfile
from apps.account.models import User

class UserProfileInputSerializer(serializers.Serializer):
    """Serializer for profile creation/update - excludes thumbnail_url from request"""
    firstname = serializers.CharField(required=True, max_length=100)
    lastname = serializers.CharField(required=True, max_length=100)
    middlename = serializers.CharField(required=False, allow_blank=True, max_length=100)
    phonenumber = serializers.CharField(required=False, allow_blank=True, max_length=20)
    occupation = serializers.CharField(required=False, allow_blank=True, max_length=200)
    bio = serializers.CharField(required=False, allow_blank=True)
    thumbnail = serializers.FileField(required=False, help_text='Upload profile picture')
    
    def create(self, validated_data):
        # Remove thumbnail from validated_data since it's not a model field
        validated_data.pop('thumbnail', None)
        # user should be passed from the view
        return UserProfile.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        # Remove thumbnail from validated_data since it's not a model field
        validated_data.pop('thumbnail', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for profile responses - includes thumbnail_url"""
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'firstname', 'lastname', 'middlename', 'phonenumber', 'occupation', 'bio', 'thumbnail', 'thumbnail_url']
        read_only_fields = ['id', 'thumbnail_url']

class UserWithProfileSerializer(serializers.ModelSerializer):
    """Serializer for user details with profile information"""
    profile = UserProfileSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login', 'profile']
        read_only_fields = ['id', 'email', 'username', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login', 'profile']
