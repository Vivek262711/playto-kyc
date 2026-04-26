"""
Auth views — register and login.
Views are thin; validation lives in serializers.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user and return auth token."""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        # Errors are flattened by custom exception handler if raised,
        # but for serializer errors we format manually for consistency.
        errors = []
        for field, msgs in serializer.errors.items():
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        return Response(
            {'error': '; '.join(errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login and return auth token."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.validated_data['user']
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['GET'])
def me_view(request):
    """Return the currently authenticated user's info."""
    return Response(UserSerializer(request.user).data)
