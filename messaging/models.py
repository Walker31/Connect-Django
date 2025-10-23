from django.db import models
from django.contrib.auth.models import User
from user.models import Profile # Assuming Profile is in the 'user' app

class ChatRoom(models.Model):
    participant1 = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='chatrooms_as_participant1'
    )
    participant2 = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='chatrooms_as_participant2'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


    class Meta:
        db_table = 'chatrooms'
        unique_together = ('participant1', 'participant2')

    def __str__(self):
        # Using .name assumes Profile model has a 'name' field
        p1_name = self.participant1.name if self.participant1.name else f"User {self.participant1.user_id}"
        p2_name = self.participant2.name if self.participant2.name else f"User {self.participant2.user_id}"
        return f"Chat between {p1_name} and {p2_name}"

class Message(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # --- ADD THIS FIELD BACK ---
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('system', 'System'), # Example types
    ]
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text' # Default to 'text'
    )
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} in room {self.chat_room.id} ({self.message_type})"