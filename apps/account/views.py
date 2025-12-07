from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import RegisterationSerializer, ResetPasswordSerializer,ResetPasswordRequestSerializer,VerificationSerializer,AccountStatusSerializer,MyTokenObtainPairSerializer,SendVerificationEmailSerializer,ChangePasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.utils import timezone
from django.contrib.auth import get_user_model
import requests  # For SMTP API
from django.conf import settings
from apps.shared.models import InternalServerError
from apps.shared.util import send_email
from django.contrib.auth import logout

User = get_user_model()

def send_verification_email_to_user(user):
    """Helper function to send verification email to a user"""
    try:
        if user.is_verified:
            return False
        
        # Generate a new verification token and prepare the verification link
        user.generate_verification_token()
        verification_link = f"{settings.PORTAL_WEB_APP_URL}/register/verification/{user.verification_token}"
        
        # Get user's name from profile if available
        user_name = user.email
        if hasattr(user, 'profile'):
            profile = user.profile
            name_parts = [profile.firstname]
            if profile.middlename:
                name_parts.append(profile.middlename)
            name_parts.append(profile.lastname)
            user_name = ' '.join(name_parts) if any(name_parts) else user.email
        
        # Prepare the email details
        subject = "Mol - Verify Your Email"
        body = (
            f"Hi {user_name},<br><br>"
            "Thank you for signing up with Mol! We're excited to have you join our community.<br><br>"
            "To complete your registration and access all features, please verify your email address by clicking the link below:<br>"
            f"<a href='{verification_link}'>{verification_link}</a><br><br>"
            "If the link above doesn't work, copy and paste the following link into your browser. "
            "Note: This link will expire in 24 hours for security reasons.<br><br>"
            "If you didn't create an account with Mol, you can safely ignore this email.<br><br>"
            "© 2025 Mol. All rights reserved."
        )
        recipients = [{
            "name": user_name,
            "email": user.email
        }]
        send_email(subject, body, recipients)
        return True
    except Exception:
        # Silently fail - don't break registration if email fails
        return False

