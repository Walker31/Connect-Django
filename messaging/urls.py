from django.urls import path
from .views import chat_room_list, message_list

urlpatterns = [
    path('rooms/', chat_room_list, name='chat-room-list'),
    path('rooms/<int:room_id>/messages/', message_list, name='message-list'),
]