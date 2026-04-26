"""
Merchant-facing KYC views.
Views are thin — all business logic is in the services layer.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.permissions import IsMerchant
from .models import KYCSubmission, Document
from .serializers import (
    KYCSubmissionListSerializer,
    KYCSubmissionDetailSerializer,
    KYCSubmissionCreateSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
)
from .services.state_machine import KYCStateMachine, InvalidTransitionError
from .services.file_validator import FileValidator, FileValidationError
from .services.sla_calculator import SLACalculator
from .services.notification_service import NotificationService


def _get_merchant_submission(user, submission_id):
    """Helper: get submission owned by the requesting merchant."""
    try:
        return KYCSubmission.objects.get(id=submission_id, merchant=user)
    except KYCSubmission.DoesNotExist:
        return None


# ---------------------------------------------------------------------------
# Submission CRUD
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsMerchant])
def submission_list_create(request):
    """
    GET  — List merchant's own submissions (with SLA info).
    POST — Create a new draft submission.
    """
    if request.method == 'GET':
        submissions = KYCSubmission.objects.filter(
            merchant=request.user
        ).order_by('-created_at')

        serializer = KYCSubmissionListSerializer(submissions, many=True)
        data = serializer.data

        # Enrich with SLA data
        for i, submission in enumerate(submissions):
            data[i] = SLACalculator.enrich_submission_data(data[i], submission)

        return Response(data)

    # POST — create draft
    serializer = KYCSubmissionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        errors = []
        for field, msgs in serializer.errors.items():
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        return Response(
            {'error': '; '.join(errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    submission = serializer.save(merchant=request.user, status='draft')
    return Response(
        KYCSubmissionDetailSerializer(submission).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'PUT'])
@permission_classes([IsMerchant])
def submission_detail_update(request, submission_id):
    """
    GET — View own submission detail.
    PUT — Update a draft submission.
    """
    submission = _get_merchant_submission(request.user, submission_id)
    if not submission:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        data = KYCSubmissionDetailSerializer(submission).data
        data = SLACalculator.enrich_submission_data(data, submission)
        return Response(data)

    # PUT — only drafts can be updated
    if submission.status != 'draft':
        return Response(
            {'error': 'Only draft submissions can be edited.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = KYCSubmissionCreateSerializer(
        submission, data=request.data, partial=True
    )
    if not serializer.is_valid():
        errors = []
        for field, msgs in serializer.errors.items():
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        return Response(
            {'error': '; '.join(errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()
    return Response(KYCSubmissionDetailSerializer(submission).data)


# ---------------------------------------------------------------------------
# State transitions (merchant side)
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsMerchant])
def submit_submission(request, submission_id):
    """Transition: draft → submitted."""
    submission = _get_merchant_submission(request.user, submission_id)
    if not submission:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        KYCStateMachine.transition(submission, 'submitted')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    NotificationService.log_submission(submission)
    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)


@api_view(['POST'])
@permission_classes([IsMerchant])
def resubmit_submission(request, submission_id):
    """Transition: more_info_requested → submitted."""
    submission = _get_merchant_submission(request.user, submission_id)
    if not submission:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Guard: resubmit is ONLY valid from more_info_requested
    if submission.status != 'more_info_requested':
        return Response(
            {'error': f"Cannot resubmit: submission is in '{submission.status}' state. "
                      f"Resubmit is only allowed from 'more_info_requested'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        KYCStateMachine.transition(submission, 'submitted')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    NotificationService.log_submission(submission)
    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)


# ---------------------------------------------------------------------------
# Document upload
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsMerchant])
def document_list_upload(request, submission_id):
    """
    GET  — List documents for a submission.
    POST — Upload a document (with file validation).
    """
    submission = _get_merchant_submission(request.user, submission_id)
    if not submission:
        return Response(
            {'error': 'Submission not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        documents = Document.objects.filter(submission=submission)
        return Response(DocumentSerializer(documents, many=True).data)

    # POST — upload document
    serializer = DocumentUploadSerializer(data=request.data)
    if not serializer.is_valid():
        errors = []
        for field, msgs in serializer.errors.items():
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        return Response(
            {'error': '; '.join(errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    uploaded_file = serializer.validated_data['file']

    # Validate file
    try:
        FileValidator.validate(uploaded_file)
    except FileValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    document = Document.objects.create(
        submission=submission,
        file=uploaded_file,
        type=serializer.validated_data['type'],
    )
    return Response(
        DocumentSerializer(document).data,
        status=status.HTTP_201_CREATED,
    )
