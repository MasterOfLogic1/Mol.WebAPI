from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class Newsletter(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    verification_token = models.CharField(max_length=64, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    def generate_verification_token(self):
        """Generate a unique verification token"""
        self.verification_token = get_random_string(length=64)
        self.save(update_fields=['verification_token'])

    class Meta:
        db_table = 'Newsletter'
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
        ordering = ['-registration_date']

