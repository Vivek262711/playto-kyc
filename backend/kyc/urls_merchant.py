"""Merchant KYC URL routes."""
from django.urls import path
from . import views_merchant as views

urlpatterns = [
    # Submissions
    path('submissions/', views.submission_list_create, name='merchant-submissions'),
    path('submissions/<int:submission_id>/', views.submission_detail_update, name='merchant-submission-detail'),
    # State transitions
    path('submissions/<int:submission_id>/submit/', views.submit_submission, name='merchant-submit'),
    path('submissions/<int:submission_id>/resubmit/', views.resubmit_submission, name='merchant-resubmit'),
    # Documents
    path('submissions/<int:submission_id>/documents/', views.document_list_upload, name='merchant-documents'),
]
