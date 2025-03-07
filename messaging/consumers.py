import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import ChatRoom, Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_room_id = self.scope['url_route']['kwargs']['chatRoomId']
        self.room_group_name = f'chat_{self.chat_room_id}'

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
        message = data['message']

        # Save message to the database
        await self.save_message(sender_id, message)

        # Broadcast message to all participants in the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'senderId': sender_id,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, sender_id, message):
        sender = User.objects.get(id=sender_id)
        chat_room = ChatRoom.objects.get(id=self.chat_room_id)

        Message.objects.create(chat_room=chat_room, sender=sender, content=message)