#Register View
@extend_schema(
    request=RegisterationSerializer,
    responses={
        201: {"message": "User created successfully"},
        400: {"error": "User already exists"}
    },
    summary="Registration",
    description="Endpoint for user registration.",
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    try:
        email = request.data.get("email")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "email already in use"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists (if provided)
        username = request.data.get("username", "").strip()
        if username and User.objects.filter(username=username).exists():
            return Response({"error": "username already in use"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Automatically send verification email
            send_verification_email_to_user(user)
            return Response({"message": "Registration successful. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Return a standardized internal server error response
        raise InternalServerError(str(e))

# Login View
@extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Obtain JWT Access Token",
        description="Endpoint to obtain an access token by providing valid credentials. Returns only access token (no refresh token)."
    )
)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



# Send Verification Email
@extend_schema(
    request=SendVerificationEmailSerializer,
    responses={200: {"message": "Verification email sent"}},
    summary="Send Account Verification Email",
    description="Sends a verification email with an activation token.",
    tags=["Account Reset & Verification"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_email_view(request):
    serializer = SendVerificationEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')

    try:
        # Get the user based on email
        user = User.objects.get(email=email)
        
        if user.is_verified:
            return Response({"message": "User already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Send verification email using the helper function
        send_verification_email_to_user(user)
        
        return Response({"message": "Verification email sent."}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # Return a standardized internal server error response
        raise InternalServerError(str(e))
    

# Verify Account View
@extend_schema(
    request=None,
    responses={200: {"message": "Account verified successfully"}},
    summary="Verify Account",
    description="Verifies a user account using the verification token.",
    tags=["Account Reset & Verification"]
)
@api_view(['POST'])  # Change to POST to accept a JSON body
@permission_classes([AllowAny])
def verify_account_view(request, verification_token):
    try:
        # You can now use verification_token directly, if that is your intent
        user = User.objects.filter(verification_token=verification_token).first()
        if user:
            user.is_verified = True
            user.verification_token = None
            user.token_expires_at = None
            user.save(update_fields=['is_verified', 'verification_token', 'token_expires_at'])
            return Response({"message": "Account verified successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))


@extend_schema(
    request=ResetPasswordRequestSerializer,
    responses={200: {"message": "Password reset email sent"}},
    summary="Request Password Reset",
    description="Sends a password reset email with a reset token.",
    tags=["Account Reset & Verification"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_password_reset_email_view(request):
    serializer = ResetPasswordRequestSerializer(data=request.data)
    if not serializer.is_valid():
        # Check if the error is due to a non-existing email
        if 'email' in serializer.errors:
            return Response({"error": "you do not have an account with us"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data.get('email')
    try:
        user = User.objects.get(email=email)
        
        # Generate a new reset token and prepare the reset link
        user.generate_reset_token()
        reset_link = f"{settings.PORTAL_WEB_APP_URL}/reset-password/{user.reset_password_token}"
        
        # Get user's name from profile if available
        user_name = user.email
        if hasattr(user, 'profile'):
            profile = user.profile
            name_parts = [profile.firstname]
            if profile.middlename:
                name_parts.append(profile.middlename)
            name_parts.append(profile.lastname)
            user_name = ' '.join(name_parts) if any(name_parts) else user.email
        
        # Prepare the email details with HTML formatting
        subject = "Mol - Reset Your Password"
        body = (
            f"Hi {user_name},<br><br>"
            "We received a request to reset your password for your Mol account.<br><br>"
            "To reset your password, please click the link below:<br>"
            f"<a href='{reset_link}'>{reset_link}</a><br><br>"
            "If you did not request a password reset, please ignore this email or contact support.<br><br>"
            "Note: This link will expire in 1 hour.<br><br>"
            "© 2025 Mol. All rights reserved."
        )
        recipients = [{
            "name": user_name,
            "email": user.email
        }]
        result = send_email(subject, body, recipients)
        
        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "you do not have an account with us"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        raise InternalServerError(str(e))


# Reset Password View
@extend_schema(
    request=ResetPasswordSerializer,
    responses={200: {"message": "Password reset successful"}},
    summary="Reset Password",
    description="Allows users to reset their password using the reset token.",
    tags=["Account Reset & Verification"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request, reset_token):
    try:
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(reset_password_token=reset_token).first()

            if user is None:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.token_expires_at and timezone.now() > user.token_expires_at:
                return Response({"error": "Reset token expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Update password
            user.set_password(serializer.validated_data.get('password'))
            user.reset_password_token = None
            user.token_expires_at = None
            user.save(update_fields=['password', 'reset_password_token', 'token_expires_at'])

            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
            # Return a standardized internal server error response
            raise InternalServerError(str(e))
    

@extend_schema(
    request=None,
    responses={200: {"message": "Logged out successfully"}},
    summary="Logout",
    description="Endpoint for user logout. Clears the session and logs out the user.",
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        # Return a standardized internal server error response
        raise InternalServerError(str(e))


@extend_schema(
    responses=AccountStatusSerializer,
    summary="Account Status",
    description="Returns the account status including active, staff, verified status, and the date joined.",
    tags=["Account Reset & Verification"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def account_status_view(request):
    serializer = AccountStatusSerializer(request.user, context={'request': request})
    return Response(serializer.data)




@extend_schema(
    methods=["PUT"],
    request=ChangePasswordSerializer,
    responses={
        200: {"message": "Password updated successfully."},
        400: {"description": "Bad Request"}
    },
    summary="Change Password",
    description="Allows an authenticated user to update their password by providing the current password, new password, and confirmation of the new password.",
    tags=["Authentication"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        # Check that the provided current password is correct.
        if not user.check_password(serializer.validated_data['current_password']):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Set the new password.
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)