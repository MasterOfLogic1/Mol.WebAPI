from rest_framework import serializers
from .models import Newsletter


class NewsletterRegistrationSerializer(serializers.Serializer):
    """Serializer for newsletter registration"""
    email = serializers.EmailField(required=True, help_text='Email address to subscribe to newsletter')


class NewsletterVerifySerializer(serializers.Serializer):
    """Serializer for newsletter verification"""
    token = serializers.CharField(required=True, help_text='Verification token from email')


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for newsletter responses"""
    class Meta:
        model = Newsletter
        fields = ['id', 'email', 'is_verified', 'registration_date']
        read_only_fields = ['id', 'is_verified', 'registration_date']

