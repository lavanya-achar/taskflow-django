from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('api/get/', views.get_notifications_json, name='get_notifications_json'),
    path('api/mark-all-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_notification_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
]
