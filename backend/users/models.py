"""
User model with role-based access (merchant / reviewer).
Extends Django's AbstractUser for built-in auth support.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with role field for authorization."""

    ROLE_CHOICES = [
        ('merchant', 'Merchant'),
        ('reviewer', 'Reviewer'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Use email for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'role']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.role})"

    @property
    def is_merchant(self):
        return self.role == 'merchant'

    @property
    def is_reviewer(self):
        return self.role == 'reviewer'
