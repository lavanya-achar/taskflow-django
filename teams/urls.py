from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_members, name='team'),
    path('invite/', views.invite_member, name='invite_member'),
    path('remove/<int:user_id>/<int:project_id>/', views.remove_member, name='remove_member'),
    
    # Project teams management
    path('project/<int:project_id>/teams/', views.project_teams, name='project_teams'),
    path('project/<int:project_id>/teams/create/', views.create_team, name='create_team'),
    
    # Team details and management
    path('<int:team_id>/details/', views.team_detail, name='team_detail'),
    path('<int:team_id>/invite/', views.invite_to_team, name='invite_to_team'),
    path('<int:team_id>/remove/<int:user_id>/', views.remove_from_team, name='remove_from_team'),
]
