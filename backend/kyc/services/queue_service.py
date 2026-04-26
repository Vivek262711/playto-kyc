"""
Queue Service — reviewer queue logic with statistics.
"""
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Now
from django.utils import timezone
from datetime import timedelta

from kyc.models import KYCSubmission


class QueueService:
    """Provides reviewer queue data and statistics."""

    @classmethod
    def get_queue(cls):
        """
        Get the reviewer queue — submissions waiting for review.
        Sorted by oldest first (FIFO).

        Returns:
            QuerySet of KYCSubmission objects with status='submitted'.
        """
        return KYCSubmission.objects.filter(
            status='submitted'
        ).select_related('merchant').order_by('updated_at')

    @classmethod
    def get_queue_stats(cls):
        """
        Compute queue statistics:
        - queue_count: number of submissions waiting for review
        - avg_time_in_queue_hours: average wait time in hours
        - approval_rate_7d: approval rate over last 7 days (percentage)

        Returns:
            dict with queue statistics.
        """
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)

        # Queue count
        queue = cls.get_queue()
        queue_count = queue.count()

        # Average time in queue (for submissions currently in queue)
        avg_time_hours = 0.0
        if queue_count > 0:
            total_seconds = sum(
                (now - sub.updated_at).total_seconds()
                for sub in queue
            )
            avg_time_hours = round((total_seconds / queue_count) / 3600, 2)

        # Approval rate in last 7 days
        resolved_last_7d = KYCSubmission.objects.filter(
            status__in=['approved', 'rejected'],
            updated_at__gte=seven_days_ago,
        )
        total_resolved = resolved_last_7d.count()
        approved_count = resolved_last_7d.filter(status='approved').count()

        if total_resolved > 0:
            approval_rate = round((approved_count / total_resolved) * 100, 1)
        else:
            approval_rate = 0.0

        return {
            'queue_count': queue_count,
            'avg_time_in_queue_hours': avg_time_hours,
            'approval_rate_7d': approval_rate,
            'total_resolved_7d': total_resolved,
        }
