from rest_framework import serializers
from .models import ChatRoom, Message
from user.serializers import ProfileSerializer
from django.db.models import Q


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
            'timestamp',
            'is_read',
            'message_type'
        ]
        read_only_fields = ['id', 'sender', 'sender_username', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    participant1 = ProfileSerializer(read_only=True)
    participant2 = ProfileSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    last_message_at = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'participant1', 'participant2', 'created_at', 'last_message', 'last_message_at']

    def get_last_message(self, obj):
        """Get the last message content in this chat room"""
        last_msg = obj.messages.order_by('-timestamp').first()
        return last_msg.content if last_msg else None

    def get_last_message_at(self, obj):
        """Get the timestamp of the last message"""
        return obj.last_message_at