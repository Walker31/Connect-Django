from rest_framework import serializers
from .models import Message, ChatRoom
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ChatRoomSerializer(serializers.ModelSerializer):
    participant1 = UserSerializer(read_only=True)
    participant2 = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True, source='message_set')

    class Meta:
        model = ChatRoom
        fields = ['id', 'participant1', 'participant2', 'messages']
