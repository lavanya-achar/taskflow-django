from django.contrib import admin

from .models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'size_kb', 'file_type')
    search_fields = ('title',)
    list_filter = ('file_type', 'uploaded_at')
