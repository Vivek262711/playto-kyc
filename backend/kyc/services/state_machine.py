"""
State Machine — Single source of truth for KYC submission transitions.

ALL status changes MUST go through KYCStateMachine.transition().
No other code is allowed to modify submission.status directly.
"""
from django.utils import timezone


class InvalidTransitionError(Exception):
    """Raised when a state transition is not allowed."""
    pass


class KYCStateMachine:
    """
    Strict state machine for KYC submission lifecycle.

    Allowed transitions:
        draft              → submitted
        submitted          → under_review
        under_review       → approved / rejected / more_info_requested
        more_info_requested → submitted

    Any other transition raises InvalidTransitionError.
    """

    TRANSITIONS = {
        'draft': ['submitted'],
        'submitted': ['under_review'],
        'under_review': ['approved', 'rejected', 'more_info_requested'],
        'more_info_requested': ['submitted'],
    }

    # Terminal states — no transitions allowed FROM these
    TERMINAL_STATES = {'approved', 'rejected'}

    @classmethod
    def get_allowed_transitions(cls, current_status):
        """Return list of valid next states for a given current status."""
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def can_transition(cls, current_status, new_status):
        """Check if a transition from current_status to new_status is allowed."""
        allowed = cls.get_allowed_transitions(current_status)
        return new_status in allowed

    @classmethod
    def transition(cls, submission, new_status):
        """
        Attempt to transition a submission to a new status.

        Args:
            submission: KYCSubmission instance
            new_status: Target status string

        Returns:
            The updated submission instance (already saved).

        Raises:
            InvalidTransitionError: If the transition is not allowed.
        """
        current_status = submission.status

        if not cls.can_transition(current_status, new_status):
            raise InvalidTransitionError(
                f"Cannot transition from '{current_status}' to '{new_status}'. "
                f"Allowed transitions from '{current_status}': "
                f"{cls.get_allowed_transitions(current_status) or 'none (terminal state)'}."
            )

        submission.status = new_status
        submission.updated_at = timezone.now()
        submission.save(update_fields=['status', 'updated_at'])
        return submission
