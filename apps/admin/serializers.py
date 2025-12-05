from rest_framework import serializers
from apps.account.models import User

class UserListSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login']
        read_only_fields = ['id', 'email', 'role_name', 'is_active', 'is_verified', 'date_joined', 'last_login']

class UserBlockSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()

