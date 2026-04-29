from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction
from .models import FileUpload

@login_required
def files_view(request):
    """
    Main files page
    """
    all_files = FileUpload.objects.all().order_by('-uploaded_at')
    
    # Storage stats (global)
    total_size = sum(f.size_kb for f in all_files)
    used_gb = total_size / (1024 * 1024)
    
    context = {
        'files': all_files,
        'total_size_gb': round(used_gb, 1),
        'used_percent': min(used_gb / 10 * 100, 100),  # 10GB limit
        'recent_uploads': all_files[:5],
    }
    return render(request, 'files.html', context)

@method_decorator([login_required, csrf_exempt], name='dispatch')
class ApiUploadView(View):
    """
    API for file upload
    """
    def post(self, request):
        try:
            title = request.POST.get('title', '').strip()
            if not title:
                title = request.FILES['file'].name
            
            file_obj = request.FILES['file']
            size_kb = file_obj.size / 1024
            
            with transaction.atomic():
                file_upload = FileUpload.objects.create(
                    title=title,
                    file=file_obj,
                    uploaded_by=request.user,
                    size_kb=int(size_kb),
                    file_type=file_obj.content_type,
                )
            
            return JsonResponse({
                'success': True,
                'id': file_upload.id,
                'title': file_upload.title,
                'size': file_upload.size_display,
                'url': file_upload.file.url,
                'icon': file_upload.file_icon,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@method_decorator(login_required, name='dispatch')
class ApiFilesListView(View):
    def get(self, request):
        files = FileUpload.objects.all().order_by('-uploaded_at')
        files_data = [{
            'id': f.id,
            'title': f.title,
            'icon': f.file_icon,
            'size': f.size_display,
            'date': f.date_display,
            'url': f.file.url,
            'uploaded_by': f.uploaded_by.username if f.uploaded_by else None,
        } for f in files]
        return JsonResponse({'files': files_data})

api_upload = ApiUploadView.as_view()
api_files_list = ApiFilesListView.as_view()

