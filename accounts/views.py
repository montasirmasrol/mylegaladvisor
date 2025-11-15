from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Q
from django.db import models as db_models
from .models import User, LawyerProfile, UserProfile, Appointment, LawyerRating, ChatRoom, ChatMessage, CaseFile, Notification
from .forms import UserRegistrationForm, LawyerProfileForm, UserProfileForm, AppointmentRequestForm, LawyerRatingForm, ContactForm, CaseFileForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def home(request):
    # Public homepage with top lawyers and FAQ/chat shown via template
    top_lawyers = User.objects.filter(user_type='lawyer', is_suspended=False).annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:6]
    lawyer_profiles = []
    for lawyer in top_lawyers:
        profile = getattr(lawyer, 'lawyer_profile', None)
        lawyer_profiles.append({ 'lawyer': lawyer, 'profile': profile, 'avg_rating': lawyer.avg_rating or 0 })
    contact_form = ContactForm()
    return render(request, 'accounts/home.html', { 'top_lawyer_profiles': lawyer_profiles, 'contact_form': contact_form })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                form.send()
                messages.success(request, 'Your message has been sent. We will get back to you soon.')
            except Exception as e:
                messages.error(request, f'Could not send message: {e}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    return redirect('home')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # Ensure superusers have user_type set to 'admin'
            if user.is_superuser and getattr(user, 'user_type', None) != 'admin':
                user.user_type = 'admin'
                user.save()

            if user.is_suspended:
                messages.error(request, 'Your account has been suspended temporarily. Please try again later or contact support.')
                return render(request, 'accounts/login.html')
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    user = request.user
    if user.is_lawyer():
        profile_obj = getattr(user, 'lawyer_profile', None)
        if not profile_obj:
            profile_obj = LawyerProfile.objects.create(user=user)
        form = LawyerProfileForm(instance=profile_obj)
        template = 'accounts/lawyer_profile.html'
    elif user.is_regular_user():
        profile_obj = getattr(user, 'user_profile', None)
        if not profile_obj:
            profile_obj = UserProfile.objects.create(user=user)
        form = UserProfileForm(instance=profile_obj)
        template = 'accounts/user_profile.html'
    else:
        # Admin user - Show admin dashboard with user management
        users = User.objects.filter(user_type='user').order_by('-date_joined')
        lawyers = User.objects.filter(user_type='lawyer').order_by('-date_joined')
        return render(request, 'accounts/admin_dashboard.html', {
            'users': users,
            'lawyers': lawyers,
            'user': user
        })
    
    if request.method == 'POST':
        if user.is_lawyer():
            form = LawyerProfileForm(request.POST, request.FILES, instance=profile_obj)
        else:
            form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        
        if form.is_valid():
            form.save()
            # Also update user's first_name and last_name if provided
            if 'first_name' in request.POST:
                user.first_name = request.POST.get('first_name', '')
            if 'last_name' in request.POST:
                user.last_name = request.POST.get('last_name', '')
            if 'email' in request.POST:
                user.email = request.POST.get('email', '')
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    
    return render(request, template, {
        'user': user,
        'profile': profile_obj,
        'form': form,
    })


def public_lawyer_list(request):
    category = request.GET.get('category')
    lawyers = User.objects.filter(user_type='lawyer', is_suspended=False)
    if category:
        lawyers = lawyers.filter(lawyer_profile__lawyer_type=category)
    lawyers = lawyers.annotate(avg_rating=Avg('ratings__rating'))
    lawyer_profiles = []
    for lawyer in lawyers:
        profile = getattr(lawyer, 'lawyer_profile', None)
        lawyer_profiles.append({ 'lawyer': lawyer, 'profile': profile, 'avg_rating': lawyer.avg_rating or 0 })
    return render(request, 'accounts/public_lawyer_list.html', { 'lawyer_profiles': lawyer_profiles, 'selected_category': category })


def public_lawyer_detail(request, lawyer_id):
    lawyer = get_object_or_404(User, id=lawyer_id, user_type='lawyer', is_suspended=False)
    profile = getattr(lawyer, 'lawyer_profile', None)
    avg_rating = lawyer.ratings.aggregate(v=Avg('rating'))['v'] or 0
    ratings = lawyer.ratings.select_related('user')[:20]

    rating_form = None
    if request.user.is_authenticated and request.user.is_regular_user():
        try:
            existing = LawyerRating.objects.get(lawyer=lawyer, user=request.user)
            rating_form = LawyerRatingForm(instance=existing)
        except LawyerRating.DoesNotExist:
            rating_form = LawyerRatingForm()

    if request.method == 'POST':
        if 'make_appointment' in request.POST and request.user.is_authenticated and request.user.is_regular_user():
            form = AppointmentRequestForm(request.POST)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.user = request.user
                appointment.lawyer = lawyer
                appointment.save()
                
                # Create notification for lawyer
                Notification.objects.create(
                    user=lawyer,
                    type='appointment_request',
                    message=f'New appointment request from {request.user.get_full_name() or request.user.username}',
                    related_id=appointment.id
                )
                
                # Handle uploaded case files (multiple)
                files = request.FILES.getlist('case_files')
                for f in files:
                    cf = CaseFile.objects.create(
                        user=request.user,
                        appointment=appointment,
                        file=f,
                        file_type=('image' if f.content_type.startswith('image') else 'pdf' if f.content_type == 'application/pdf' else 'video' if f.content_type.startswith('video') else 'other')
                    )

                messages.success(request, 'Appointment request sent successfully!')
                return redirect('appointments')
        elif 'rate_lawyer' in request.POST and request.user.is_authenticated and request.user.is_regular_user():
            try:
                instance = LawyerRating.objects.get(lawyer=lawyer, user=request.user)
            except LawyerRating.DoesNotExist:
                instance = None
            rating_form = LawyerRatingForm(request.POST, instance=instance)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.lawyer = lawyer
                rating.user = request.user
                rating.save()
                messages.success(request, 'Your rating has been submitted!')
                return redirect('public_lawyer_detail', lawyer_id=lawyer.id)

    appointment_form = AppointmentRequestForm()
    return render(request, 'accounts/public_lawyer_detail.html', {
        'lawyer': lawyer,
        'profile': profile,
        'avg_rating': avg_rating,
        'ratings': ratings,
        'appointment_form': appointment_form,
        'rating_form': rating_form,
    })


@login_required
def appointments(request):
    user = request.user
    if user.is_lawyer():
        # Show appointments for this lawyer
        appointments_list = Appointment.objects.filter(lawyer=user)
        template = 'accounts/lawyer_appointments.html'
    elif user.is_regular_user():
        # Show appointments for this user
        appointments_list = Appointment.objects.filter(user=user)
        template = 'accounts/user_appointments.html'
    else:
        messages.error(request, 'Invalid access.')
        return redirect('home')
    
    return render(request, template, {'appointments': appointments_list})


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    
    # Check if user has permission to view this appointment
    if not (appointment.user == user or appointment.lawyer == user or user.is_superuser):
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('home')
    
    case_files = CaseFile.objects.filter(appointment=appointment)
    case_file_form = None
    
    # Only allow users to upload files and only for accepted appointments
    if user == appointment.user and appointment.status == 'accepted':
        case_file_form = CaseFileForm()
    
    if request.method == 'POST':
        if user.is_lawyer() and appointment.lawyer == user:
            action = request.POST.get('action')
            if action == 'accept':
                appointment.status = 'accepted'
                
                # If it's an online consultation, generate Google Meet link
                if appointment.consultation_type == 'online':
                    from .google_meet import create_meet_link
                    try:
                        # First save the appointment status
                        appointment.status = 'accepted'
                        appointment.save()
                        
                        # Then try to create the meet link
                        meet_link, event_id = create_meet_link(appointment)
                        if meet_link and event_id:
                            appointment.meeting_link = meet_link
                            appointment.google_event_id = event_id
                            appointment.save()
                            messages.success(request, "Appointment accepted and Google Meet link created successfully!")
                        else:
                            messages.warning(request, "Appointment accepted but could not create Google Meet link. Please try creating the meeting link again later.")
                    except FileNotFoundError as e:
                        messages.error(request, "Google Calendar credentials not found. Please contact the administrator.")
                        logger.error(f"Google Calendar credentials error: {str(e)}")
                        return redirect('appointment_detail', appointment_id=appointment.id)
                    except Exception as e:
                        messages.error(request, "Could not create Google Meet link. Please try again or create a meeting manually.")
                        logger.error(f"Error creating Google Meet link: {str(e)}")
                        return redirect('appointment_detail', appointment_id=appointment.id)
                else:
                    # For offline appointments, just save
                    appointment.save()
                
                # Create notification for user
                Notification.objects.create(
                    user=appointment.user,
                    type='appointment_update',
                    message=f'Your appointment with {appointment.lawyer.get_full_name()} has been accepted.',
                    related_id=appointment.id
                )
                
                # Send email notification
                email_sent = send_appointment_email(appointment, 'accepted')
                
                if email_sent:
                    messages.success(request, 'Appointment accepted! Email sent to the user.')
                else:
                    messages.warning(request, 'Appointment accepted! However, email could not be sent. Please check email configuration.')
                return redirect('appointment_detail', appointment_id=appointment.id)
            
            elif action == 'reject':
                appointment.status = 'rejected'
                appointment.save()
                
                # Create notification for user
                Notification.objects.create(
                    user=appointment.user,
                    type='appointment_update',
                    message=f'Your appointment with {appointment.lawyer.get_full_name()} has been rejected.',
                    related_id=appointment.id
                )
                
                messages.info(request, 'Appointment rejected.')
                return redirect('appointment_detail', appointment_id=appointment.id)
        
        elif user == appointment.user and 'upload_files' in request.POST:
            # Accept multiple files named 'case_files'
            uploaded_files = request.FILES.getlist('case_files')
            if not uploaded_files:
                messages.error(request, 'No files selected for upload.')
            else:
                successful_uploads = 0
                for f in uploaded_files:
                    # Determine file type
                    file_type = ('image' if f.content_type.startswith('image') else 
                               'pdf' if f.content_type == 'application/pdf' else 
                               'video' if f.content_type.startswith('video') else 'other')
                    
                    try:
                        cf = CaseFile.objects.create(
                            user=user,
                            appointment=appointment,
                            file=f,
                            file_type=file_type
                        )
                        successful_uploads += 1
                    except Exception as e:
                        messages.error(request, f'Failed to upload {f.name}: {str(e)}')
                        continue

                if successful_uploads > 0:
                    # Create notification for lawyer
                    Notification.objects.create(
                        user=appointment.lawyer,
                        type='message',
                        message=f'New case file(s) uploaded by {user.get_full_name() or user.username}',
                        related_id=appointment.id
                    )
                    messages.success(request, f'{successful_uploads} file(s) uploaded successfully.')
                return redirect('appointment_detail', appointment_id=appointment.id)
    
    context = {
        'appointment': appointment,
        'case_files': case_files,
        'case_file_form': case_file_form,
    }
    
    return render(request, 'accounts/appointment_detail.html', context)


def send_appointment_email(appointment, action):
    """Send email notification to user about appointment status"""
    if action == 'accepted':
        # Check if email is configured
        if not settings.EMAIL_HOST_USER:
            print("WARNING: EMAIL_HOST_USER is not configured. Email will not be sent.")
            print("Please configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py")
            return False
        
        subject = f'Appointment Accepted - {appointment.lawyer.get_full_name() or appointment.lawyer.username}'
        
        lawyer_name = appointment.lawyer.get_full_name() or appointment.lawyer.username
        user_name = appointment.user.get_full_name() or appointment.user.username
        lawyer_type = appointment.lawyer.lawyer_profile.get_lawyer_type_display() if hasattr(appointment.lawyer, 'lawyer_profile') else 'N/A'
        
        meeting_info = ""
        if appointment.consultation_type == 'online' and appointment.meeting_link:
            meeting_info = f"""
Meeting Link: {appointment.meeting_link}
Please click the link at your appointment time to join the online consultation."""
        elif appointment.consultation_type == 'offline':
            meeting_info = f"""
This is an offline consultation. Please visit the lawyer's office at the scheduled time.
Address: {appointment.lawyer.lawyer_profile.address}"""
            
        message = f"""Hello {user_name},

Great news! Your appointment request has been accepted by {lawyer_name}.

Appointment Details:
- Date: {appointment.appointment_date}
- Time: {appointment.appointment_time}
- Lawyer: {lawyer_name}
- Lawyer Type: {lawyer_type}
- Consultation Type: {appointment.get_consultation_type_display()}
{meeting_info}

Welcome to MyLegalAdvisor! We look forward to assisting you with your legal needs.

If you have any questions or need to reschedule, please contact your lawyer.

Best regards,
MyLegalAdvisor Team"""
        
        recipient_list = [appointment.user.email]
        from_email = settings.EMAIL_HOST_USER  # Use the configured email as sender
        
        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            print(f"Email sent successfully to {appointment.user.email}")
            return True
        except Exception as e:
            print(f"Error sending email to {appointment.user.email}: {e}")
            return False
    return False


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    users = User.objects.filter(user_type='user').order_by('-date_joined')
    lawyers = User.objects.filter(user_type='lawyer').order_by('-date_joined')
    
    return render(request, 'accounts/admin_dashboard.html', {
        'users': users,
        'lawyers': lawyers,
    })


@login_required
@require_http_methods(["POST"])
def admin_suspend_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = True
    user.save()
    messages.success(request, f'{user.username} has been suspended.')
    return redirect('admin_dashboard')


@login_required
@require_http_methods(["POST"])
def admin_unsuspend_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_suspended = False
    user.save()
    messages.success(request, f'{user.username} has been unsuspended.')
    return redirect('admin_dashboard')


@login_required
@require_http_methods(["POST"])
def admin_delete_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f'{username} has been deleted.')
    return redirect('admin_dashboard')


