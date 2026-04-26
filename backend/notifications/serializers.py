"""Notification serializer."""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'merchant', 'event_type', 'payload', 'timestamp']
        read_only_fields = fields
