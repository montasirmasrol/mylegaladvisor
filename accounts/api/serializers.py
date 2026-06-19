from django.contrib.auth import authenticate
from django.db.models import Avg
from rest_framework import serializers
from accounts.models import (
    User, LawyerProfile, UserProfile, Appointment,
    LawyerRating, ChatRoom, ChatMessage, CaseFile, Notification,
)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'is_suspended', 'is_superuser', 'photo_url',
        ]
        read_only_fields = ['id', 'user_type', 'is_suspended', 'is_superuser']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_photo_url(self, obj):
        if obj.is_lawyer() and hasattr(obj, 'lawyer_profile') and obj.lawyer_profile.photo:
            return obj.lawyer_profile.photo.url
        if obj.is_regular_user() and hasattr(obj, 'user_profile') and obj.user_profile.photo:
            return obj.user_profile.photo.url
        return None


class LawyerProfileSerializer(serializers.ModelSerializer):
    lawyer_type_display = serializers.CharField(source='get_lawyer_type_display', read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = LawyerProfile
        fields = [
            'lawyer_type', 'lawyer_type_display', 'bio', 'experience_years',
            'phone_number', 'address', 'photo', 'photo_url',
        ]
        read_only_fields = ['photo', 'photo_url', 'lawyer_type_display']

    def get_photo_url(self, obj):
        return obj.photo.url if obj.photo else None


class UserProfileSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'date_of_birth', 'photo', 'photo_url']
        read_only_fields = ['photo', 'photo_url']

    def get_photo_url(self, obj):
        return obj.photo.url if obj.photo else None


class LawyerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    lawyer_type = serializers.CharField(allow_null=True)
    lawyer_type_display = serializers.CharField(allow_null=True)
    bio = serializers.CharField(allow_blank=True)
    experience_years = serializers.IntegerField()
    photo_url = serializers.CharField(allow_null=True)
    avg_rating = serializers.FloatField()


class LawyerRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = LawyerRating
        fields = ['id', 'rating', 'comment', 'user_name', 'created_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    lawyer_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    consultation_type_display = serializers.CharField(source='get_consultation_type_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'lawyer', 'user_name', 'lawyer_name',
            'appointment_date', 'appointment_time', 'message', 'status',
            'status_display', 'consultation_type', 'consultation_type_display',
            'meeting_link', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'lawyer', 'status', 'meeting_link', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_lawyer_name(self, obj):
        return obj.lawyer.get_full_name() or obj.lawyer.username


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'message', 'consultation_type']


class CaseFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CaseFile
        fields = ['id', 'file', 'file_url', 'file_type', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None


class ChatUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'user_type', 'photo_url']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_photo_url(self, obj):
        if obj.is_lawyer() and hasattr(obj, 'lawyer_profile') and obj.lawyer_profile.photo:
            return obj.lawyer_profile.photo.url
        if obj.is_regular_user() and hasattr(obj, 'user_profile') and obj.user_profile.photo:
            return obj.user_profile.photo.url
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender_name', 'message', 'created_at', 'attachment_url', 'attachment_type']

    def get_sender_name(self, obj):
        return obj.sender.username if obj.sender else obj.sender_name

    def get_attachment_url(self, obj):
        return obj.attachment.url if obj.attachment else None


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'type', 'type_display', 'message', 'is_read', 'created_at', 'related_id']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.ChoiceField(choices=['user', 'lawyer'])
    photo = serializers.ImageField(required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def create(self, validated_data):
        photo = validated_data.pop('photo', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        if user.user_type == 'lawyer':
            profile = LawyerProfile.objects.create(user=user, lawyer_type='other')
            if photo:
                profile.photo = photo
                profile.save()
        else:
            profile = UserProfile.objects.create(user=user)
            if photo:
                profile.photo = photo
                profile.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=150)
    message = serializers.CharField()


class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'user_type', 'is_suspended', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
