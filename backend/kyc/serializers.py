"""
KYC serializers for submissions and documents.
"""
from rest_framework import serializers
from .models import KYCSubmission, Document
from users.serializers import UserSerializer


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    class Meta:
        model = Document
        fields = ['id', 'submission', 'file', 'type', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload — validates type field."""
    file = serializers.FileField()
    type = serializers.ChoiceField(choices=['PAN', 'Aadhaar', 'Bank'])


class KYCSubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing submissions."""
    merchant_name = serializers.CharField(source='merchant.name', read_only=True)
    document_count = serializers.IntegerField(
        source='documents.count', read_only=True
    )

    class Meta:
        model = KYCSubmission
        fields = [
            'id', 'merchant', 'merchant_name', 'status',
            'document_count', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class KYCSubmissionDetailSerializer(serializers.ModelSerializer):
    """Full serializer for submission detail views."""
    merchant_info = UserSerializer(source='merchant', read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = KYCSubmission
        fields = [
            'id', 'merchant', 'merchant_info', 'personal_details',
            'business_details', 'status', 'documents',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'merchant', 'status', 'created_at', 'updated_at']


class KYCSubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating a draft submission."""
    class Meta:
        model = KYCSubmission
        fields = ['id', 'personal_details', 'business_details', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class ReviewerActionSerializer(serializers.Serializer):
    """Serializer for reviewer actions (reject / request-info) that require a reason."""
    reason = serializers.CharField(required=False, default='', allow_blank=True)
