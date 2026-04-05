from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import CustomUser, Role
from .serializers import UserSerializer, UserUpdateSerializer, UserDetailSerializer
from core.permissions import IsAdmin
from core.responses import APIResponse


class RegisterView(generics.CreateAPIView):
    """Public endpoint to create a new user (default role: VIEWER)."""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Public endpoint to create a new user account. New users are assigned the VIEWER role by default.",
        tags=["authentication"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return APIResponse.created({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        }, message="User registered successfully")


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only endpoint to manage users: list, retrieve, update, delete (soft delete)."""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    ordering_fields = ['date_joined', 'email']
    ordering = ['-date_joined']

    @property
    def queryset(self):
        """Return queryset. Skip auth check during schema generation."""
        if getattr(self, "swagger_fake_view", False):
            return CustomUser.objects.none()
        return CustomUser.objects.all()

    @extend_schema(
        summary="List all users",
        description="Admin-only endpoint to list all users in the system.",
        tags=["users"],
    )
    def list(self, request, *args, **kwargs):
        """List all users (admin only)."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new user",
        description="Admin endpoint to create a new user. Use /api/register/ for public user registration.",
        tags=["users"],
    )
    def create(self, request, *args, **kwargs):
        """Create a new user (admin only)."""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve user details",
        description="Get details of a specific user (admin only).",
        tags=["users"],
    )
    def retrieve(self, request, *args, **kwargs):
        """Get user details (admin only)."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update user (admin only)",
        description="Update user profile information. Cannot change role or status here—use assign-role and toggle-status actions instead.",
        tags=["users"],
    )
    def update(self, request, *args, **kwargs):
        """Update user (admin only)."""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update user (admin only)",
        description="Partially update user profile information.",
        tags=["users"],
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update user (admin only)."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete user (soft delete)",
        description="Delete a user. This is a soft delete—the user is marked as deleted but data is preserved for audit.",
        tags=["users"],
    )
    def destroy(self, request, *args, **kwargs):
        """Delete user with soft delete (admin only)."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserDetailSerializer
        return UserDetailSerializer

    def perform_destroy(self, instance):
        """Soft delete the user instead of hard delete."""
        instance.soft_delete()

    @extend_schema(
        summary="Assign role to user",
        description="Change a user's role (VIEWER, ANALYST, or ADMIN). Admin-only action. Send JSON: {\"role\": \"analyst\"}",
        tags=["users"],
    )
    @action(detail=True, methods=['patch'], url_path='assign-role')
    def assign_role(self, request, pk=None):
        """Admin-only action to assign a role to a user."""
        user = self.get_object()
        role = request.data.get('role')
        if role not in [choice[0] for choice in Role.choices]:
            return APIResponse.validation_error(
                message="Invalid role provided",
                details={'valid_roles': [choice[0] for choice in Role.choices]}
            )
        user.role = role
        user.save(update_fields=['role', 'updated_at'])
        return APIResponse.success(
            data={'role': user.role},
            message=f"Role assigned: {role}"
        )

    @extend_schema(
        summary="Toggle user active status",
        description="Activate or deactivate a user account. Admin-only action.",
        tags=["users"],
    )
    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        """Admin-only action to activate/deactivate a user."""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=['is_active', 'updated_at'])
        return APIResponse.success(
            data={'is_active': user.is_active, 'status': 'active' if user.is_active else 'inactive'},
            message=f"User {user.email} is now {('active' if user.is_active else 'inactive')}"
        )