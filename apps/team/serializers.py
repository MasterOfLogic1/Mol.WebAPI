from rest_framework import serializers
from .models import TeamMember

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'full_name', 'occupation', 'bio', 'avatar_url', 'email_url', 'linkedin_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

