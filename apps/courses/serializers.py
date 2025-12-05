from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'url', 'thumbnail_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

