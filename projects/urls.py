from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects_list, name='projects_list'),
    path('create/', views.create_project, name='create_project'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('<int:project_id>/update/', views.update_project, name='update_project'),
    path('<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('sprints/', views.sprints_list, name='sprints'),
    path('sprints/create/', views.create_sprint, name='create_sprint'),
]
