"""
Notification Service — logs events for KYC lifecycle transitions.
"""
from notifications.models import Notification


class NotificationService:
    """
    Creates notification records for KYC events.
    Append-only event log — no updates or deletes.
    """

    @classmethod
    def log_event(cls, merchant_id, event_type, payload=None):
        """
        Log a KYC lifecycle event.

        Args:
            merchant_id: ID of the merchant user.
            event_type: One of 'submitted', 'approved', 'rejected', 'more_info_requested'.
            payload: Optional dict with additional event context.

        Returns:
            Notification instance.
        """
        return Notification.objects.create(
            merchant_id=merchant_id,
            event_type=event_type,
            payload=payload or {},
        )

    @classmethod
    def log_submission(cls, submission):
        """Log a submission event."""
        return cls.log_event(
            merchant_id=submission.merchant_id,
            event_type='submitted',
            payload={
                'submission_id': submission.id,
                'message': f'KYC submission #{submission.id} has been submitted for review.',
            },
        )

    @classmethod
    def log_approval(cls, submission):
        """Log an approval event."""
        return cls.log_event(
            merchant_id=submission.merchant_id,
            event_type='approved',
            payload={
                'submission_id': submission.id,
                'message': f'KYC submission #{submission.id} has been approved.',
            },
        )

    @classmethod
    def log_rejection(cls, submission, reason=''):
        """Log a rejection event."""
        return cls.log_event(
            merchant_id=submission.merchant_id,
            event_type='rejected',
            payload={
                'submission_id': submission.id,
                'reason': reason,
                'message': f'KYC submission #{submission.id} has been rejected.',
            },
        )

    @classmethod
    def log_more_info_request(cls, submission, reason=''):
        """Log a more-info-requested event."""
        return cls.log_event(
            merchant_id=submission.merchant_id,
            event_type='more_info_requested',
            payload={
                'submission_id': submission.id,
                'reason': reason,
                'message': f'More information requested for KYC submission #{submission.id}.',
            },
        )
