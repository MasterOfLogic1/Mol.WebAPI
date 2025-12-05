from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from .models import Course
from .serializers import CourseSerializer
from apps.shared.models import InternalServerError

# List courses with pagination (Public)
@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number (default: 1)', required=False),
        OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Number of items per page (default: 10, max: 100)', required=False),
    ],
    responses={200: CourseSerializer(many=True)},
    summary="List Courses",
    description="Retrieves a paginated list of all courses. Use 'page' and 'page_size' query parameters for pagination. Public endpoint.",
    tags=["Course"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_courses(request):
    try:
        courses = Course.objects.all()
        
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
        
        paginator = Paginator(courses, page_size)
        
        try:
            courses_page = paginator.page(page)
        except PageNotAnInteger:
            courses_page = paginator.page(1)
        except EmptyPage:
            courses_page = paginator.page(paginator.num_pages)
        
        serializer = CourseSerializer(courses_page, many=True)
        
        return Response({
            'count': paginator.count,
            'page': courses_page.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Get single course (Public)
@extend_schema(
    methods=["GET"],
    responses={200: CourseSerializer, 404: {"description": "Course not found"}},
    summary="Get Course",
    description="Retrieves a single course by ID. Public endpoint.",
    tags=["Course"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_course(request, course_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Create course (Admin only)
@extend_schema(
    methods=["POST"],
    request=CourseSerializer,
    responses={201: CourseSerializer, 400: {"description": "Bad Request"}},
    summary="Create Course",
    description="Creates a new course. Admin only.",
    tags=["Course"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    try:
        # Check if user is admin
        if not request.user.role or request.user.role.name != 'admin':
            return Response(
                {"error": "Only admins can create courses"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Update course (Admin only)
@extend_schema(
    methods=["PUT"],
    request=CourseSerializer,
    responses={200: CourseSerializer, 400: {"description": "Bad Request"}, 404: {"description": "Course not found"}},
    summary="Update Course",
    description="Updates an existing course. Admin only.",
    tags=["Course"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_course(request, course_id):
    try:
        # Check if user is admin
        if not request.user.role or request.user.role.name != 'admin':
            return Response(
                {"error": "Only admins can update courses"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        course = get_object_or_404(Course, id=course_id)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Delete course (Admin only)
@extend_schema(
    methods=["DELETE"],
    responses={204: {"description": "Course deleted"}, 404: {"description": "Course not found"}},
    summary="Delete Course",
    description="Deletes a course. Admin only.",
    tags=["Course"]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course(request, course_id):
    try:
        # Check if user is admin
        if not request.user.role or request.user.role.name != 'admin':
            return Response(
                {"error": "Only admins can delete courses"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise InternalServerError(str(e))

