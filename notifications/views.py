from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime

from .models import Notification

@login_required(login_url='login')
def notifications_list(request):
    """Get user's notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)

@login_required(login_url='login')
@require_POST
def mark_as_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.read_at = datetime.now()
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required(login_url='login')
def unread_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required(login_url='login')
def get_notifications_json(request):
    """Get user's notifications as JSON for dropdown"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    data = {
        'notifications': [
            {
                'id': notif.id,
                'message': notif.message,
                'is_read': notif.is_read,
                'created_at': notif.created_at.strftime('%I:%M %p'),
                'notification_type': notif.notification_type,
            }
            for notif in notifications
        ]
    }
    return JsonResponse(data)

@login_required(login_url='login')
@require_POST
def mark_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=datetime.now())
    return JsonResponse({'success': True})
