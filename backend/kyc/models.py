"""
KYC models — KYCSubmission and Document.
Status field is controlled EXCLUSIVELY by the state machine service.
"""
from django.conf import settings
from django.db import models


class KYCSubmission(models.Model):
    """Represents a merchant's KYC submission lifecycle."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info_requested', 'More Info Requested'),
    ]

    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kyc_submissions',
        limit_choices_to={'role': 'merchant'},
    )
    personal_details = models.JSONField(default=dict, blank=True)
    business_details = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='draft',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kyc_submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"KYC#{self.id} — {self.merchant.name} ({self.status})"


class Document(models.Model):
    """File attachment linked to a KYC submission."""

    TYPE_CHOICES = [
        ('PAN', 'PAN Card'),
        ('Aadhaar', 'Aadhaar Card'),
        ('Bank', 'Bank Statement'),
    ]

    submission = models.ForeignKey(
        KYCSubmission,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return f"{self.type} — Submission#{self.submission_id}"
