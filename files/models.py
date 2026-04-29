from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class FileUpload(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='uploads/files/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size_kb = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    @property
    def size_display(self):
        size = self.size_kb
        if size > 1024:
            return f"{size // 1024} MB"
        return f"{size} KB"

    @property
    def date_display(self):
        from django.utils import timezone
        if self.uploaded_at.date() == timezone.now().date():
            return self.uploaded_at.strftime('%b %d')
        return self.uploaded_at.strftime('%b %d')

    @property
    def file_icon(self):
        ext = self.title.lower().split('.')[-1] if '.' in self.title else ''
        icons = {
            'pdf': '📄',
            'png': '🖼',
            'jpg': '🖼',
            'jpeg': '🖼',
            'gif': '🖼',
            'xlsx': '📊',
            'xls': '📊',
            'doc': '📝',
            'docx': '📝',
            'yaml': '📋',
            'yml': '📋',
            'sql': '📦',
            'fig': '🎨',
            'zip': '📦',
            'rar': '📦'
        }
        return icons.get(ext, '📁')

    def get_absolute_url(self):
        return reverse('files_detail', args=[self.id])

