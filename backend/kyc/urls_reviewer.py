"""Reviewer KYC URL routes."""
from django.urls import path
from . import views_reviewer as views

urlpatterns = [
    path('queue/', views.reviewer_queue, name='reviewer-queue'),
    path('submissions/<int:submission_id>/', views.reviewer_submission_detail, name='reviewer-submission-detail'),
    path('submissions/<int:submission_id>/pick/', views.pick_submission, name='reviewer-pick'),
    path('submissions/<int:submission_id>/approve/', views.approve_submission, name='reviewer-approve'),
    path('submissions/<int:submission_id>/reject/', views.reject_submission, name='reviewer-reject'),
    path('submissions/<int:submission_id>/request-info/', views.request_info_submission, name='reviewer-request-info'),
]
