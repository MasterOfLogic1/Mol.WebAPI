from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.conf import settings
from .models import Newsletter
from .serializers import NewsletterRegistrationSerializer, NewsletterVerifySerializer, NewsletterSerializer
from apps.shared.util import send_email
from apps.shared.models import InternalServerError


@extend_schema(
    request=NewsletterRegistrationSerializer,
    responses={
        201: {"message": "Verification email sent successfully"},
        400: {"error": "Email already registered"}
    },
    summary="Register for Newsletter",
    description="Register an email address for the newsletter. A verification email will be sent.",
    tags=["Newsletter"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_newsletter(request):
    """Register an email for newsletter subscription"""
    serializer = NewsletterRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email').lower().strip()

    try:
        # Check if email already exists
        newsletter = Newsletter.objects.get(email=email)
        
        # If already verified, return message
        if newsletter.is_verified:
            return Response(
                {"message": "This email is already subscribed to our newsletter."},
                status=status.HTTP_200_OK
            )
        
        # If not verified, resend verification email
        newsletter.generate_verification_token()
        verification_link = f"{settings.PORTAL_WEB_APP_URL}/newsletter/verify/{newsletter.verification_token}"
        
        subject = "Welcome to Our Newsletter!"
        body = (
            f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'>"
            f"<h2 style='color: #333;'>Welcome to Our Newsletter!</h2>"
            f"<p style='color: #666; font-size: 16px; line-height: 1.6;'>"
            f"Thank you for subscribing to our newsletter! We're excited to have you join our community."
            f"</p>"
            f"<p style='color: #666; font-size: 16px; line-height: 1.6;'>"
            f"To complete your subscription and start receiving our updates, please verify your email address by clicking the button below:"
            f"</p>"
            f"<div style='text-align: center; margin: 30px 0;'>"
            f"<a href='{verification_link}' "
            f"style='display: inline-block; background-color: #007bff; color: #ffffff; padding: 12px 30px; "
            f"text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;'>"
            f"Verify Email Address"
            f"</a>"
            f"</div>"
            f"<p style='color: #666; font-size: 14px; line-height: 1.6;'>"
            f"If the button doesn't work, you can copy and paste the following link into your browser:<br>"
            f"<a href='{verification_link}' style='color: #007bff;'>{verification_link}</a>"
            f"</p>"
            f"<p style='color: #999; font-size: 12px; margin-top: 30px;'>"
            f"If you didn't subscribe to our newsletter, you can safely ignore this email."
            f"</p>"
            f"<p style='color: #999; font-size: 12px;'>"
            f"© 2025 Mol. All rights reserved."
            f"</p>"
            f"</div>"
        )
        
        recipients = [{
            "name": email,
            "email": email
        }]
        
        send_email(subject, body, recipients)
        
        return Response(
            {"message": "Verification email sent. Please check your inbox to verify your subscription."},
            status=status.HTTP_200_OK
        )
    
    except Newsletter.DoesNotExist:
        # Create new newsletter subscription
        newsletter = Newsletter.objects.create(email=email)
        newsletter.generate_verification_token()
        
        verification_link = f"{settings.PORTAL_WEB_APP_URL}/newsletter/verify/{newsletter.verification_token}"
        
        subject = "Welcome to Our Newsletter!"
        body = (
            f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'>"
            f"<h2 style='color: #333;'>Welcome to Our Newsletter!</h2>"
            f"<p style='color: #666; font-size: 16px; line-height: 1.6;'>"
            f"Thank you for subscribing to our newsletter! We're excited to have you join our community."
            f"</p>"
            f"<p style='color: #666; font-size: 16px; line-height: 1.6;'>"
            f"To complete your subscription and start receiving our updates, please verify your email address by clicking the button below:"
            f"</p>"
            f"<div style='text-align: center; margin: 30px 0;'>"
            f"<a href='{verification_link}' "
            f"style='display: inline-block; background-color: #007bff; color: #ffffff; padding: 12px 30px; "
            f"text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;'>"
            f"Verify Email Address"
            f"</a>"
            f"</div>"
            f"<p style='color: #666; font-size: 14px; line-height: 1.6;'>"
            f"If the button doesn't work, you can copy and paste the following link into your browser:<br>"
            f"<a href='{verification_link}' style='color: #007bff;'>{verification_link}</a>"
            f"</p>"
            f"<p style='color: #999; font-size: 12px; margin-top: 30px;'>"
            f"If you didn't subscribe to our newsletter, you can safely ignore this email."
            f"</p>"
            f"<p style='color: #999; font-size: 12px;'>"
            f"© 2025 Mol. All rights reserved."
            f"</p>"
            f"</div>"
        )
        
        recipients = [{
            "name": email,
            "email": email
        }]
        
        send_email(subject, body, recipients)
        
        return Response(
            {"message": "Verification email sent. Please check your inbox to verify your subscription."},
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        raise InternalServerError(str(e))


@extend_schema(
    request=None,
    responses={
        200: {"message": "Email verified successfully. Welcome to our newsletter!"},
        400: {"error": "Invalid or expired token"}
    },
    summary="Verify Newsletter Subscription",
    description="Verify newsletter subscription using the token from the verification email. Can be accessed via GET (clicking the link) or POST.",
    tags=["Newsletter"]
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_newsletter(request, verification_token):
    """Verify newsletter subscription"""
    try:
        newsletter = Newsletter.objects.get(verification_token=verification_token)
        
        if newsletter.is_verified:
            return Response(
                {"message": "This email is already verified."},
                status=status.HTTP_200_OK
            )
        
        # Mark as verified
        newsletter.is_verified = True
        newsletter.save(update_fields=['is_verified'])
        
        return Response(
            {"message": "Email verified successfully. Welcome to our newsletter!"},
            status=status.HTTP_200_OK
        )
    
    except Newsletter.DoesNotExist:
        return Response(
            {"error": "Invalid or expired verification token."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        raise InternalServerError(str(e))

