from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Role

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'password', 'is_active']
        read_only_fields = ['id', 'is_active']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', Role.VIEWER)
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (no password change)."""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for admin to view and manage user details (role, status)."""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined', 'updated_at']
        read_only_fields = ['id', 'date_joined', 'updated_at']