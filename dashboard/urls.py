from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read'),
]
