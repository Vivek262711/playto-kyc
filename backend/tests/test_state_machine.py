"""
Tests for the KYC State Machine.
Verifies that:
- Valid transitions succeed.
- Invalid transitions raise InvalidTransitionError (400 in API).
- Terminal states block all transitions.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from users.models import User
from kyc.models import KYCSubmission
from kyc.services.state_machine import KYCStateMachine, InvalidTransitionError


class StateMachineUnitTest(TestCase):
    """Unit tests for KYCStateMachine — direct service-layer testing."""

    def setUp(self):
        self.merchant = User.objects.create_user(
            username='test_merchant@example.com',
            email='test_merchant@example.com',
            password='testpass123',
            name='Test Merchant',
            role='merchant',
        )
        self.submission = KYCSubmission.objects.create(
            merchant=self.merchant,
            personal_details={'full_name': 'John Doe'},
            business_details={'business_name': 'Doe Corp'},
            status='draft',
        )

    def test_valid_draft_to_submitted(self):
        """draft → submitted should succeed."""
        result = KYCStateMachine.transition(self.submission, 'submitted')
        self.assertEqual(result.status, 'submitted')

    def test_valid_submitted_to_under_review(self):
        """submitted → under_review should succeed."""
        self.submission.status = 'submitted'
        self.submission.save()
        result = KYCStateMachine.transition(self.submission, 'under_review')
        self.assertEqual(result.status, 'under_review')

    def test_valid_under_review_to_approved(self):
        """under_review → approved should succeed."""
        self.submission.status = 'under_review'
        self.submission.save()
        result = KYCStateMachine.transition(self.submission, 'approved')
        self.assertEqual(result.status, 'approved')

    def test_valid_under_review_to_rejected(self):
        """under_review → rejected should succeed."""
        self.submission.status = 'under_review'
        self.submission.save()
        result = KYCStateMachine.transition(self.submission, 'rejected')
        self.assertEqual(result.status, 'rejected')

    def test_valid_under_review_to_more_info(self):
        """under_review → more_info_requested should succeed."""
        self.submission.status = 'under_review'
        self.submission.save()
        result = KYCStateMachine.transition(self.submission, 'more_info_requested')
        self.assertEqual(result.status, 'more_info_requested')

    def test_valid_more_info_to_submitted(self):
        """more_info_requested → submitted should succeed."""
        self.submission.status = 'more_info_requested'
        self.submission.save()
        result = KYCStateMachine.transition(self.submission, 'submitted')
        self.assertEqual(result.status, 'submitted')

    # ------ INVALID TRANSITIONS ------

    def test_invalid_draft_to_approved(self):
        """draft → approved should raise InvalidTransitionError."""
        with self.assertRaises(InvalidTransitionError):
            KYCStateMachine.transition(self.submission, 'approved')

    def test_invalid_draft_to_under_review(self):
        """draft → under_review should raise InvalidTransitionError."""
        with self.assertRaises(InvalidTransitionError):
            KYCStateMachine.transition(self.submission, 'under_review')

    def test_invalid_submitted_to_approved(self):
        """submitted → approved should raise InvalidTransitionError."""
        self.submission.status = 'submitted'
        self.submission.save()
        with self.assertRaises(InvalidTransitionError):
            KYCStateMachine.transition(self.submission, 'approved')

    def test_invalid_approved_to_anything(self):
        """approved is terminal — no transitions allowed."""
        self.submission.status = 'approved'
        self.submission.save()
        with self.assertRaises(InvalidTransitionError):
            KYCStateMachine.transition(self.submission, 'submitted')

    def test_invalid_rejected_to_anything(self):
        """rejected is terminal — no transitions allowed."""
        self.submission.status = 'rejected'
        self.submission.save()
        with self.assertRaises(InvalidTransitionError):
            KYCStateMachine.transition(self.submission, 'draft')

    def test_invalid_more_info_to_approved(self):
        """more_info_requested → approved should raise InvalidTransitionError."""
        self.submission.status = 'more_info_requested'
        self.submission.save()
        with self.assertRaises(InvalidTransitionError):
            KYCStateMachine.transition(self.submission, 'approved')


class StateMachineAPITest(TestCase):
    """
    API-level test: invalid state transition returns HTTP 400
    with consistent error format {"error": "..."}.
    """

    def setUp(self):
        self.merchant = User.objects.create_user(
            username='api_merchant@example.com',
            email='api_merchant@example.com',
            password='testpass123',
            name='API Merchant',
            role='merchant',
        )
        self.token = Token.objects.create(user=self.merchant)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.submission = KYCSubmission.objects.create(
            merchant=self.merchant,
            personal_details={'full_name': 'Jane Doe'},
            business_details={'business_name': 'Jane Corp'},
            status='draft',
        )

    def test_invalid_transition_returns_400(self):
        """
        Attempting to resubmit a draft (only valid from more_info_requested)
        should return 400 with {"error": "..."}.
        """
        url = f'/api/v1/merchant/submissions/{self.submission.id}/resubmit/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        # The resubmit guard returns a descriptive error message
        self.assertIn('Cannot resubmit', response.json()['error'])

    def test_submit_draft_succeeds(self):
        """Submitting a draft should succeed and return submission data."""
        url = f'/api/v1/merchant/submissions/{self.submission.id}/submit/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'submitted')

    def test_double_submit_fails(self):
        """Submitting an already-submitted submission should return 400."""
        # First submit
        url = f'/api/v1/merchant/submissions/{self.submission.id}/submit/'
        self.client.post(url)

        # Second submit should fail
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
