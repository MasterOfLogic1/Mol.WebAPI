from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from .models import BlogPost
from .serializers import BlogPostSerializer, BlogPostInputSerializer
from .permissions import IsWriterOrAdmin, CanCreateBlogPost
from apps.shared.models import InternalServerError
from apps.shared.util import upload_file_to_minio
import uuid
from datetime import datetime

# List blog posts with pagination (Public)
@extend_schema(
    methods=["GET"],
    parameters=[
        OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number (default: 1)', required=False),
        OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Number of items per page (default: 10, max: 100)', required=False),
    ],
    responses={200: BlogPostSerializer(many=True)},
    summary="List Blog Posts",
    description="Retrieves a paginated list of all blog posts. Use 'page' and 'page_size' query parameters for pagination. Public endpoint.",
    tags=["Blog"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_blog_posts(request):
    try:
        posts = BlogPost.objects.all()
        
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
        
        paginator = Paginator(posts, page_size)
        
        try:
            posts_page = paginator.page(page)
        except PageNotAnInteger:
            posts_page = paginator.page(1)
        except EmptyPage:
            posts_page = paginator.page(paginator.num_pages)
        
        serializer = BlogPostSerializer(posts_page, many=True)
        
        return Response({
            'count': paginator.count,
            'page': posts_page.number,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Get single blog post (Public)
@extend_schema(
    methods=["GET"],
    responses={200: BlogPostSerializer, 404: {"description": "Blog post not found"}},
    summary="Get Blog Post",
    description="Retrieves a single blog post by ID or slug. Public endpoint. Use /blog/4 or /blog/my-blog-post-slug",
    tags=["Blog"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_blog_post(request, identifier):
    try:
        # Try to get by ID first (if identifier is numeric)
        if identifier.isdigit():
            post = get_object_or_404(BlogPost, id=int(identifier))
        else:
            # Otherwise, try to get by slug
            post = get_object_or_404(BlogPost, slug=identifier)
        serializer = BlogPostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        raise InternalServerError(str(e))

# Create blog post (Writer and Admin only)
@extend_schema(
    methods=["POST"],
    request=BlogPostInputSerializer,
    responses={201: BlogPostSerializer, 400: {"description": "Bad Request"}},
    summary="Create Blog Post",
    description="Creates a new blog post. Writers and admins only. Upload thumbnail as a file in the 'thumbnail' field.",
    tags=["Blog"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, CanCreateBlogPost])
@parser_classes([MultiPartParser, FormParser])
def create_blog_post(request):
    try:
        # Check if user is writer or admin
        if not request.user.role or request.user.role.name not in ['admin', 'writer']:
            return Response(
                {"error": "Only writers and admins can create blog posts"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Handle thumbnail upload if provided
        thumbnail_url = None
        if 'thumbnail' in request.FILES:
            thumbnail_file = request.FILES['thumbnail']
            # Generate unique filename
            file_extension = thumbnail_file.name.split('.')[-1] if '.' in thumbnail_file.name else 'jpg'
            unique_filename = f"blog/{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            
            # Upload to MinIO
            upload_result = upload_file_to_minio(
                file=thumbnail_file,
                object_name=unique_filename,
                content_type=thumbnail_file.content_type
            )
            thumbnail_url = upload_result['url']
        
        # Use input serializer for validation (excludes thumbnail_url)
        serializer = BlogPostInputSerializer(data=request.data)
        if serializer.is_valid():
            # Set the creator to the current user
            post = serializer.save(created_by=request.user)
            # Set thumbnail_url if a thumbnail was uploaded
            if thumbnail_url:
                post.thumbnail_url = thumbnail_url
                post.save()
            return Response(BlogPostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Update blog post (Writer can only update own posts, Admin can update any)
@extend_schema(
    methods=["PUT"],
    request=BlogPostInputSerializer,
    responses={200: BlogPostSerializer, 400: {"description": "Bad Request"}, 404: {"description": "Blog post not found"}},
    summary="Update Blog Post",
    description="Updates an existing blog post. Writers can only update their own posts, admins can update any. Upload thumbnail as a file in the 'thumbnail' field. Use /blog/4/update or /blog/my-blog-post-slug/update",
    tags=["Blog"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsWriterOrAdmin])
@parser_classes([MultiPartParser, FormParser])
def update_blog_post(request, identifier):
    try:
        # Try to get by ID first (if identifier is numeric)
        if identifier.isdigit():
            post = get_object_or_404(BlogPost, id=int(identifier))
        else:
            # Otherwise, try to get by slug
            post = get_object_or_404(BlogPost, slug=identifier)
        
        # Check permissions
        if not request.user.role or request.user.role.name != 'admin':
            if not request.user.role or request.user.role.name != 'writer' or post.created_by != request.user:
                return Response(
                    {"error": "You can only edit your own posts"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Handle thumbnail upload if provided
        thumbnail_url = None
        if 'thumbnail' in request.FILES:
            thumbnail_file = request.FILES['thumbnail']
            # Generate unique filename
            file_extension = thumbnail_file.name.split('.')[-1] if '.' in thumbnail_file.name else 'jpg'
            unique_filename = f"blog/{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            
            # Upload to MinIO
            upload_result = upload_file_to_minio(
                file=thumbnail_file,
                object_name=unique_filename,
                content_type=thumbnail_file.content_type
            )
            thumbnail_url = upload_result['url']
        
        # Use input serializer for validation (excludes thumbnail_url)
        serializer = BlogPostInputSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            post = serializer.save()
            # Update thumbnail_url if a new thumbnail was uploaded
            if thumbnail_url:
                post.thumbnail_url = thumbnail_url
                post.save()
            return Response(BlogPostSerializer(post).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise InternalServerError(str(e))

# Delete blog post (Writer can only delete own posts, Admin can delete any)
@extend_schema(
    methods=["DELETE"],
    responses={204: {"description": "Blog post deleted"}, 404: {"description": "Blog post not found"}},
    summary="Delete Blog Post",
    description="Deletes a blog post. Writers can only delete their own posts, admins can delete any. Use /blog/4/delete or /blog/my-blog-post-slug/delete",
    tags=["Blog"]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsWriterOrAdmin])
def delete_blog_post(request, identifier):
    try:
        # Try to get by ID first (if identifier is numeric)
        if identifier.isdigit():
            post = get_object_or_404(BlogPost, id=int(identifier))
        else:
            # Otherwise, try to get by slug
            post = get_object_or_404(BlogPost, slug=identifier)
        
        # Check permissions
        if not request.user.role or request.user.role.name != 'admin':
            if not request.user.role or request.user.role.name != 'writer' or post.created_by != request.user:
                return Response(
                    {"error": "You can only delete your own posts"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise InternalServerError(str(e))

