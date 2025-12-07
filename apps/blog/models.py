from django.db import models
from apps.account.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    body = models.TextField()
    thumbnail_url = models.URLField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='blog_posts', blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')

    def __str__(self):
        return self.title

    @property
    def creator_fullname(self):
        """Returns the full name of the creator"""
        if hasattr(self.created_by, 'profile') and self.created_by.profile:
            profile = self.created_by.profile
            parts = [profile.firstname]
            if profile.middlename:
                parts.append(profile.middlename)
            parts.append(profile.lastname)
            return ' '.join(parts)
        return self.created_by.email if self.created_by else ''

    class Meta:
        db_table = 'BlogPost'
        verbose_name = 'BlogPost'
        verbose_name_plural = 'BlogPosts'
        ordering = ['-date_uploaded']

