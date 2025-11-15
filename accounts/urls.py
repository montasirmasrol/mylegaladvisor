from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    # Public lawyer pages
    path('lawyers/', views.public_lawyer_list, name='lawyer_list'),
    path('lawyer/<int:lawyer_id>/', views.public_lawyer_detail, name='public_lawyer_detail'),
    # Auth-required appointments
    path('appointments/', views.appointments, name='appointments'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/suspend/<int:user_id>/', views.admin_suspend_user, name='admin_suspend_user'),
    path('admin-dashboard/unsuspend/<int:user_id>/', views.admin_unsuspend_user, name='admin_unsuspend_user'),
    path('admin-dashboard/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    # Chat
    path('chat/', views.private_chat, name='private_chat'),
    path('chat/<int:user_id>/', views.private_chat, name='private_chat_with'),
    path('chat/send/<int:room_id>/', views.send_private_message, name='send_private_message'),
    path('public-chat/', views.public_chat, name='public_chat'),
    path('public-chat/send/', views.send_public_message, name='send_public_message'),
    path('chat/messages/<int:room_id>/', views.get_chat_messages, name='get_chat_messages'),
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]

