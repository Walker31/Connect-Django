from django.urls import path
from .views import ChatRoomListView, SendMessageView

urlpatterns = [
    path('rooms/', ChatRoomListView.as_view(), name='chat-room-list'),
    path('send-message/', SendMessageView.as_view(), name='send-message'),
]
