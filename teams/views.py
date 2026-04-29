from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from projects.models import Project
from .models import Team, TeamMember
from notifications.models import Notification

@login_required(login_url='login')
def project_teams(request, project_id):
    """List all teams in a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check authorization - only project members can view teams
    if request.user != project.owner and request.user not in project.members.all():
        messages.error(request, 'You do not have access to this project.')
        return redirect('projects_list')
    
    teams = project.teams.all().order_by('-created_at')
    is_owner = request.user == project.owner
    is_member = request.user in project.members.all()
    
    context = {
        'project': project,
        'teams': teams,
        'is_owner': is_owner,
        'is_member': is_member,
        'can_create_team': is_owner or is_member,
    }
    return render(request, 'project_teams.html', context)

@login_required(login_url='login')
def team_detail(request, team_id):
    """View team details and members"""
    team = get_object_or_404(Team, id=team_id)
    project = team.project
    
    # Check authorization - only team members and project members can view
    is_team_member = TeamMember.objects.filter(team=team, user=request.user).exists()
    is_project_member = request.user == project.owner or request.user in project.members.all()
    
    if not (is_team_member or is_project_member):
        messages.error(request, 'You do not have access to this team.')
        return redirect('projects_list')
    
    team_members = team.members.all().order_by('role', '-joined_at')
    
    context = {
        'team': team,
        'project': project,
        'team_members': team_members,
        'is_owner': request.user == team.owner,
        'is_team_member': is_team_member,
    }
    return render(request, 'team_detail.html', context)

@login_required(login_url='login')
def create_team(request, project_id):
    """Create a new team in a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check authorization - project owner and members can create teams
    is_owner = request.user == project.owner
    is_member = request.user in project.members.all()
    
    if not (is_owner or is_member):
        messages.error(request, 'You do not have permission to create teams in this project.')
        return redirect('project_teams', project_id=project_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        team = Team.objects.create(
            name=name,
            description=description,
            project=project,
            owner=request.user
        )
        
        # Add owner as first team member
        TeamMember.objects.create(
            team=team,
            user=request.user,
            role='admin'
        )
        
        messages.success(request, f'Team "{name}" created successfully!')
        return redirect('project_teams', project_id=project_id)
    
    return redirect('project_teams', project_id=project_id)

@login_required(login_url='login')
def invite_to_team(request, team_id):
    """Invite a member to a team"""
    team = get_object_or_404(Team, id=team_id)
    project = team.project
    
    # Check authorization - only team owner/admins can invite
    team_member = TeamMember.objects.filter(team=team, user=request.user).first()
    is_admin = team_member and team_member.role == 'admin'
    is_owner = request.user == team.owner
    
    if not (is_admin or is_owner):
        messages.error(request, 'You do not have permission to invite members to this team.')
        return redirect('team_detail', team_id=team_id)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', 'member')
        
        try:
            user = User.objects.get(email=email)
            
            # Check if already a team member
            if TeamMember.objects.filter(team=team, user=user).exists():
                messages.warning(request, f'User "{user.get_full_name()}" is already a member of this team.')
                return redirect('team_detail', team_id=team_id)
            
            # Add user to project if not already there
            if user not in project.members.all():
                project.members.add(user)
            
            # Add user to team
            TeamMember.objects.create(
                team=team,
                user=user,
                role=role
            )
            
            # Create notification
            Notification.objects.create(
                user=user,
                notification_type='team_added',
                title='Added to Team',
                message=f'You have been added to team "{team.name}" in project "{project.name}"',
                related_object_type='team',
                related_object_id=team.id
            )
            
            messages.success(request, f'User "{user.get_full_name()}" has been added to the team!')
        except User.DoesNotExist:
            messages.error(request, f'User with email "{email}" not found.')
        except Exception as e:
            messages.error(request, f'Error inviting member: {str(e)}')
        
        return redirect('team_detail', team_id=team_id)
    
    return redirect('team_detail', team_id=team_id)

@login_required(login_url='login')
def remove_from_team(request, team_id, user_id):
    """Remove a member from a team"""
    team = get_object_or_404(Team, id=team_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Check authorization - only team owner/admins can remove
    team_member = TeamMember.objects.filter(team=team, user=request.user).first()
    is_admin = team_member and team_member.role == 'admin'
    is_owner = request.user == team.owner
    
    if not (is_admin or is_owner):
        messages.error(request, 'You do not have permission to remove members from this team.')
        return redirect('team_detail', team_id=team_id)
    
    # Prevent removing the owner
    if team.owner == user_to_remove:
        messages.error(request, 'Cannot remove the team owner.')
        return redirect('team_detail', team_id=team_id)
    
    team_member_to_remove = get_object_or_404(TeamMember, team=team, user=user_to_remove)
    team_member_to_remove.delete()
    
    messages.success(request, f'User "{user_to_remove.get_full_name()}" has been removed from the team.')
    return redirect('team_detail', team_id=team_id)

@login_required(login_url='login')
def team_members(request):
    """List team members for user's projects"""
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().prefetch_related('teams__members__user')
    
    # Organize teams by project
    projects_with_teams = []
    for project in projects:
        teams = project.teams.all().order_by('-created_at')
        if teams.exists():
            projects_with_teams.append({
                'project': project,
                'teams': teams
            })
    
    # Get all unique team members from teams in user's projects
    team_memberships = TeamMember.objects.filter(
        team__project__in=projects
    ).select_related('user', 'team')
    
    context = {
        'team_members': team_memberships,
        'projects_with_teams': projects_with_teams,
        'members_count': team_memberships.count(),
        'projects_count': projects.count(),
        'projects': projects,
    }
    return render(request, 'team.html', context)

@login_required(login_url='login')
def invite_member(request):
    """Invite a user to a project or team"""
    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', 'member')
        project_id = request.POST.get('project_id')
        team_id = request.POST.get('team_id')
        
        try:
            user = User.objects.get(email=email)
            
            # Handle team invitation
            if team_id:
                team = get_object_or_404(Team, id=team_id)
                project = team.project
                
                # Check authorization - only team owner/admins can invite
                team_member = TeamMember.objects.filter(team=team, user=request.user).first()
                is_admin = team_member and team_member.role == 'admin'
                is_owner = request.user == team.owner
                
                if not (is_admin or is_owner):
                    messages.error(request, 'You do not have permission to invite members to this team.')
                    return redirect('team')
                
                # Check if already a team member
                if TeamMember.objects.filter(team=team, user=user).exists():
                    messages.warning(request, f'User "{user.get_full_name()}" is already a member of this team.')
                    return redirect('team')
                
                # Add user to project if not already there
                if user not in project.members.all():
                    project.members.add(user)
                
                # Add user to team
                TeamMember.objects.create(
                    team=team,
                    user=user,
                    role=role
                )
                
                # Create notification
                Notification.objects.create(
                    user=user,
                    notification_type='team_added',
                    title='Added to Team',
                    message=f'You have been added to team "{team.name}" in project "{project.name}"',
                    related_object_type='team',
                    related_object_id=team.id
                )
                
                messages.success(request, f'User "{user.get_full_name()}" has been added to the team!')
            
            # Handle project invitation (legacy - adds to default team)
            elif project_id:
                project = get_object_or_404(Project, id=project_id)
                
                # Check authorization - only owner can invite
                if request.user != project.owner:
                    messages.error(request, 'You do not have permission to invite members.')
                    return redirect('team')
                
                # Add user to project
                project.members.add(user)
                
                # Create or get default team for this project and add user
                default_team, created = Team.objects.get_or_create(
                    project=project,
                    name='Default Team'
                )
                
                # Set default team owner if it was just created
                if created:
                    default_team.owner = request.user
                    default_team.save()
                    # Add project owner to default team
                    TeamMember.objects.get_or_create(
                        team=default_team,
                        user=request.user,
                        defaults={'role': 'admin'}
                    )
                
                # Add as team member
                TeamMember.objects.get_or_create(
                    team=default_team,
                    user=user,
                    defaults={'role': role}
                )
                
                # Create notification
                Notification.objects.create(
                    user=user,
                    notification_type='team_added',
                    title='Project Invitation',
                    message=f'You have been added to project: {project.name}',
                    related_object_type='project',
                    related_object_id=project.id
                )
                
                messages.success(request, f'User "{user.get_full_name()}" has been added to the project!')
            else:
                messages.error(request, 'Please select a project or team.')
                
        except User.DoesNotExist:
            messages.error(request, f'User with email "{email}" not found.')
        except Exception as e:
            messages.error(request, f'Error inviting member: {str(e)}')
        
        return redirect('team')
    
    return redirect('team')

@login_required(login_url='login')
def remove_member(request, user_id, project_id):
    """Remove a member from a project"""
    project = get_object_or_404(Project, id=project_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Check authorization - only owner can remove
    if request.user != project.owner:
        messages.error(request, 'You do not have permission to remove members.')
        return redirect('team')
    
    # Prevent removing the owner
    if project.owner == user_to_remove:
        messages.error(request, 'Cannot remove the project owner.')
        return redirect('team')
    
    project.members.remove(user_to_remove)
    messages.success(request, f'User "{user_to_remove.get_full_name()}" has been removed from the project.')
    
    return redirect('team')
