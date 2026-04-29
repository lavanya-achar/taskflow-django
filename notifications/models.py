from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    """Notification model"""
    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('task_updated', 'Task Updated'),
        ('sprint_started', 'Sprint Started'),
        ('sprint_ended', 'Sprint Ended'),
        ('comment_added', 'Comment Added'),
        ('project_updated', 'Project Updated'),
        ('team_added', 'Team Added'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    
    # Optional related object fields
    related_object_type = models.CharField(max_length=50, blank=True, null=True)  # 'task', 'project', 'sprint', etc.
    related_object_id = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    class Meta:
        ordering = ['-created_at']
