from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    is_group = models.BooleanField(default=True, help_text="True for group chat, False for private 1:1")
    participants = models.ManyToManyField(User, through='Participant', related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name or "Private chat"

    def participant_count(self):
        return self.participants.count()


class Participant(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participant_instances')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('room', 'user')
        ordering = ['user__first_name']


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    @property
    def sender_avatar(self):
        initials = f"{self.sender.first_name[0].upper() if self.sender.first_name else ''}{self.sender.last_name[0].upper() if self.sender.last_name else ''}"
        return initials or self.sender.username[0].upper() if self.sender.username else "U"

    @property
    def time_str(self):
        from django.utils import timezone
        now = timezone.now()
        if self.timestamp.date() == now.date():
            return self.timestamp.strftime("%H:%M")
        return self.timestamp.strftime("%m/%d %H:%M")

