from rest_framework import serializers

class EmailRecipientSerializer(serializers.Serializer):
    """Serializer for recipient details"""
    name = serializers.CharField(required=True, max_length=255)
    email = serializers.EmailField(required=True)

class SendVerificationEmailSerializer(serializers.Serializer):
    """Serializer for the verification email request"""
    subject = serializers.CharField(default="Welcome to Mol", max_length=255)
    body = serializers.CharField()
    to = EmailRecipientSerializer(many=True)