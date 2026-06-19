import logging
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.models import (
    User, LawyerProfile, UserProfile, Appointment,
    LawyerRating, ChatRoom, ChatMessage, CaseFile, Notification,
)
from accounts.api.serializers import (
    UserSerializer, LawyerProfileSerializer, UserProfileSerializer,
    LawyerListSerializer, LawyerRatingSerializer, AppointmentSerializer,
    AppointmentCreateSerializer, CaseFileSerializer, ChatUserSerializer,
    ChatMessageSerializer, NotificationSerializer, RegisterSerializer,
    LoginSerializer, ContactSerializer, AdminUserSerializer,
)
from accounts.views import send_appointment_email

logger = logging.getLogger(__name__)

LAWYER_TYPE_LABELS = dict(LawyerProfile.LAWYER_TYPE_CHOICES)


def _lawyer_to_dict(lawyer, avg_rating=None):
    profile = getattr(lawyer, 'lawyer_profile', None)
    return {
        'id': lawyer.id,
        'username': lawyer.username,
        'full_name': lawyer.get_full_name() or lawyer.username,
        'lawyer_type': profile.lawyer_type if profile else None,
        'lawyer_type_display': profile.get_lawyer_type_display() if profile else None,
        'bio': profile.bio if profile else '',
        'experience_years': profile.experience_years if profile else 0,
        'phone_number': profile.phone_number if profile else '',
        'address': profile.address if profile else '',
        'photo_url': profile.photo.url if profile and profile.photo else None,
        'avg_rating': float(avg_rating or 0),
    }


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def current_user(request):
    if not request.user.is_authenticated:
        return Response({'user': None})
    return Response({'user': UserSerializer(request.user).data})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    if not user:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
    if user.is_superuser and getattr(user, 'user_type', None) != 'admin':
        user.user_type = 'admin'
        user.save()
    if user.is_suspended:
        return Response({'error': 'Your account has been suspended.'}, status=status.HTTP_403_FORBIDDEN)
    login(request, user)
    return Response({'user': UserSerializer(user).data, 'message': f'Welcome back, {user.username}!'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({
        'message': f'Account created for {user.username}! Please login.',
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def profile_view(request):
    user = request.user
    if user.is_superuser and user.user_type == 'admin':
        return Response({'error': 'Use admin dashboard for admin profile.'}, status=status.HTTP_400_BAD_REQUEST)

    if user.is_lawyer():
        profile_obj, _ = LawyerProfile.objects.get_or_create(user=user, defaults={'lawyer_type': 'other'})
        if request.method == 'GET':
            return Response({
                'user': UserSerializer(user).data,
                'profile': LawyerProfileSerializer(profile_obj).data,
                'profile_type': 'lawyer',
            })
        form_data = request.data.copy()
        serializer = LawyerProfileSerializer(profile_obj, data=form_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        for field in ('first_name', 'last_name', 'email'):
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response({
            'message': 'Profile updated successfully!',
            'user': UserSerializer(user).data,
            'profile': LawyerProfileSerializer(profile_obj).data,
        })

    profile_obj, _ = UserProfile.objects.get_or_create(user=user)
    if request.method == 'GET':
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile_obj).data,
            'profile_type': 'user',
        })
    serializer = UserProfileSerializer(profile_obj, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    for field in ('first_name', 'last_name', 'email'):
        if field in request.data:
            setattr(user, field, request.data[field])
    user.save()
    return Response({
        'message': 'Profile updated successfully!',
        'user': UserSerializer(user).data,
        'profile': UserProfileSerializer(profile_obj).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def home_data(request):
    top_lawyers = User.objects.filter(
        user_type='lawyer', is_suspended=False
    ).annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:6]
    lawyers = [_lawyer_to_dict(l, l.avg_rating) for l in top_lawyers]
    return Response({'top_lawyers': lawyers})


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_view(request):
    serializer = ContactSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        send_mail(
            f"[Contact] {data['subject']}",
            f"From: {data['name']} <{data['email']}>\n\n{data['message']}",
            settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return Response({'message': 'Your message has been sent. We will get back to you soon.'})
    except Exception as e:
        return Response({'error': f'Could not send message: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lawyer_list(request):
    category = request.GET.get('category')
    lawyers = User.objects.filter(user_type='lawyer', is_suspended=False)
    if category:
        lawyers = lawyers.filter(lawyer_profile__lawyer_type=category)
    lawyers = lawyers.annotate(avg_rating=Avg('ratings__rating'))
    return Response({
        'lawyers': [_lawyer_to_dict(l, l.avg_rating) for l in lawyers],
        'categories': [{'value': k, 'label': v} for k, v in LawyerProfile.LAWYER_TYPE_CHOICES],
        'selected_category': category,
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def lawyer_detail(request, lawyer_id):
    lawyer = get_object_or_404(User, id=lawyer_id, user_type='lawyer', is_suspended=False)
    profile = getattr(lawyer, 'lawyer_profile', None)
    avg_rating = lawyer.ratings.aggregate(v=Avg('rating'))['v'] or 0
    ratings = LawyerRatingSerializer(lawyer.ratings.select_related('user')[:20], many=True).data

    if request.method == 'GET':
        user_rating = None
        if request.user.is_authenticated and request.user.is_regular_user():
            existing = LawyerRating.objects.filter(lawyer=lawyer, user=request.user).first()
            if existing:
                user_rating = LawyerRatingSerializer(existing).data
        return Response({
            'lawyer': _lawyer_to_dict(lawyer, avg_rating),
            'ratings': ratings,
            'user_rating': user_rating,
        })

    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    action = request.data.get('action')

    if action == 'appointment' and request.user.is_regular_user():
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save(user=request.user, lawyer=lawyer)
        Notification.objects.create(
            user=lawyer,
            type='appointment_request',
            message=f'New appointment request from {request.user.get_full_name() or request.user.username}',
            related_id=appointment.id,
        )
        files = request.FILES.getlist('case_files')
        for f in files:
            file_type = (
                'image' if f.content_type.startswith('image') else
                'pdf' if f.content_type == 'application/pdf' else
                'video' if f.content_type.startswith('video') else 'other'
            )
            CaseFile.objects.create(user=request.user, appointment=appointment, file=f, file_type=file_type)
        return Response({
            'message': 'Appointment request sent successfully!',
            'appointment': AppointmentSerializer(appointment).data,
        }, status=status.HTTP_201_CREATED)

    if action == 'rate' and request.user.is_regular_user():
        instance = LawyerRating.objects.filter(lawyer=lawyer, user=request.user).first()
        rating_data = {
            'rating': request.data.get('rating'),
            'comment': request.data.get('comment', ''),
        }
        if instance:
            instance.rating = int(rating_data['rating'])
            instance.comment = rating_data['comment']
            instance.save()
        else:
            LawyerRating.objects.create(
                lawyer=lawyer, user=request.user,
                rating=int(rating_data['rating']), comment=rating_data['comment'],
            )
        return Response({'message': 'Your rating has been submitted!'})

    return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    user = request.user
    if user.is_lawyer():
        qs = Appointment.objects.filter(lawyer=user)
    elif user.is_regular_user():
        qs = Appointment.objects.filter(user=user)
    else:
        return Response({'error': 'Invalid access.'}, status=status.HTTP_403_FORBIDDEN)
    return Response({'appointments': AppointmentSerializer(qs, many=True).data})


@api_view(['GET', 'PATCH', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def appointment_detail_api(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    if not (appointment.user == user or appointment.lawyer == user or user.is_superuser):
        return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        case_files = CaseFileSerializer(
            CaseFile.objects.filter(appointment=appointment), many=True
        ).data
        return Response({
            'appointment': AppointmentSerializer(appointment).data,
            'case_files': case_files,
            'can_upload': user == appointment.user and appointment.status == 'accepted',
            'can_manage': user.is_lawyer() and appointment.lawyer == user,
        })

    if request.method == 'PATCH' and user.is_lawyer() and appointment.lawyer == user:
        action = request.data.get('action')
        if action == 'accept':
            appointment.status = 'accepted'
            if appointment.consultation_type == 'online':
                from accounts.google_meet import create_meet_link
                try:
                    appointment.save()
                    meet_link, event_id = create_meet_link(appointment)
                    if meet_link and event_id:
                        appointment.meeting_link = meet_link
                        appointment.google_event_id = event_id
                    appointment.save()
                except Exception as e:
                    logger.error(f"Google Meet error: {e}")
                    appointment.save()
            else:
                appointment.save()
            Notification.objects.create(
                user=appointment.user,
                type='appointment_update',
                message=f'Your appointment with {appointment.lawyer.get_full_name()} has been accepted.',
                related_id=appointment.id,
            )
            send_appointment_email(appointment, 'accepted')
            return Response({'message': 'Appointment accepted!', 'appointment': AppointmentSerializer(appointment).data})
        if action == 'reject':
            appointment.status = 'rejected'
            appointment.save()
            Notification.objects.create(
                user=appointment.user,
                type='appointment_update',
                message=f'Your appointment with {appointment.lawyer.get_full_name()} has been rejected.',
                related_id=appointment.id,
            )
            return Response({'message': 'Appointment rejected.', 'appointment': AppointmentSerializer(appointment).data})

    if request.method == 'POST' and user == appointment.user and appointment.status == 'accepted':
        uploaded_files = request.FILES.getlist('case_files')
        if not uploaded_files:
            return Response({'error': 'No files selected.'}, status=status.HTTP_400_BAD_REQUEST)
        count = 0
        for f in uploaded_files:
            file_type = (
                'image' if f.content_type.startswith('image') else
                'pdf' if f.content_type == 'application/pdf' else
                'video' if f.content_type.startswith('video') else 'other'
            )
            CaseFile.objects.create(user=user, appointment=appointment, file=f, file_type=file_type)
            count += 1
        Notification.objects.create(
            user=appointment.lawyer,
            type='message',
            message=f'New case file(s) uploaded by {user.get_full_name() or user.username}',
            related_id=appointment.id,
        )
        return Response({'message': f'{count} file(s) uploaded successfully.'})

    return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_users(request):
    user = request.user
    if user.is_superuser:
        chat_users_qs = User.objects.filter(user_type='lawyer', is_suspended=False).order_by('-date_joined')
    elif user.is_lawyer():
        chat_rooms = ChatRoom.objects.filter(room_type='private').filter(
            Q(user1=user) | Q(user2=user)
        )
        user_ids = []
        for room in chat_rooms:
            user_ids.append(room.user2.id if room.user1 == user else room.user1.id)
        chat_users_qs = User.objects.filter(
            Q(id__in=user_ids) | Q(is_superuser=True), is_suspended=False
        ).distinct()
    elif user.is_regular_user():
        chat_users_qs = User.objects.filter(user_type='lawyer', is_suspended=False).order_by('-date_joined')
    else:
        chat_users_qs = User.objects.none()
    return Response({'users': ChatUserSerializer(chat_users_qs, many=True).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return Response({'error': 'Cannot chat with yourself.'}, status=status.HTTP_400_BAD_REQUEST)
    user1_id = min(request.user.id, other_user.id)
    user2_id = max(request.user.id, other_user.id)
    room, _ = ChatRoom.objects.get_or_create(
        room_type='private', user1_id=user1_id, user2_id=user2_id,
    )
    return Response({
        'room_id': room.id,
        'other_user': ChatUserSerializer(other_user).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def chat_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if room.room_type == 'private':
        if not request.user.is_authenticated or request.user not in [room.user1, room.user2]:
            return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    last_id = int(request.GET.get('last_id', 0))
    messages = room.messages.filter(id__gt=last_id).order_by('created_at')[:20]
    return Response({'messages': ChatMessageSerializer(messages, many=True).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def send_chat_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in [room.user1, room.user2]:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    message_text = request.data.get('message', '').strip()
    attachment = request.FILES.get('attachment')
    if not message_text and not attachment:
        return Response({'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
    message = ChatMessage.objects.create(room=room, sender=request.user, message=message_text)
    if attachment:
        message.attachment.save(attachment.name, attachment)
        ext = attachment.name.split('.')[-1].lower()
        type_map = {'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
                    'pdf': 'pdf', 'mp4': 'video', 'mov': 'video', 'avi': 'video'}
        message.attachment_type = type_map.get(ext, 'other')
        message.save()
    recipient = room.user2 if request.user == room.user1 else room.user1
    Notification.objects.create(
        user=recipient, type='message',
        message=f'New message from {request.user.get_full_name() or request.user.username}',
        related_id=room.id,
    )
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_chat_room(request):
    room, _ = ChatRoom.objects.get_or_create(room_type='public', defaults={'user1': None, 'user2': None})
    return Response({'room_id': room.id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_public_message(request):
    room, _ = ChatRoom.objects.get_or_create(room_type='public', defaults={'user1': None, 'user2': None})
    message_text = request.data.get('message', '').strip()
    if not message_text:
        return Response({'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
    ChatMessage.objects.create(room=room, sender=request.user, message=message_text)
    return Response({'success': True})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notifications_api(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        notifications.update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})
    unread_count = notifications.filter(is_read=False).count()
    return Response({
        'notifications': NotificationSerializer(notifications, many=True).data,
        'unread_count': unread_count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_api(request):
    if not request.user.is_superuser:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.filter(user_type='user').order_by('-date_joined')
    lawyers = User.objects.filter(user_type='lawyer').order_by('-date_joined')
    return Response({
        'users': AdminUserSerializer(users, many=True).data,
        'lawyers': AdminUserSerializer(lawyers, many=True).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_suspend_user(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = True
    user.save()
    return Response({'message': f'{user.username} has been suspended.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_unsuspend_user(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = False
    user.save()
    return Response({'message': f'{user.username} has been unsuspended.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    return Response({'message': f'{username} has been deleted.'})
