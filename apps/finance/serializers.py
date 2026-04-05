from django.utils import timezone
from rest_framework import serializers
from .models import FinancialRecord

class FinancialRecordSerializer(serializers.ModelSerializer):
    created_by_email = serializers.ReadOnlyField(source='created_by.email')
    updated_by_email = serializers.ReadOnlyField(source='updated_by.email', default=None)

    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'amount', 'type', 'category', 'date', 'notes',
            'created_by', 'created_by_email', 'updated_by', 'updated_by_email',
            'created_at', 'updated_at', 'is_deleted'
        ]
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_deleted'
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value