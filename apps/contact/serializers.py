from rest_framework import serializers
from .models import ContactMessage


class GeneralContactSerializer(serializers.Serializer):
    """Serializer for general contact form submission"""
    name = serializers.CharField(required=True, max_length=255, help_text='Your name')
    email = serializers.EmailField(required=True, help_text='Your email address')
    subject = serializers.CharField(required=True, max_length=255, help_text='Message subject')
    message = serializers.CharField(required=True, help_text='Your message')


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for contact message responses"""
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

