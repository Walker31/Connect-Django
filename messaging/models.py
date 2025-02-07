from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User,on_delete=models.CASCADE, related_name= 'sent_messages')
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return f"from {self.sender} to {self.receiver} at {self.timestamp}"

class ChatRoom(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatroom_participant1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatroom_participant2')

    class Meta:
        db_table = 'chatrooms'
        unique_together = ('participant1', 'participant2')  # Ensure only one room per user pair

    def __str__(self):
        return f"Chat between {self.participant1.username} and {self.participant2.username}"

