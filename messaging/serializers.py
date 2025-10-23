from rest_framework import serializers
from .models import ChatRoom, Message
from user.serializers import ProfileSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = [
            'id', 
            'chat_room', 
            'sender', 
            'sender_username', 
            'content', 
            'timestamp'
        ]
        read_only_fields = ['id', 'sender', 'sender_username', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    participant1 = ProfileSerializer(read_only=True)
    participant2 = ProfileSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'participant1', 'participant2', 'created_at']