from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extended user profile with additional information"""
    ROLE_CHOICES = [
        ('project_manager', 'Project Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('admin', 'Admin'),
    ]
    
    MODE_CHOICES = [
        ('beginner', 'Beginner'),
        ('professional', 'Professional'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='beginner')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        ordering = ['-created_at']
