from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('lawyer', 'Lawyer'),
        ('user', 'User'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    is_suspended = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
    def is_lawyer(self):
        return self.user_type == 'lawyer'
    
    def is_regular_user(self):
        return self.user_type == 'user'

    def save(self, *args, **kwargs):
        # Ensure superusers are marked as admin user_type so templates and checks
        # don't confuse a superuser with a regular user or lawyer.
        if getattr(self, 'is_superuser', False):
            self.user_type = 'admin'
        return super().save(*args, **kwargs)


class LawyerProfile(models.Model):
    LAWYER_TYPE_CHOICES = [
        ('criminal', 'Criminal Law'),
        ('civil', 'Civil Law'),
        ('family', 'Family Law'),
        ('corporate', 'Corporate Law'),
        ('immigration', 'Immigration Law'),
        ('tax', 'Tax Law'),
        ('employment', 'Employment Law'),
        ('real_estate', 'Real Estate Law'),
        ('personal_injury', 'Personal Injury Law'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lawyer_profile')
    lawyer_type = models.CharField(max_length=20, choices=LAWYER_TYPE_CHOICES)
    bio = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='lawyers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_lawyer_type_display()}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    CONSULTATION_TYPE_CHOICES = [
        ('offline', 'Offline Meeting'),
        ('online', 'Online Meeting'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments')
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lawyer_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    consultation_type = models.CharField(max_length=10, choices=CONSULTATION_TYPE_CHOICES, default='offline')
    meeting_link = models.URLField(blank=True, null=True)
    google_event_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.lawyer.username} - {self.appointment_date}"


class LawyerRating(models.Model):
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('lawyer', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lawyer.username} rated {self.rating} by {self.user.username}"


class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ('public', 'Public Chat'),
        ('private', 'Private Chat'),
    ]
    
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user1', null=True, blank=True)
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user2', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user1', 'user2']]
    
    def __str__(self):
        if self.room_type == 'public':
            return 'Public Chat Room'
        return f"Chat: {self.user1.username} - {self.user2.username}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    sender_name = models.CharField(max_length=100, blank=True)  # For public chat anonymous users
    message = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('other', 'Other'),
    ]
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sender_name = self.sender.username if self.sender else self.sender_name
        return f"{sender_name}: {self.message[:50]}"


class CaseFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='case_files')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='case_files')
    file = models.FileField(upload_to='case_files/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.file_type} - {self.uploaded_at}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('appointment_request', 'New Appointment Request'),
        ('appointment_update', 'Appointment Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_id = models.IntegerField(null=True, blank=True)  # Store related object id (appointment id, message id, etc)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.created_at}"
