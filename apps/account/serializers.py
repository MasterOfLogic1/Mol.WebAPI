from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from .models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
import re
from apps.shared.models import CustomWebApiException

User = get_user_model()

class RegisterationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, help_text='Username (must be unique)')
    firstname = serializers.CharField(write_only=True, required=True)
    lastname = serializers.CharField(write_only=True, required=True)
    middlename = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phonenumber = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'firstname', 'lastname', 'middlename', 'phonenumber']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Extract profile data
        firstname = validated_data.pop('firstname')
        lastname = validated_data.pop('lastname')
        middlename = validated_data.pop('middlename', '')
        phonenumber = validated_data.pop('phonenumber', '')
        username = validated_data.pop('username', '').strip()
        
        email = validated_data['email']
        
        # Validate username is provided
        if not username:
            raise serializers.ValidationError({'username': 'Username is required.'})
        
        # Get or create default member role
        from .models import UserRole
        member_role, _ = UserRole.objects.get_or_create(name='member')
        
        # Create user with member role by default
        user = User.objects.create_user(
            email=email,
            password=validated_data['password'],
            username=username,
            role=member_role
        )
        
        # Create user profile
        from apps.user_profile.models import UserProfile
        UserProfile.objects.create(
            user=user,
            firstname=firstname,
            lastname=lastname,
            middlename=middlename if middlename else None,
            phonenumber=phonenumber if phonenumber else None
        )
        
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(help_text='Email or username')
    password = serializers.CharField(write_only=True)



class ResetPasswordRequestSerializer(serializers.Serializer):
    """Serializer to validate the email for password reset request"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if the email exists in the system"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer to validate and reset password"""
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        max_length=128,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Ensure passwords match"""
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Password strength check (optional)
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$", password):
            raise serializers.ValidationError(
                {"password": "Password must be at least 8 characters long and contain at least one letter and one number."}
            )

        return data


class VerificationSerializer(serializers.Serializer):
    """Serializer to handle account verification"""
    token = serializers.CharField()

    def validate_token(self, value):
        """Check if token exists and is still valid"""
        user = User.objects.filter(verification_token=value).first()

        if not user:
            raise serializers.ValidationError("Invalid verification token.")

        if user.token_expires_at and timezone.now() > user.token_expires_at:
            raise serializers.ValidationError("Verification token has expired.")

        return value
    

class AccountStatusSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    date_joined = serializers.DateTimeField()
    last_login = serializers.DateTimeField()
    id = serializers.IntegerField(source='pk', read_only=True)
    email = serializers.EmailField()
    role = serializers.CharField(source='role.name', read_only=True)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Optionally add extra fields to the token
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['user_id'] = user.id
        token['role'] = user.role.name if user.role else None
        return token

    def validate(self, attrs):
        # Support authentication with either email or username
        email_or_username = attrs.get('email')  # The field is named 'email' but can contain username
        password = attrs.get('password')
        
        # Try to find user by email or username
        from apps.account.models import User
        
        user = None
        
        # First try to find user by email
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            # If not found by email, try username
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                pass
        
        # If user found, check password
        if user and user.check_password(password):
            # Password is correct, use this user
            pass
        else:
            user = None

        if not user:
            # Raise custom error if authentication fails
            raise CustomWebApiException(
                error="Wrong username or password",
                code=status.HTTP_401_UNAUTHORIZED
            )
        
        # If the user is inactive or another check fails, you can also handle it:
        if not user.is_active:
            raise CustomWebApiException(
                error="Account is disabled",
                code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is verified
        if not user.is_verified:
            raise CustomWebApiException(
                error="Account not verified",
                code=status.HTTP_403_FORBIDDEN
            )

        # If we got here, the user is valid, so get the access token
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken.for_user(user)
        access_token['email'] = user.email
        access_token['user_id'] = user.id
        access_token['role'] = user.role.name if user.role else None

        return {
            'accessToken': str(access_token),
        }


class SendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()



class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("New password and confirmation do not match.")
        return data