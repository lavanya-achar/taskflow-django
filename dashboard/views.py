from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from datetime import datetime, timedelta

from projects.models import Project, Sprint
from tasks.models import Task
from notifications.models import Notification
from teams.models import TeamMember

@login_required(login_url='login')
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    
    # Get user's projects (all for calculations)
    all_projects = Project.objects.filter(
        Q(owner=user) | Q(members=user)
    ).distinct()
    
    # Get limited projects for display
    projects = all_projects[:4]
    
    # Calculate project completion
    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='done').count()
        project.total_tasks = total_tasks
        project.completed_tasks = completed_tasks
        project.completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get active projects count
    active_projects_count = all_projects.filter(status='active').count()
    
    # Get user's tasks
    user_tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(project__members=user)
    ).distinct()
    
    my_tasks_count = user_tasks.count()
    tasks_in_progress = user_tasks.filter(status='in_progress').count()
    tasks_due_this_week = user_tasks.filter(
        due_date__gte=datetime.now().date(),
        due_date__lte=datetime.now().date() + timedelta(days=7)
    ).count()
    overdue_tasks = user_tasks.filter(due_date__lt=datetime.now().date()).count()
    
    # Get completion rate
    total_completed = user_tasks.filter(status='done').count()
    completion_rate = (total_completed / my_tasks_count * 100) if my_tasks_count > 0 else 0
    
    # Get current and next sprints
    current_sprint = Sprint.objects.filter(
        status='active',
        project__in=all_projects
    ).first()
    
    next_sprint = Sprint.objects.filter(
        status='planned',
        project__in=all_projects
    ).order_by('start_date').first()
    
    if current_sprint:
        total_sprint_tasks = current_sprint.tasks.count()
        completed_sprint_tasks = current_sprint.tasks.filter(status='done').count()
        current_sprint.total_tasks = total_sprint_tasks
        current_sprint.completed_tasks = completed_sprint_tasks
        current_sprint.completion_percentage = (completed_sprint_tasks / total_sprint_tasks * 100) if total_sprint_tasks > 0 else 0
    
    if next_sprint:
        total_next_tasks = next_sprint.tasks.count()
        next_sprint.total_tasks = total_next_tasks
    
    # Get user's assigned tasks
    user_assigned_tasks = Task.objects.filter(assigned_to=user).order_by('due_date')[:4]

    # Get notifications
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
    notifications_count = Notification.objects.filter(user=user, is_read=False).count()
    
    # Get recent activities
    recent_activities = Notification.objects.filter(user=user).order_by('-created_at')[:3]
    
    # Format today's date
    today = datetime.now()
    today_str = today.strftime('%A, %B %d, %Y')
    
    # Current sprint info
    if current_sprint:
        current_sprint_info = f"{current_sprint.name} ends in {(current_sprint.end_date - today.date()).days} days"
    else:
        current_sprint_info = "No active sprint"
    
    context = {
        'projects': projects,
        'projects_count': all_projects.count(),
        'active_projects_count': active_projects_count,
        'my_tasks_count': my_tasks_count,
        'tasks_in_progress': tasks_in_progress,
        'tasks_due_this_week': tasks_due_this_week,
        'overdue_tasks': overdue_tasks,
        'completion_rate': int(completion_rate),
        'completion_rate_change': 12,
        'current_sprint': current_sprint,
        'next_sprint': next_sprint,
        'user_tasks': user_assigned_tasks,
        'notifications': notifications,
        'notifications_count': notifications_count,
        'recent_activities': recent_activities,
        'today_date': today_str,
        'current_sprint_info': current_sprint_info,
        'new_projects_this_month': 1,
    }
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def search_view(request):
    """Search across tasks and projects"""
    query = request.GET.get('q', '')
    results = {
        'tasks': [],
        'projects': [],
    }
    
    if query:
        user = request.user
        # Search tasks
        tasks = Task.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            Q(assigned_to=user) | Q(project__members=user)
        ).values('id', 'title', 'project__name')[:5]
        results['tasks'] = list(tasks)
        
        # Search projects
        projects = Project.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            Q(owner=user) | Q(members=user)
        ).values('id', 'name')[:5]
        results['projects'] = list(projects)
    
    return JsonResponse(results)

@login_required(login_url='login')
def mark_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=datetime.now()
        )
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
