"""
SLA Calculator — computes SLA risk dynamically.
NEVER stores at_risk in the database.
"""
from django.utils import timezone
from datetime import timedelta

# Submissions pending longer than this are considered at-risk
SLA_THRESHOLD = timedelta(hours=24)


class SLACalculator:
    """Computes SLA risk status for KYC submissions dynamically."""

    @classmethod
    def is_at_risk(cls, submission):
        """
        Determine if a submission is at SLA risk.

        A submission is at-risk if it has been in 'submitted' or 'under_review'
        status for longer than 24 hours.

        Args:
            submission: KYCSubmission instance.

        Returns:
            bool: True if at-risk, False otherwise.
        """
        if submission.status not in ('submitted', 'under_review'):
            return False

        time_in_status = timezone.now() - submission.updated_at
        return time_in_status > SLA_THRESHOLD

    @classmethod
    def time_in_queue(cls, submission):
        """
        Calculate how long a submission has been in its current status.

        Returns:
            timedelta: Duration in current status.
        """
        return timezone.now() - submission.updated_at

    @classmethod
    def time_in_queue_seconds(cls, submission):
        """Return time in queue as total seconds (for API responses)."""
        return cls.time_in_queue(submission).total_seconds()

    @classmethod
    def enrich_submission_data(cls, submission_data, submission):
        """
        Add SLA fields to a serialized submission dict.

        Args:
            submission_data: dict — serialized submission data.
            submission: KYCSubmission instance.

        Returns:
            dict: Enriched data with 'at_risk' and 'time_in_queue_hours'.
        """
        submission_data['at_risk'] = cls.is_at_risk(submission)
        seconds = cls.time_in_queue_seconds(submission)
        submission_data['time_in_queue_hours'] = round(seconds / 3600, 2)
        return submission_data
