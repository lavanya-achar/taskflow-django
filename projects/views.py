from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from datetime import datetime

from .models import Project, Sprint
from tasks.models import Task

@login_required(login_url='login')
def projects_list(request):
    """List all projects for the user"""
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('-created_at')
    
    # Calculate completion for each project
    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='done').count()
        project.total_tasks = total_tasks
        project.completed_tasks = completed_tasks
        project.completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    context = {
        'projects': projects,
        'projects_count': projects.count(),
    }
    return render(request, 'projects.html', context)

@login_required(login_url='login')
def create_project(request):
    """Create a new project"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        project = Project.objects.create(
            name=name,
            description=description,
            owner=request.user,
            start_date=start_date,
            end_date=end_date if end_date else None
        )
        
        # Add owner as member
        project.members.add(request.user)
        
        messages.success(request, f'Project "{name}" created successfully!')
        return redirect('projects_list')
    
    return redirect('projects_list')

@login_required(login_url='login')
def project_detail(request, project_id):
    """Project detail view"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check authorization
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects_list')
    
    tasks = project.tasks.all()
    sprints = project.sprints.all()
    
    context = {
        'project': project,
        'tasks': tasks,
        'sprints': sprints,
    }
    return render(request, 'project_detail.html', context)

@login_required(login_url='login')
def update_project(request, project_id):
    """Update project details"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check authorization - only owner can update
    if request.user != project.owner:
        messages.error(request, 'You do not have permission to update this project.')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == 'POST':
        project.name = request.POST.get('name', project.name)
        project.description = request.POST.get('description', project.description)
        project.status = request.POST.get('status', project.status)
        project.save()
        
        messages.success(request, 'Project updated successfully!')
        return redirect('project_detail', project_id=project_id)
    
    return redirect('project_detail', project_id=project_id)

@login_required(login_url='login')
def delete_project(request, project_id):
    """Delete a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check authorization - only owner can delete
    if request.user != project.owner:
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('projects_list')
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('projects_list')
    
    return redirect('projects_list')

@login_required(login_url='login')
def sprints_list(request):
    """List all sprints"""
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    
    sprints = Sprint.objects.filter(project__in=projects).order_by('-created_at')
    
    # Calculate completion for each sprint
    for sprint in sprints:
        total_tasks = sprint.tasks.count()
        completed_tasks = sprint.tasks.filter(status='done').count()
        sprint.total_tasks = total_tasks
        sprint.completed_tasks = completed_tasks
        sprint.completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    context = {
        'sprints': sprints,
        'projects': projects,
    }
    return render(request, 'sprints.html', context)

@login_required(login_url='login')
def create_sprint(request):
    """Create a new sprint"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        project_id = request.POST.get('project')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        project = get_object_or_404(Project, id=project_id)
        
        # Check authorization
        if request.user != project.owner and request.user not in project.members.all():
            messages.error(request, 'You do not have access to this project.')
            return redirect('sprints')
        
        sprint = Sprint.objects.create(
            name=name,
            description=description,
            project=project,
            start_date=start_date,
            end_date=end_date
        )
        
        messages.success(request, f'Sprint "{name}" created successfully!')
        return redirect('sprints')
    
    return redirect('sprints')
