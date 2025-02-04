from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User,on_delete=models.CASCADE, related_name= 'sent_messages')
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Messages'

    def __str__(self):
        return f"from {self.sender} to {self.receiver} at {self.timestamp}"

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')

    class Meta:
        db_table = 'ChatRooms'

    def __str__(self):
        return self.name
