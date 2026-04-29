from django.urls import path
from . import views

urlpatterns = [
    path('', views.files_view, name='files'),
    path('api/upload/', views.api_upload, name='api_upload'),
    path('api/list/', views.api_files_list, name='api_files_list'),
]

