from django.http import JsonResponse
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import status
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class ChatRoomListView(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')

        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch chat rooms where the user is either participant1 or participant2
        rooms = ChatRoom.objects.filter(Q(participant1_id=user_id) | Q(participant2_id=user_id))
        serializer = ChatRoomSerializer(rooms, many=True)

        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        participant1_id = request.POST.get('participant1')
        participant2_id = request.POST.get('participant2')

        if not participant1_id or not participant2_id:
            return JsonResponse({'error': 'Both participants are required'}, status=status.HTTP_400_BAD_REQUEST)

        participant1 = get_object_or_404(User, id=participant1_id)
        participant2 = get_object_or_404(User, id=participant2_id)

        # Ensure consistent ordering of participants
        room, created = ChatRoom.objects.get_or_create(
            participant1=min(participant1, participant2, key=lambda x: x.id),
            participant2=max(participant1, participant2, key=lambda x: x.id)
        )

        serializer = ChatRoomSerializer(room)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class SendMessageView(APIView):
    def post(self, request):
        sender_id = request.POST.get('sender')
        receiver_id = request.POST.get('receiver')
        message = request.POST.get('content')

        if not sender_id or not receiver_id or not message:
            return JsonResponse({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        sender = get_object_or_404(User, id=sender_id)
        receiver = get_object_or_404(User, id=receiver_id)

        # Ensure chat room exists
        chat_room, _ = ChatRoom.objects.get_or_create(
            participant1=min(sender, receiver, key=lambda x: x.id),
            participant2=max(sender, receiver, key=lambda x: x.id)
        )

        # Save message
        msg = Message.objects.create(sender=sender, receiver=receiver, content=message)
        serializer = MessageSerializer(msg)

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, safe=False)
