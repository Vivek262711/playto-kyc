"""
Seed script — creates test data for development.

Creates:
- 2 merchants: one with a draft submission, one with an under_review submission
- 1 reviewer
- Sample documents and notifications

Usage:
    python manage.py shell < seed.py
    OR
    python seed.py  (with Django settings configured)
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from users.models import User
from kyc.models import KYCSubmission, Document
from notifications.models import Notification
from rest_framework.authtoken.models import Token


def seed():
    print("🌱 Seeding database...")

    # ------------------------------------------------------------------
    # Clear existing seed data (idempotent)
    # ------------------------------------------------------------------
    User.objects.filter(email__in=[
        'merchant1@example.com',
        'merchant2@example.com',
        'reviewer@example.com',
    ]).delete()

    # ------------------------------------------------------------------
    # Create Users
    # ------------------------------------------------------------------
    merchant1 = User.objects.create_user(
        username='merchant1@example.com',
        email='merchant1@example.com',
        password='merchant123',
        name='Raj Sharma',
        role='merchant',
    )
    token1, _ = Token.objects.get_or_create(user=merchant1)
    print(f"  ✅ Merchant 1: {merchant1.email} (token: {token1.key})")

    merchant2 = User.objects.create_user(
        username='merchant2@example.com',
        email='merchant2@example.com',
        password='merchant123',
        name='Priya Patel',
        role='merchant',
    )
    token2, _ = Token.objects.get_or_create(user=merchant2)
    print(f"  ✅ Merchant 2: {merchant2.email} (token: {token2.key})")

    reviewer = User.objects.create_user(
        username='reviewer@example.com',
        email='reviewer@example.com',
        password='reviewer123',
        name='Amit Verma',
        role='reviewer',
    )
    token3, _ = Token.objects.get_or_create(user=reviewer)
    print(f"  ✅ Reviewer:   {reviewer.email} (token: {token3.key})")

    # ------------------------------------------------------------------
    # Create KYC Submissions
    # ------------------------------------------------------------------

    # Merchant 1 — Draft submission
    submission1 = KYCSubmission.objects.create(
        merchant=merchant1,
        personal_details={
            'full_name': 'Raj Sharma',
            'dob': '1990-05-15',
            'address': '123 MG Road, Mumbai',
            'phone': '+91-9876543210',
        },
        business_details={
            'business_name': 'Sharma Enterprises',
            'business_type': 'Sole Proprietorship',
            'gstin': '27AAPFU0939F1ZV',
            'registered_address': '456 Commercial St, Mumbai',
        },
        status='draft',
    )
    print(f"  ✅ Submission #{submission1.id}: draft (Merchant 1)")

    # Merchant 2 — Under review submission (submitted 26 hours ago → at_risk)
    submission2 = KYCSubmission.objects.create(
        merchant=merchant2,
        personal_details={
            'full_name': 'Priya Patel',
            'dob': '1988-11-22',
            'address': '789 Nehru Nagar, Delhi',
            'phone': '+91-9123456789',
        },
        business_details={
            'business_name': 'Patel Trading Co.',
            'business_type': 'Partnership',
            'gstin': '07AABCT1332L1ZN',
            'registered_address': '101 Trade Center, Delhi',
        },
        status='under_review',
    )
    # Backdate to make it at_risk (26 hours ago)
    KYCSubmission.objects.filter(id=submission2.id).update(
        updated_at=timezone.now() - timedelta(hours=26)
    )
    submission2.refresh_from_db()
    print(f"  ✅ Submission #{submission2.id}: under_review (Merchant 2, at_risk=True)")

    # ------------------------------------------------------------------
    # Create Notifications
    # ------------------------------------------------------------------
    Notification.objects.create(
        merchant=merchant2,
        event_type='submitted',
        payload={
            'submission_id': submission2.id,
            'message': f'KYC submission #{submission2.id} has been submitted for review.',
        },
    )
    print(f"  ✅ Notification: submitted event for Merchant 2")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n🎉 Seed complete!")
    print(f"\n📋 Login credentials:")
    print(f"   Merchant 1: merchant1@example.com / merchant123")
    print(f"   Merchant 2: merchant2@example.com / merchant123")
    print(f"   Reviewer:   reviewer@example.com  / reviewer123")


if __name__ == '__main__':
    seed()
else:
    seed()
