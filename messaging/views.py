from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message, Profile
from .serializers import ChatRoomSerializer, MessageSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_room_list(request):
    
    current_profile = request.user.profile

    if request.method == 'GET':
        rooms = ChatRoom.objects.filter(
            Q(participant1=current_profile) | Q(participant2=current_profile)
        ).select_related('participant1', 'participant2')
        
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        participant2_id = request.data.get('participant2_id')
        if not participant2_id:
            return Response(
                {'error': 'participant2_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if current_profile.id == participant2_id:
            return Response(
                {'error': 'Cannot create a chat room with yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        participant2 = get_object_or_404(Profile, id=participant2_id)
        
        p1 = min(current_profile, participant2, key=lambda p: p.id)
        p2 = max(current_profile, participant2, key=lambda p: p.id)

        room, created = ChatRoom.objects.get_or_create(
            participant1=p1,
            participant2=p2
        )
        
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status_code)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_list(request, room_id):
    
    current_profile = request.user.profile
    room = get_object_or_404(ChatRoom, id=room_id)

    if not (room.participant1 == current_profile or room.participant2 == current_profile):
        return Response(
            {'error': 'You are not a participant in this chat room'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    messages = Message.objects.filter(chat_room=room)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)