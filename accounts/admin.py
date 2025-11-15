from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LawyerProfile, UserProfile, Appointment, LawyerRating, ChatRoom, ChatMessage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_suspended', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'is_suspended']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type', 'is_suspended')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'lawyer_type', 'experience_years', 'phone_number']
    list_filter = ['lawyer_type']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'date_of_birth']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'lawyer', 'appointment_date', 'appointment_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date']
    search_fields = ['user__username', 'lawyer__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LawyerRating)
class LawyerRatingAdmin(admin.ModelAdmin):
    list_display = ['lawyer', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['lawyer__username', 'user__username']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['room_type', 'user1', 'user2', 'created_at']
    list_filter = ['room_type', 'created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'sender_name', 'message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message', 'sender__username', 'sender_name']
