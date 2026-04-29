from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import ChatRoom, Participant, Message
import json

User = get_user_model()

@login_required
def chat_view(request):
    """Main chat page"""
    general_room = ChatRoom.objects.filter(name='#general', is_group=True).first()
    if not general_room:
        general_room = ChatRoom.objects.create(
            name='#general',
            is_group=True,
            created_by=request.user
        )
    Participant.objects.get_or_create(room=general_room, user=request.user)

    rooms = ChatRoom.objects.filter(participants=request.user).distinct().order_by('-updated_at')[:20]

    context = {
        'rooms': rooms,
    }
    return render(request, 'chat.html', context)

@login_required
def api_search_users(request):
    """API search users for DMs"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    return JsonResponse({
        'users': [{
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'initials': (user.first_name[0] + user.last_name[0]).upper() if user.get_full_name() else user.username[0].upper(),
            'role': getattr(user.profile, 'role', 'Member'),
        } for user in users]
    })

@login_required
@require_POST
def create_private_chat(request):
    """API to create/load private chat with specific user"""
    try:
        data = json.loads(request.body)
        target_user_id = data.get('user_id')
        
        if target_user_id == request.user.id:
            return JsonResponse({'error': 'Cannot chat with self'}, status=400)
        
        target_user = get_object_or_404(User, id=target_user_id)
        
        # Find existing private room
        room = ChatRoom.objects.filter(
            is_group=False
        ).filter(
            participants__user=request.user
        ).filter(
            participants__user=target_user
        ).distinct().first()
        
        if not room:
            room = ChatRoom.objects.create(
                name='', 
                is_group=False,
                created_by=request.user
            )
            Participant.objects.create(room=room, user=request.user)
            Participant.objects.create(room=room, user=target_user)
        
        return JsonResponse({
            'room_id': room.id,
            'room_name': target_user.get_full_name(),
            'is_group': False,
            'participant_count': 2,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@method_decorator(login_required, name='dispatch')
class ApiRoomsView(View):
    def get(self, request):
        general_room = ChatRoom.objects.filter(name='#general', is_group=True).first()
        if not general_room:
            general_room = ChatRoom.objects.create(
                name='#general',
                is_group=True,
                created_by=request.user
            )
        Participant.objects.get_or_create(room=general_room, user=request.user)
        
        rooms = ChatRoom.objects.filter(participants=request.user).distinct().order_by('-updated_at')
        rooms_data = []
        for room in rooms:
            unread_count = Message.objects.filter(
                room=room, 
                is_read=False
            ).exclude(sender=request.user).count()
            
            if not room.is_group:
                other_participant = room.participants.exclude(user=request.user).first()
                room_name = other_participant.user.get_full_name() if other_participant else 'Unknown'
            else:
                room_name = room.name or f'Group {room.id}'
            
            rooms_data.append({
                'id': room.id,
                'name': room_name,
                'is_group': room.is_group,
                'participant_count': room.participants.count(),
                'updated_at': room.updated_at.isoformat(),
                'unread_count': unread_count,
            })
        return JsonResponse({'rooms': rooms_data})

@method_decorator([login_required, csrf_exempt], name='dispatch')
class ApiMessagesView(View):
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        messages = Message.objects.filter(room=room).select_related('sender').order_by('timestamp')[:50]
        msgs_data = []
        for msg in messages:
            msgs_data.append({
                'id': msg.id,
                'sender': msg.sender.get_full_name(),
                'sender_avatar': getattr(msg.sender, 'avatar', f"{msg.sender.first_name[0]}{msg.sender.last_name[0]}".upper()),
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'time_str': msg.timestamp.strftime('%H:%M'),
                'is_me': msg.sender == request.user,
            })
        return JsonResponse({'messages': msgs_data})

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        content = data.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        msg = Message.objects.create(room=room, sender=request.user, content=content)
        room.updated_at = msg.timestamp
        room.save()
        
        return JsonResponse({
            'id': msg.id,
            'sender': msg.sender.get_full_name(),
            'sender_avatar': getattr(msg.sender, 'avatar', f"{msg.sender.first_name[0]}{msg.sender.last_name[0]}".upper()),
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'time_str': msg.timestamp.strftime('%H:%M'),
            'is_me': True,
        })

api_search_users_view = api_search_users
api_private_view = create_private_chat
api_rooms = ApiRoomsView.as_view()
api_messages = ApiMessagesView.as_view()

