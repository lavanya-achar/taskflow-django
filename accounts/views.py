from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserProfile

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def signup_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'signup.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')
    
    return render(request, 'signup.html')

from django.contrib.messages import get_messages

def logout_view(request):
    """Handle user logout"""
    storage = get_messages(request)
    for _ in storage:
        pass  # ✅ this clears messages

    logout(request)
    return redirect('login')

@login_required(login_url='login')
def settings_view(request):
    """User settings page"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        bio = request.POST.get('bio', '').strip()
        
        # Update user fields
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        
        # Update profile bio
        profile.bio = bio
        profile.save()
        
        messages.success(request, 'Your settings have been updated successfully.')
        return redirect('settings')
    
    context = {
        'profile': profile,
    }
    return render(request, 'settings.html', context)

@login_required(login_url='login')
def billing_view(request):
    """User billing and pricing page"""
    profile = request.user.profile
    context = {
        'profile': profile,
    }
    return render(request, 'billing.html', context)

@login_required(login_url='login')
@require_POST
def switch_mode(request):
    """Switch between beginner and professional mode"""
    profile = request.user.profile
    mode = request.POST.get('mode', 'beginner')
    
    if mode not in ['beginner', 'professional']:
        return JsonResponse({'success': False, 'error': 'Invalid mode'}, status=400)
    
    profile.mode = mode
    profile.save()
    
    return JsonResponse({
        'success': True,
        'mode': mode,
        'message': f'Switched to {mode.capitalize()} mode'
    })

@login_required(login_url='login')
@require_POST
def delete_account(request):
    """Delete user account"""
    user = request.user
    username = user.username
    
    # Delete user account (this also deletes related profile due to CASCADE)
    user.delete()
    logout(request)
    
    return JsonResponse({
        'success': True,
        'message': 'Account deleted successfully'
    })
