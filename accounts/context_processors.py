from django.conf import settings

def unread_notifications(request):
    """Return unread notification count for the current user.

    Adds `unread_notification_count` to the template context for authenticated users.
    """
    try:
        if request.user.is_authenticated:
            count = request.user.notifications.filter(is_read=False).count()
        else:
            count = 0
    except Exception:
        # If notifications relation is not available for some reason, return 0
        count = 0
    return {
        'unread_notification_count': count
    }
