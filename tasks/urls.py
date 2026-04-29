from django.urls import path
from . import views

urlpatterns = [
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('create/', views.create_task, name='create_task'),
    path('kanban/', views.kanban, name='kanban'),
    path('kanban/<int:project_id>/', views.kanban, name='kanban'),
    path('<int:task_id>/update/', views.update_task, name='update_task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('update-status/', views.update_task_status, name='update_task_status'),
]
