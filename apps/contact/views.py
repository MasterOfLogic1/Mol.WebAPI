from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.conf import settings
from .models import ContactMessage
from .serializers import GeneralContactSerializer
from apps.shared.util import send_email
from apps.shared.models import InternalServerError


@extend_schema(
    request=GeneralContactSerializer,
    responses={
        201: {"message": "Contact message sent successfully"},
        400: {"error": "Invalid data"}
    },
    summary="General Contact",
    description="Submit a general contact message. The message will be sent via email and stored in the database.",
    tags=["Contact"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def general_contact(request):
    """Handle general contact form submissions"""
    serializer = GeneralContactSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    name = serializer.validated_data.get('name')
    email = serializer.validated_data.get('email')
    subject = serializer.validated_data.get('subject')
    message = serializer.validated_data.get('message')
    
    try:
        # Store the contact message in the database
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Get contact email from settings or use a default
        contact_email = getattr(settings, 'CONTACT_EMAIL', 'contact@mol.com')
        contact_name = getattr(settings, 'CONTACT_NAME', 'Mol Support')
        
        # Prepare email body with the contact message
        email_subject = f"New Contact Message: {subject}"
        email_body = (
            f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'>"
            f"<h2 style='color: #333;'>New Contact Message</h2>"
            f"<p style='color: #666; font-size: 16px; line-height: 1.6;'>"
            f"You have received a new contact message from your website."
            f"</p>"
            f"<div style='background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;'>"
            f"<p style='margin: 10px 0;'><strong style='color: #333;'>Name:</strong> <span style='color: #666;'>{name}</span></p>"
            f"<p style='margin: 10px 0;'><strong style='color: #333;'>Email:</strong> <span style='color: #666;'>{email}</span></p>"
            f"<p style='margin: 10px 0;'><strong style='color: #333;'>Subject:</strong> <span style='color: #666;'>{subject}</span></p>"
            f"<p style='margin: 10px 0;'><strong style='color: #333;'>Message:</strong></p>"
            f"<p style='color: #666; line-height: 1.6; white-space: pre-wrap;'>{message}</p>"
            f"</div>"
            f"<p style='color: #999; font-size: 12px; margin-top: 30px;'>"
            f"This message was sent from the contact form on your website."
            f"</p>"
            f"</div>"
        )
        
        # Send email to contact/admin email
        recipients = [{
            "name": contact_name,
            "email": contact_email
        }]
        
        send_email(email_subject, email_body, recipients)
        
        return Response(
            {"message": "Your message has been sent successfully. We will get back to you soon."},
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        raise InternalServerError(str(e))

