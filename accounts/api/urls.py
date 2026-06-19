from django.urls import path
from accounts.api import views

urlpatterns = [
    path('auth/me/', views.current_user, name='api_current_user'),
    path('auth/login/', views.login_view, name='api_login'),
    path('auth/logout/', views.logout_view, name='api_logout'),
    path('auth/register/', views.register_view, name='api_register'),
    path('profile/', views.profile_view, name='api_profile'),
    path('home/', views.home_data, name='api_home'),
    path('contact/', views.contact_view, name='api_contact'),
    path('lawyers/', views.lawyer_list, name='api_lawyer_list'),
    path('lawyers/<int:lawyer_id>/', views.lawyer_detail, name='api_lawyer_detail'),
    path('appointments/', views.appointment_list, name='api_appointments'),
    path('appointments/<int:appointment_id>/', views.appointment_detail_api, name='api_appointment_detail'),
    path('chat/users/', views.chat_users, name='api_chat_users'),
    path('chat/room/<int:user_id>/', views.chat_room, name='api_chat_room'),
    path('chat/messages/<int:room_id>/', views.chat_messages, name='api_chat_messages'),
    path('chat/send/<int:room_id>/', views.send_chat_message, name='api_send_chat'),
    path('public-chat/room/', views.public_chat_room, name='api_public_chat_room'),
    path('public-chat/send/', views.send_public_message, name='api_send_public'),
    path('notifications/', views.notifications_api, name='api_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='api_mark_read'),
    path('admin/dashboard/', views.admin_dashboard_api, name='api_admin_dashboard'),
    path('admin/suspend/<int:user_id>/', views.admin_suspend_user, name='api_admin_suspend'),
    path('admin/unsuspend/<int:user_id>/', views.admin_unsuspend_user, name='api_admin_unsuspend'),
    path('admin/delete/<int:user_id>/', views.admin_delete_user, name='api_admin_delete'),
]
