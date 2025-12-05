from django.db import models
from apps.account.models import User

def user_directory_path(instance, filename):
    # Extract the file extension (if any)
    ext = filename.split('.')[-1] if '.' in filename else ''
    # Create the new filename using the user's id
    new_filename = f"{instance.user.id}.{ext}" if ext else f"{instance.user.id}"
    # Save the file inside the public_html folder
    return f'rockae_user_profile/{new_filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, null=True, blank=True)
    phonenumber = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.lastname

    class Meta:
        db_table = 'UserProfile'
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfile'
       