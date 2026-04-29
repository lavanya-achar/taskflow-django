from django.contrib import admin
from .models import Task, SubTask

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'priority', 'status', 'due_date')
    list_filter = ('status', 'priority', 'project', 'created_at')
    search_fields = ('title', 'assigned_to__username', 'project__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'assigned_to', 'status', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'task__title', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at')
