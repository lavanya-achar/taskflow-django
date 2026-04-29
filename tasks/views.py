from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Task, SubTask
from projects.models import Project
from notifications.models import Notification

@login_required(login_url='login')
def my_tasks(request):
    """List user's assigned tasks"""
    tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    # Count tasks by status
    todo_count = tasks.filter(status='todo').count()
    in_progress_count = tasks.filter(status='in_progress').count()
    review_count = tasks.filter(status='review').count()
    done_count = tasks.filter(status='done').count()
    
    context = {
        'tasks': tasks,
        'projects': projects,
        'tasks_count': tasks.count(),
        'todo_count': todo_count,
        'in_progress_count': in_progress_count,
        'review_count': review_count,
        'done_count': done_count,
    }
    return render(request, 'tasks.html', context)

@login_required(login_url='login')
def kanban(request, project_id=None):
    """Kanban board view"""
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        # Check authorization
        if request.user != project.owner and request.user not in project.members.all():
            messages.error(request, 'You do not have access to this project.')
            return redirect('projects_list')
    else:
        # Get first project
        project = Project.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).first()
        if not project:
            messages.info(request, 'Please create or join a project first.')
            return redirect('projects_list')
    
    tasks = project.tasks.all().order_by('order')
    statuses = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    
    context = {
        'project': project,
        'tasks': tasks,
        'statuses': statuses,
        'current_sprint': project.sprints.filter(status='active').first(),
    }
    return render(request, 'kanban.html', context)

@login_required(login_url='login')
def create_task(request):
    """Create a new task"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        project_id = request.POST.get('project')
        priority = request.POST.get('priority', 'medium')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        
        project = get_object_or_404(Project, id=project_id)
        
        # Check authorization
        if request.user != project.owner and request.user not in project.members.all():
            messages.error(request, 'You do not have access to this project.')
            return redirect('projects_list')
        
        assigned_to = None
        if assigned_to_id:
            assigned_to_id = int(assigned_to_id) if assigned_to_id else None
            assigned_to = assigned_to_id
        
        task = Task.objects.create(
            title=title,
            description=description,
            project=project,
            priority=priority,
            assigned_to_id=assigned_to,
            due_date=due_date if due_date else None,
            created_by=request.user
        )
        
        # Create notification
        if assigned_to:
            Notification.objects.create(
                user_id=assigned_to,
                notification_type='task_assigned',
                title='New Task Assigned',
                message=f'You have been assigned to: {title}',
                related_object_type='task',
                related_object_id=task.id
            )
        
        messages.success(request, f'Task "{title}" created successfully!')
        
        # Redirect based on referrer
        referrer = request.POST.get('referrer', 'my_tasks')
        if referrer == 'kanban':
            return redirect('kanban', project_id=project_id)
        return redirect('my_tasks')
    
    return redirect('my_tasks')

@login_required(login_url='login')
@require_POST
def update_task_status(request):
    """Update task status (for drag and drop)"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        status = data.get('status')
        
        task = get_object_or_404(Task, id=task_id)
        
        # Check authorization
        if request.user != task.project.owner and request.user not in task.project.members.all():
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        
        old_status = task.status
        task.status = status
        task.save()
        
        # Create notification if task status changed
        if task.assigned_to and old_status != status:
            Notification.objects.create(
                user=task.assigned_to,
                notification_type='task_updated',
                title='Task Status Updated',
                message=f'Task "{task.title}" status changed to {task.get_status_display()}',
                related_object_type='task',
                related_object_id=task.id
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='login')
def update_task(request, task_id):
    """Update task details"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check authorization
    if request.user != task.project.owner and request.user not in task.project.members.all():
        messages.error(request, 'You do not have access to this task.')
        return redirect('my_tasks')
    
    if request.method == 'POST':
        task.title = request.POST.get('title', task.title)
        task.description = request.POST.get('description', task.description)
        task.priority = request.POST.get('priority', task.priority)
        task.status = request.POST.get('status', task.status)
        task.due_date = request.POST.get('due_date') or task.due_date
        task.save()
        
        messages.success(request, 'Task updated successfully!')
        return redirect('my_tasks')
    
    return redirect('my_tasks')

@login_required(login_url='login')
def delete_task(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check authorization
    if request.user != task.project.owner and request.user not in task.project.members.all():
        messages.error(request, 'You do not have access to this task.')
        return redirect('my_tasks')
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('my_tasks')
    
    return redirect('my_tasks')
