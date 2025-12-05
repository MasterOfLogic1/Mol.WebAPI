from rest_framework import serializers
from .models import BlogPost

class BlogPostSerializer(serializers.ModelSerializer):
    creator_fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'description', 'body', 'date_uploaded', 'updated_at', 'created_by', 'creator_fullname']
        read_only_fields = ['id', 'date_uploaded', 'updated_at', 'created_by', 'creator_fullname']
    
    def get_creator_fullname(self, obj):
        """Returns the full name of the creator"""
        try:
            if hasattr(obj.created_by, 'profile') and obj.created_by.profile:
                profile = obj.created_by.profile
                parts = [profile.firstname]
                if profile.middlename:
                    parts.append(profile.middlename)
                parts.append(profile.lastname)
                return ' '.join(parts)
        except Exception:
            pass
        return obj.created_by.email if obj.created_by else ''

