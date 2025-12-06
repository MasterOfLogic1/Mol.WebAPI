from rest_framework import serializers
from .models import Course

class CourseInputSerializer(serializers.Serializer):
    """Serializer for course creation/update - excludes thumbnail_url from request"""
    title = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    thumbnail = serializers.FileField(required=False, help_text='Upload course thumbnail image')
    
    def create(self, validated_data):
        # Remove thumbnail from validated_data since it's not a model field
        validated_data.pop('thumbnail', None)
        return Course.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        # Remove thumbnail from validated_data since it's not a model field
        validated_data.pop('thumbnail', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CourseSerializer(serializers.ModelSerializer):
    """Serializer for course responses - includes thumbnail_url"""
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'url', 'thumbnail', 'thumbnail_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'thumbnail_url', 'created_at', 'updated_at']

