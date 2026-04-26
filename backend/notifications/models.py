"""
Notification model — append-only event log for KYC lifecycle events.
"""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Immutable event log entry for KYC lifecycle events."""

    EVENT_TYPE_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info_requested', 'More Info Requested'),
    ]

    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        limit_choices_to={'role': 'merchant'},
    )
    event_type = models.CharField(max_length=25, choices=EVENT_TYPE_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} — Merchant#{self.merchant_id} @ {self.timestamp}"
