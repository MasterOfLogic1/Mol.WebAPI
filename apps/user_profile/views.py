from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileInputSerializer, UserWithProfileSerializer
from apps.account.models import User
from apps.shared.models import InternalServerError
from apps.shared.util import upload_file_to_minio
import uuid
from datetime import datetime

@extend_schema(
    methods=["GET"],
    responses={200: UserProfileSerializer, 400: {"description": "Bad Request"}},
    summary="Retrieve User Profile",
    description="Retrieve the authenticated user's profile details.",
    tags=["Profile"]
)
@extend_schema(
    methods=["PUT"],
    request=UserProfileInputSerializer,
    responses={200: UserProfileSerializer, 400: {"description": "Bad Request"}},
    summary="Update User Profile",
    description="Update the authenticated user's profile details. Upload thumbnail as a file in the 'thumbnail' field.",
    tags=["Profile"]
)
@extend_schema(
    methods=["POST"],
    request=UserProfileInputSerializer,
    responses={201: UserProfileSerializer, 400: {"description": "Bad Request"}},
    summary="Create User Profile",
    description="Allows an authenticated user to create their profile. Upload thumbnail as a file in the 'thumbnail' field.",
    tags=["Profile"]
)
@api_view(['GET', 'PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method in ['PUT', 'POST']:
        # Handle thumbnail upload if provided
        thumbnail_url = None
        if 'thumbnail' in request.FILES:
            thumbnail_file = request.FILES['thumbnail']
            # Generate unique filename
            file_extension = thumbnail_file.name.split('.')[-1] if '.' in thumbnail_file.name else 'jpg'
            unique_filename = f"profiles/{request.user.id}/{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            
            # Upload to MinIO
            upload_result = upload_file_to_minio(
                file=thumbnail_file,
                object_name=unique_filename,
                content_type=thumbnail_file.content_type
            )
            thumbnail_url = upload_result['url']
        
        # Use input serializer for validation (excludes thumbnail_url)
        # Since we use get_or_create, profile already exists with user set
        serializer = UserProfileInputSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            profile = serializer.save()
            # Update thumbnail_url if a new thumbnail was uploaded
            if thumbnail_url:
                profile.thumbnail_url = thumbnail_url
                profile.save()
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    methods=["GET"],
    responses={200: UserWithProfileSerializer, 404: {"description": "User not found"}},
    summary="Get User by Username",
    description="Retrieves a user's details including profile information by username. Public endpoint.",
    tags=["Profile"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_username(request, username):
    try:
        user = get_object_or_404(User, username=username)
        serializer = UserWithProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))
