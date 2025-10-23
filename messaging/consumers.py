import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, Profile
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        is_participant = await self.check_participation()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error during group_discard: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_content = data.get('message')

            if not message_content or not self.user or not self.user.is_authenticated:
                return

            message_instance = await self.save_message(message_content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': message_instance.id,
                    'message': message_instance.content,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'timestamp': message_instance.timestamp.isoformat()
                }
            )

        except json.JSONDecodeError:
            print(f"WebSocket received invalid JSON: {text_data}")
        except Exception as e:
            print(f"Error processing received WebSocket message: {e}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'id': event.get('id'),
                'message': event.get('message'),
                'sender_id': event.get('sender_id'),
                'sender_username': event.get('sender_username'),
                'timestamp': event.get('timestamp')
            }))
        except Exception as e:
             print(f"Error sending WebSocket message: {e}")

    @database_sync_to_async
    def check_participation(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if hasattr(self.user, 'profile'):
                profile = self.user.profile
                return room.participant1 == profile or room.participant2 == profile
            return False
        except ChatRoom.DoesNotExist:
             print(f"ChatRoom {self.room_id} does not exist in check_participation.")
             return False
        except Exception as e:
            print(f"Error checking participation for user {self.user.id} in room {self.room_id}: {e}")
            return False

    @database_sync_to_async
    def save_message(self, content):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message = Message.objects.create(
                chat_room=room,
                sender=self.user,
                content=content
            )
            # Optional: Update ChatRoom's last_message_at
            # room.last_message_at = message.timestamp
            # room.save(update_fields=['last_message_at'])
            return message
        except ChatRoom.DoesNotExist:
             print(f"ChatRoom {self.room_id} does not exist in save_message.")
             raise
        except Exception as e:
            print(f"Error saving message for user {self.user.id} in room {self.room_id}: {e}")
            raise