@login_required
def private_chat(request, user_id=None):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access chat.')
        return redirect('login')
    
    if user_id:
        other_user = get_object_or_404(User, id=user_id)
        if other_user == request.user:
            messages.error(request, 'Cannot chat with yourself.')
            return redirect('private_chat')
        
        # Get or create chat room
        user1_id = min(request.user.id, other_user.id)
        user2_id = max(request.user.id, other_user.id)
        room, created = ChatRoom.objects.get_or_create(
            room_type='private',
            user1_id=user1_id,
            user2_id=user2_id,
        )
        messages_list = room.messages.all()[:50]
        return render(request, 'accounts/private_chat.html', {
            'room': room,
            'other_user': other_user,
            'messages': messages_list,
        })
    
    # List of users/lawyers to chat with
    if request.user.is_superuser:
        # Admin can see all lawyers
        chat_users = User.objects.filter(user_type='lawyer', is_suspended=False).order_by('-date_joined')
    elif request.user.is_lawyer():
        # Lawyers can see users who've messaged them and admins
        chat_rooms = ChatRoom.objects.filter(
            room_type='private'
        ).filter(
            Q(user1=request.user) | Q(user2=request.user)
        )
        user_ids = []
        for room in chat_rooms:
            if room.user1 == request.user:
                user_ids.append(room.user2.id)
            else:
                user_ids.append(room.user1.id)
        # Add regular users who have chatted and all admins
        chat_users = User.objects.filter(
            Q(id__in=user_ids) | Q(is_superuser=True),
            is_suspended=False
        ).distinct()
    elif request.user.is_regular_user():
        # Regular users should see all available lawyers
        chat_users = User.objects.filter(user_type='lawyer', is_suspended=False).order_by('-date_joined')
    else:
        chat_users = User.objects.none()
    
    return render(request, 'accounts/private_chat_list.html', {'chat_users': chat_users})


