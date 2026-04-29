from django.contrib import admin
from .models import Project, Sprint

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'start_date', 'created_at')
    list_filter = ('status', 'created_at', 'is_public')
    search_fields = ('name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('members',)

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'start_date')
    search_fields = ('name', 'project__name')
    readonly_fields = ('created_at',)
