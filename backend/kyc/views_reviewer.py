"""
Reviewer-facing KYC views.
Views are thin — all business logic is in the services layer.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.permissions import IsReviewer
from .models import KYCSubmission
from .serializers import (
    KYCSubmissionListSerializer,
    KYCSubmissionDetailSerializer,
    ReviewerActionSerializer,
)
from .services.state_machine import KYCStateMachine, InvalidTransitionError
from .services.sla_calculator import SLACalculator
from .services.queue_service import QueueService
from .services.notification_service import NotificationService


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsReviewer])
def reviewer_queue(request):
    """
    GET — Return the reviewer queue (oldest first) with statistics.
    """
    queue = QueueService.get_queue()
    stats = QueueService.get_queue_stats()

    serializer = KYCSubmissionListSerializer(queue, many=True)
    data = serializer.data

    # Enrich each item with SLA info
    for i, submission in enumerate(queue):
        data[i] = SLACalculator.enrich_submission_data(data[i], submission)

    return Response({
        'stats': stats,
        'submissions': data,
    })


# ---------------------------------------------------------------------------
# Submission detail (reviewer can view any)
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsReviewer])
def reviewer_submission_detail(request, submission_id):
    """GET — View any submission's full detail."""
    try:
        submission = KYCSubmission.objects.select_related('merchant').get(
            id=submission_id
        )
    except KYCSubmission.DoesNotExist:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    data = KYCSubmissionDetailSerializer(submission).data
    data = SLACalculator.enrich_submission_data(data, submission)
    return Response(data)


# ---------------------------------------------------------------------------
# Reviewer actions (state transitions)
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsReviewer])
def pick_submission(request, submission_id):
    """Transition: submitted → under_review."""
    try:
        submission = KYCSubmission.objects.get(id=submission_id)
    except KYCSubmission.DoesNotExist:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        KYCStateMachine.transition(submission, 'under_review')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsReviewer])
def approve_submission(request, submission_id):
    """Transition: under_review → approved."""
    try:
        submission = KYCSubmission.objects.get(id=submission_id)
    except KYCSubmission.DoesNotExist:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        KYCStateMachine.transition(submission, 'approved')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    NotificationService.log_approval(submission)
    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsReviewer])
def reject_submission(request, submission_id):
    """Transition: under_review → rejected."""
    try:
        submission = KYCSubmission.objects.get(id=submission_id)
    except KYCSubmission.DoesNotExist:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    action_serializer = ReviewerActionSerializer(data=request.data)
    action_serializer.is_valid(raise_exception=True)
    reason = action_serializer.validated_data.get('reason', '')

    try:
        KYCStateMachine.transition(submission, 'rejected')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    NotificationService.log_rejection(submission, reason=reason)
    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsReviewer])
def request_info_submission(request, submission_id):
    """Transition: under_review → more_info_requested."""
    try:
        submission = KYCSubmission.objects.get(id=submission_id)
    except KYCSubmission.DoesNotExist:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    action_serializer = ReviewerActionSerializer(data=request.data)
    action_serializer.is_valid(raise_exception=True)
    reason = action_serializer.validated_data.get('reason', '')

    try:
        KYCStateMachine.transition(submission, 'more_info_requested')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    NotificationService.log_more_info_request(submission, reason=reason)
    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)