@login_required
@require_http_methods(["POST"])
def send_private_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in [room.user1, room.user2]:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    message_text = request.POST.get('message', '').strip()
    attachment = request.FILES.get('attachment')
    if not message_text and not attachment:
        return JsonResponse({'error': 'Message cannot be empty or no attachment provided'}, status=400)
    
    message = ChatMessage.objects.create(
        room=room,
        sender=request.user,
        message=message_text
    )
    if attachment:
        # Save attachment and infer type by extension
        message.attachment.save(attachment.name, attachment)
        ext = attachment.name.split('.')[-1].lower()
        if ext in ['jpg','jpeg','png','gif']:
            message.attachment_type = 'image'
        elif ext == 'pdf':
            message.attachment_type = 'pdf'
        elif ext in ['mp4','mov','avi']:
            message.attachment_type = 'video'
        else:
            message.attachment_type = 'other'
        message.save()
    
    # Create notification for the recipient
    recipient = room.user2 if request.user == room.user1 else room.user1
    Notification.objects.create(
        user=recipient,
        type='message',
        message=f'New message from {request.user.get_full_name() or request.user.username}',
        related_id=room.id
    )
    
    return JsonResponse({'success': True})


def public_chat(request):
    # Public chat available only to authenticated users
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access public chat.')
        return redirect('login')

    room, created = ChatRoom.objects.get_or_create(room_type='public', defaults={'user1': None, 'user2': None})
    messages_list = room.messages.all()[:50]
    return render(request, 'accounts/public_chat.html', {
        'room': room,
        'messages': messages_list,
    })


@login_required
@require_http_methods(["POST"])
def send_public_message(request):
    # Only authenticated users can post to public chat
    room, created = ChatRoom.objects.get_or_create(room_type='public', defaults={'user1': None, 'user2': None})
    message_text = request.POST.get('message', '').strip()
    if not message_text:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    ChatMessage.objects.create(
        room=room,
        sender=request.user,
        sender_name='',
        message=message_text
    )
    return JsonResponse({'success': True})


@require_http_methods(["GET"])
def get_chat_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check access for private rooms
    if room.room_type == 'private':
        if not request.user.is_authenticated or request.user not in [room.user1, room.user2]:
            return JsonResponse({'error': 'Access denied'}, status=403)
    
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except:
        last_id = 0
    
    messages = room.messages.filter(id__gt=last_id).order_by('created_at')[:20]
    messages_data = []
    for msg in messages:
        attachment_url = msg.attachment.url if msg.attachment else None
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.username if msg.sender else msg.sender_name,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'attachment_url': attachment_url,
            'attachment_type': msg.attachment_type,
        })
    
    return JsonResponse({'messages': messages_data})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    # Get unread count for notification bar
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'accounts/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    # If this was an AJAX request, return JSON. Otherwise redirect back to notifications page.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notifications')
