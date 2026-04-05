# apps/finance/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from apps.users.models import Role
from core.permissions import IsAnalystOrAbove, CanModifyRecord, IsAdmin
from core.pagination import StandardResultsPagination
from core.responses import APIResponse
from .models import FinancialRecord
from .serializers import FinancialRecordSerializer
from .filters import FinancialRecordFilter
from .services import DashboardService

class FinancialRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRecordSerializer
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = FinancialRecordFilter
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    @property
    def queryset(self):
        """Return queryset. Skip auth check during schema generation."""
        if getattr(self, "swagger_fake_view", False):
            return FinancialRecord.objects.none()
        return FinancialRecord.objects.select_related("created_by")

    @extend_schema(
        summary="List transactions",
        description="List all financial records (transactions) with optional filtering and sorting. Analysts see only their own records. Admins see all records.",
        tags=["transactions"],
        parameters=[
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by transaction type: "income" or "expense"',
                required=False,
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category name (e.g., "Salary", "Groceries")',
                required=False,
            ),
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter transactions from this date (YYYY-MM-DD)',
                required=False,
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter transactions until this date (YYYY-MM-DD)',
                required=False,
            ),
            OpenApiParameter(
                name='min_amount',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Filter transactions with amount >= this value',
                required=False,
            ),
            OpenApiParameter(
                name='max_amount',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Filter transactions with amount <= this value',
                required=False,
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Sort by field: date, amount, created_at. Use "-" prefix for descending (e.g., "-date")',
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List financial records (transactions).
        
        **Filters:**
        - type: "income" or "expense"
        - category: category name
        - date_from, date_to: date range
        - min_amount, max_amount: amount range
        - ordering: sort by field
        
        **Note:** Analysts see only their own records. Admins see all records.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new transaction",
        description="Create a new financial record (income or expense). Analyst and above can create. You are automatically set as the creator.",
        tags=["transactions"],
    )
    def create(self, request, *args, **kwargs):
        """Create a new transaction (analyst+ only)."""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a transaction",
        description="Get details of a specific transaction. Analysts see only their own. Admins see all.",
        tags=["transactions"],
    )
    def retrieve(self, request, *args, **kwargs):
        """Get transaction details (analyst+ only, own records only unless admin)."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a transaction",
        description="Update a financial record. Can only update your own records unless you're an admin.",
        tags=["transactions"],
    )
    def update(self, request, *args, **kwargs):
        """Update transaction (analyst+ only, own records only unless admin)."""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a transaction",
        description="Partially update a financial record (update some fields). Can only modify your own records unless admin.",
        tags=["transactions"],
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update transaction (analyst+ only, own records only unless admin)."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a transaction (soft delete)",
        description="Delete a financial record. This is a soft delete—the record is marked as deleted but stays in system for audit. Can only delete your own records unless admin.",
        tags=["transactions"],
    )
    def destroy(self, request, *args, **kwargs):
        """Delete transaction with soft delete (analyst+ only, own records only unless admin)."""
        return super().destroy(request, *args, **kwargs)
        """Filter queryset by user role and action."""
        user = self.request.user
        qs = super().get_queryset()  # Uses the queryset property
        # Only filter for list/retrieve; other actions use raw queryset
        if self.action in ["list", "retrieve"]:
            if user.role == Role.ADMIN:
                return qs
            return qs.filter(created_by=user)
        return qs
    
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated(), IsAnalystOrAbove()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), CanModifyRecord()]
        if self.action == "dashboard_summary":
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @extend_schema(
        summary="Get dashboard summary",
        description="Get aggregated financial summary with totals, by category, recent activity, and monthly trends. Data is filtered by user role: viewers see aggregates only, analysts see their own, admins see all.",
        tags=["transactions"],
        responses={
            200: {
                'description': 'Dashboard summary data',
                'examples': {
                    'application/json': {
                        'success': True,
                        'message': 'Dashboard summary retrieved successfully',
                        'data': {
                            'total_income': '5000.00',
                            'total_expense': '1200.50',
                            'net_balance': '3799.50',
                            'category_totals': {
                                'Salary': '5000.00',
                                'Groceries': '500.00'
                            },
                            'recent_activity': [],
                            'monthly_trends': []
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=["get"], url_path="dashboard/summary")
    def dashboard_summary(self, request):
        """Return aggregated dashboard data respecting user's role."""
        service = DashboardService(request.user)
        data = service.get_summary()
        return APIResponse.success(
            data=data,
            message="Dashboard summary retrieved successfully"
        )