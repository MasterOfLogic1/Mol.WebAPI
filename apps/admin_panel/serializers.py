from rest_framework import serializers
from apps.account.models import User

class UserListSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    firstname = serializers.SerializerMethodField()
    lastname = serializers.SerializerMethodField()
    middlename = serializers.SerializerMethodField()
    phonenumber = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login', 
                  'firstname', 'lastname', 'middlename', 'phonenumber']
        read_only_fields = ['id', 'email', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login',
                           'firstname', 'lastname', 'middlename', 'phonenumber']
    
    def get_role_name(self, obj):
        return obj.role.name if obj.role else None
    
    def get_firstname(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.firstname
        return None
    
    def get_lastname(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.lastname
        return None
    
    def get_middlename(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.middlename
        return None
    
    def get_phonenumber(self, obj):
        if hasattr(obj, 'profile') and obj.profile:
            return obj.profile.phonenumber
        return None

class UserBlockSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()

class UpdateUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8, help_text="New password (minimum 8 characters)")

