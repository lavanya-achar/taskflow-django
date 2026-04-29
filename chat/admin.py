from django.contrib import admin
from .models import ChatRoom, Participant, Message

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1
    raw_id_fields = ('user',)

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_group', 'participant_count', 'created_by', 'created_at')
    list_filter = ('is_group', 'created_at')
    search_fields = ('name', 'created_by__username')
    inlines = [ParticipantInline]

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Members'

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('user__username', 'room__name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'content_preview', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('content', 'sender__username', 'room__name')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Message'

