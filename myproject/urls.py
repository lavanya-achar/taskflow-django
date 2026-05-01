from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('team/', include('teams.urls')),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),
    path('files/', include('files.urls')),
    path('analytics/', include('analytics.urls')),

    # 👇 THIS IS IMPORTANT
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
]