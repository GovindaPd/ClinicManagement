from .models import Notification, SeenNotification
from django.db.models import Exists, OuterRef

def notification_context(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(
            receiver=request.user
        ).exclude(
            seen_notes__seen_by=request.user
        ).count()
    else:
        unread = 0
    return {"unread_notifications": unread}