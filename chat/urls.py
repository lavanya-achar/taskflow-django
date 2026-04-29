from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/rooms/', views.api_rooms, name='api_rooms'),
    path('api/messages/<int:room_id>/', views.api_messages, name='api_messages'),
    path('api/search-users/', views.api_search_users_view, name='api_search_users'),
    path('api/private/', views.api_private_view, name='api_private'),
]
