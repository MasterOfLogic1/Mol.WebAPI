from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import UserProfile
from .serializers import UserProfileSerializer

@extend_schema(
    methods=["GET"],
    responses={200: UserProfileSerializer, 400: {"description": "Bad Request"}},
    summary="Retrieve User Profile",
    description="Retrieve the authenticated user's profile details.",
    tags=["Profile"]
)
@extend_schema(
    methods=["PUT"],
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer, 400: {"description": "Bad Request"}},
    summary="Update User Profile",
    description="Update the authenticated user's profile details.",
    tags=["Profile"]
)
@extend_schema(
    methods=["POST"],
    request=UserProfileSerializer,
    responses={201: UserProfileSerializer, 400: {"description": "Bad Request"}},
    summary="Create User Profile",
    description="Allows an authenticated user to create their profile.",
    tags=["Profile"]
)
@api_view(['GET', 'PUT', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method in ['PUT', 'POST']:
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
