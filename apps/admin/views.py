from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from apps.account.models import User
from .serializers import UserListSerializer, UserBlockSerializer, UserStatsSerializer
from apps.shared.models import InternalServerError

def check_admin_permission(user):
    """Helper function to check if user is admin"""
    if not user.role or user.role.name != 'admin':
        return False
    return True

# List all users (Admin only)
@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number (default: 1)', required=False),
        OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Number of items per page (default: 10, max: 100)', required=False),
    ],
    responses={200: UserListSerializer(many=True)},
    summary="List All Users",
    description="Retrieves a paginated list of all users. Admin only.",
    tags=["Admin"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_users(request):
    try:
        # Check if user is admin
        if not check_admin_permission(request.user):
            return Response(
                {"error": "Only admins can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = User.objects.all().order_by('-date_joined')
        
        # Pagination
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        
        try:
            page_size = int(page_size)
            if page_size > 100:
                page_size = 100
            if page_size < 1:
                page_size = 10
        except (ValueError, TypeError):
            page_size = 10
        
        paginator = Paginator(users, page_size)
        
        try:
            users_page = paginator.page(page)
        except PageNotAnInteger:
            users_page = paginator.page(1)
        except EmptyPage:
            users_page = paginator.page(paginator.num_pages)
        
        serializer = UserListSerializer(users_page, many=True)
        
        return Response({
            'count': paginator.count,
            'page': users_page.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Block/Unblock user (Admin only)
@extend_schema(
    methods=["PUT"],
    request=UserBlockSerializer,
    responses={200: {"description": "User status updated"}, 404: {"description": "User not found"}},
    summary="Block/Unblock User",
    description="Blocks or unblocks a user by setting is_active to false or true. Admin only.",
    tags=["Admin"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def block_user(request, user_id):
    try:
        # Check if user is admin
        if not check_admin_permission(request.user):
            return Response(
                {"error": "Only admins can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = get_object_or_404(User, id=user_id)
        serializer = UserBlockSerializer(data=request.data)
        
        if serializer.is_valid():
            user.is_active = serializer.validated_data['is_active']
            user.save(update_fields=['is_active'])
            
            status_msg = "unblocked" if user.is_active else "blocked"
            return Response(
                {"message": f"User {status_msg} successfully"},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Get user statistics (Admin only)
@extend_schema(
    methods=["GET"],
    responses={200: UserStatsSerializer},
    summary="Get User Statistics",
    description="Retrieves statistics about users: total, active, inactive, and verified counts. Admin only.",
    tags=["Admin"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_statistics(request):
    try:
        # Check if user is admin
        if not check_admin_permission(request.user):
            return Response(
                {"error": "Only admins can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        verified_users = User.objects.filter(is_verified=True).count()
        
        data = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'verified_users': verified_users
        }
        
        serializer = UserStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

