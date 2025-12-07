from rest_framework import serializers
from .models import BlogPost, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']

class BlogPostInputSerializer(serializers.Serializer):
    """Serializer for blog post creation/update - excludes thumbnail_url from request"""
    title = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    body = serializers.CharField(required=True)
    thumbnail = serializers.FileField(required=False, help_text='Upload blog post thumbnail image')
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text='List of tag names to associate with the blog post'
    )
    
    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        validated_data.pop('thumbnail', None)  # Remove thumbnail, handled in view
        blog_post = BlogPost.objects.create(**validated_data)
        
        # Create or get tags and associate them
        for tag_name in tag_names:
            if tag_name.strip():  # Only process non-empty tag names
                tag, created = Tag.objects.get_or_create(
                    name=tag_name.strip()
                )
                blog_post.tags.add(tag)
        
        return blog_post
    
    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        validated_data.pop('thumbnail', None)  # Remove thumbnail, handled in view
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_names is not None:
            instance.tags.clear()
            for tag_name in tag_names:
                if tag_name.strip():  # Only process non-empty tag names
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name.strip()
                    )
                    instance.tags.add(tag)
        
        return instance

class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer for blog post responses - includes thumbnail_url"""
    creator_fullname = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text='List of tag names to associate with the blog post'
    )
    thumbnail = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'description', 'body', 'thumbnail', 'thumbnail_url', 'tags', 'tag_names', 'date_uploaded', 'updated_at', 'created_by', 'creator_fullname']
        read_only_fields = ['id', 'slug', 'date_uploaded', 'updated_at', 'created_by', 'creator_fullname', 'tags', 'thumbnail_url']
    
    def get_creator_fullname(self, obj):
        """Returns the full name of the creator"""
        try:
            if hasattr(obj.created_by, 'profile') and obj.created_by.profile:
                profile = obj.created_by.profile
                parts = [profile.firstname]
                if profile.middlename:
                    parts.append(profile.middlename)
                parts.append(profile.lastname)
                return ' '.join(parts)
        except Exception:
            pass
        return obj.created_by.email if obj.created_by else ''
    
    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        blog_post = BlogPost.objects.create(**validated_data)
        
        # Create or get tags and associate them
        for tag_name in tag_names:
            if tag_name.strip():  # Only process non-empty tag names
                tag, created = Tag.objects.get_or_create(
                    name=tag_name.strip()
                )
                blog_post.tags.add(tag)
        
        return blog_post
    
    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_names is not None:
            instance.tags.clear()
            for tag_name in tag_names:
                if tag_name.strip():  # Only process non-empty tag names
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name.strip()
                    )
                    instance.tags.add(tag)
        
        return instance

