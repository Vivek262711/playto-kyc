"""Notification views — merchant can view their own notifications."""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.permissions import IsMerchant
from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsMerchant])
def notification_list(request):
    """List notifications for the authenticated merchant."""
    notifications = Notification.objects.filter(merchant=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)
