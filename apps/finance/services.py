from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import FinancialRecord

class DashboardService:
    def __init__(self, user):
        self.user = user

    def get_queryset(self):
        """Return base queryset respecting user role (admin sees all)."""
        qs = FinancialRecord.objects.all()
        if self.user.role != "admin":
            qs = qs.filter(created_by=self.user)
        return qs

    def get_summary(self):
        qs = self.get_queryset()

        # Totals
        income = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        net = income - expense

        # Category totals (all categories, sorted descending)
        category_totals = {}
        cats = qs.values('category').annotate(total=Sum('amount')).order_by('-total')
        for cat in cats:
            category_totals[cat['category']] = float(cat['total'])

        # Recent activity (last 5 transactions)
        recent = list(qs.order_by('-date', '-created_at')[:5].values(
            'date', 'amount', 'type', 'category', 'notes'
        ))

        # Monthly trends (last 6 months)
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)
        monthly_qs = qs.filter(date__gte=six_months_ago)
        monthly_data = (
            monthly_qs.values('date__year', 'date__month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('date__year', 'date__month')
        )
        trends = {}
        for entry in monthly_data:
            key = f"{entry['date__year']}-{entry['date__month']:02d}"
            if key not in trends:
                trends[key] = {'income': 0, 'expense': 0}
            ttype = 'income' if entry['type'] == 'income' else 'expense'
            trends[key][ttype] = float(entry['total'])

        return {
            'total_income': float(income),
            'total_expense': float(expense),
            'net_balance': float(net),
            'category_totals': category_totals,
            'recent_activity': recent,
            'monthly_trends': trends,
        }