from django.db import models

class TeamMember(models.Model):
    full_name = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    email_url = models.EmailField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'TeamMember'
        verbose_name = 'TeamMember'
        verbose_name_plural = 'TeamMembers'
        ordering = ['-created_at']

