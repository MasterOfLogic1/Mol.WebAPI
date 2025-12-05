from rest_framework import permissions

class IsWriterOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow writers to edit/delete their own posts,
    and admins to edit/delete any post.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request (public)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is admin
        if request.user.role and request.user.role.name == 'admin':
            return True
        
        # Check if user is writer and owns the post
        if request.user.role and request.user.role.name == 'writer':
            return obj.created_by == request.user
        
        return False

class CanCreateBlogPost(permissions.BasePermission):
    """
    Custom permission to only allow writers and admins to create posts.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only writers and admins can create posts
        if request.user.is_authenticated:
            if request.user.role and request.user.role.name in ['admin', 'writer']:
                return True
        return False

