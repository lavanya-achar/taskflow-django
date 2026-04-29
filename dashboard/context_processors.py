from notifications.models import Notification


def notifications_context(request):
    """
    Context processor to add notifications count to all templates.
    This ensures the notification badge and dropdown are available on every page.
    """
    if request.user.is_authenticated:
        notifications_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    else:
        notifications_count = 0
    
    return {
        'notifications_count': notifications_count,
    }
