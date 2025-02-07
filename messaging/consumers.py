import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import ChatRoom, Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.participant1 = self.scope['url_route']['kwargs']['participant1']
        self.participant2 = self.scope['url_route']['kwargs']['participant2']

        # Ensure participants exist
        self.room_group_name = f'chat_{min(self.participant1, self.participant2)}_{max(self.participant1, self.participant2)}'

        # Join the WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data['senderId']
        receiver_id = data['receiverId']
        message = data['message']
        typing = data.get('typing', False)
        read = data.get('read', False)

        # Save message to the database
        await self.save_message(sender_id, receiver_id, message)

        # Broadcast message to both participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'senderId': sender_id,
                'receiverId': receiver_id,
                'typing': typing,
                'read': read
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        chat_room, _ = ChatRoom.objects.get_or_create(participant1=sender, participant2=receiver)

        Message.objects.create(sender=sender, receiver=receiver, content=message)
