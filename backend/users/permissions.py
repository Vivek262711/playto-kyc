"""
Custom permission classes for role-based authorization.
"""
from rest_framework.permissions import BasePermission


class IsMerchant(BasePermission):
    """Allow access only to users with role='merchant'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'merchant'
        )


class IsReviewer(BasePermission):
    """Allow access only to users with role='reviewer'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'reviewer'
        )
