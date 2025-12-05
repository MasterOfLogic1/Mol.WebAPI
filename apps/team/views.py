from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from .models import TeamMember
from .serializers import TeamMemberSerializer
from apps.shared.models import InternalServerError

# List team members with pagination (Public)
@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number (default: 1)', required=False),
        OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Number of items per page (default: 10, max: 100)', required=False),
    ],
    responses={200: TeamMemberSerializer(many=True)},
    summary="List Team Members",
    description="Retrieves a paginated list of all team members. Use 'page' and 'page_size' query parameters for pagination. Public endpoint.",
    tags=["Team"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_team_members(request):
    try:
        members = TeamMember.objects.all()
        
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
        
        paginator = Paginator(members, page_size)
        
        try:
            members_page = paginator.page(page)
        except PageNotAnInteger:
            members_page = paginator.page(1)
        except EmptyPage:
            members_page = paginator.page(paginator.num_pages)
        
        serializer = TeamMemberSerializer(members_page, many=True)
        
        return Response({
            'count': paginator.count,
            'page': members_page.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Get single team member (Public)
@extend_schema(
    methods=["GET"],
    responses={200: TeamMemberSerializer, 404: {"description": "Team member not found"}},
    summary="Get Team Member",
    description="Retrieves a single team member by ID. Public endpoint.",
    tags=["Team"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_team_member(request, member_id):
    try:
        member = get_object_or_404(TeamMember, id=member_id)
        serializer = TeamMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Create team member (Admin only)
@extend_schema(
    methods=["POST"],
    request=TeamMemberSerializer,
    responses={201: TeamMemberSerializer, 400: {"description": "Bad Request"}},
    summary="Create Team Member",
    description="Creates a new team member. Admin only.",
    tags=["Team"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_team_member(request):
    try:
        # Check if user is admin
        if not request.user.role or request.user.role.name != 'admin':
            return Response(
                {"error": "Only admins can create team members"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TeamMemberSerializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save()
            return Response(TeamMemberSerializer(member).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Update team member (Admin only)
@extend_schema(
    methods=["PUT"],
    request=TeamMemberSerializer,
    responses={200: TeamMemberSerializer, 400: {"description": "Bad Request"}, 404: {"description": "Team member not found"}},
    summary="Update Team Member",
    description="Updates an existing team member. Admin only.",
    tags=["Team"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_team_member(request, member_id):
    try:
        # Check if user is admin
        if not request.user.role or request.user.role.name != 'admin':
            return Response(
                {"error": "Only admins can update team members"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        member = get_object_or_404(TeamMember, id=member_id)
        serializer = TeamMemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Delete team member (Admin only)
@extend_schema(
    methods=["DELETE"],
    responses={204: {"description": "Team member deleted"}, 404: {"description": "Team member not found"}},
    summary="Delete Team Member",
    description="Deletes a team member. Admin only.",
    tags=["Team"]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_team_member(request, member_id):
    try:
        # Check if user is admin
        if not request.user.role or request.user.role.name != 'admin':
            return Response(
                {"error": "Only admins can delete team members"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        member = get_object_or_404(TeamMember, id=member_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise InternalServerError(str(e))

