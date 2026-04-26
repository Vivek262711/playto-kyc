"""
User serializers for registration and login.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role']

    def validate_role(self, value):
        if value not in ('merchant', 'reviewer'):
            raise serializers.ValidationError("Role must be 'merchant' or 'reviewer'.")
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['email'],  # Use email as username
            name=validated_data['name'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login — returns token."""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Read-only user info serializer."""
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role']
