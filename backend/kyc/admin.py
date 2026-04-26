from django.contrib import admin
from .models import KYCSubmission, Document


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'merchant', 'status', 'created_at', 'updated_at']
    list_filter = ['status']
    search_fields = ['merchant__name', 'merchant__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission', 'type', 'uploaded_at']
    list_filter = ['type']
