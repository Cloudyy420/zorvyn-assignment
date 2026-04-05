from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.users.models import CustomUser, Role
from apps.finance.models import FinancialRecord


class Command(BaseCommand):
    help = "Seed database with test users and transactions"

    def handle(self, *args, **options):
        # Clear existing data
        FinancialRecord.objects.all().delete()
        CustomUser.objects.filter(email__in=[
            'viewer@test.com', 'analyst@test.com', 'admin@test.com'
        ]).delete()

        # Create users
        viewer = CustomUser.objects.create_user(
            email='viewer@test.com',
            password='viewer123',
            first_name='View',
            last_name='Only',
            role=Role.VIEWER,
            is_active=True
        )

        analyst = CustomUser.objects.create_user(
            email='analyst@test.com',
            password='analyst123',
            first_name='Ana',
            last_name='Lyst',
            role=Role.ANALYST,
            is_active=True
        )

        admin = CustomUser.objects.create_user(
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role=Role.ADMIN,
            is_active=True
        )

        # Create transactions for analyst
        today = timezone.now().date()
        transactions = [
            {
                'amount': Decimal('2500.00'),
                'type': 'income',
                'category': 'Salary',
                'date': today,
                'notes': 'Monthly salary',
                'created_by': analyst,
            },
            {
                'amount': Decimal('45.50'),
                'type': 'expense',
                'category': 'Groceries',
                'date': today - timedelta(days=1),
                'notes': 'Weekly groceries',
                'created_by': analyst,
            },
            {
                'amount': Decimal('20.00'),
                'type': 'expense',
                'category': 'Transport',
                'date': today - timedelta(days=2),
                'notes': 'Gas',
                'created_by': analyst,
            },
            {
                'amount': Decimal('100.00'),
                'type': 'income',
                'category': 'Freelance',
                'date': today - timedelta(days=3),
                'notes': 'Side project payment',
                'created_by': analyst,
            },
            {
                'amount': Decimal('15.99'),
                'type': 'expense',
                'category': 'Entertainment',
                'date': today - timedelta(days=4),
                'notes': 'Movie ticket',
                'created_by': analyst,
            },
            {
                'amount': Decimal('55.00'),
                'type': 'expense',
                'category': 'Utilities',
                'date': today - timedelta(days=5),
                'notes': 'Internet bill',
                'created_by': analyst,
            },
        ]

        for tx in transactions:
            FinancialRecord.objects.create(**tx)

        # Create transactions for admin
        admin_transactions = [
            {
                'amount': Decimal('3500.00'),
                'type': 'income',
                'category': 'Salary',
                'date': today,
                'notes': 'Monthly salary',
                'created_by': admin,
            },
            {
                'amount': Decimal('1200.00'),
                'type': 'expense',
                'category': 'Rent',
                'date': today - timedelta(days=1),
                'notes': 'Rent payment',
                'created_by': admin,
            },
        ]

        for tx in admin_transactions:
            FinancialRecord.objects.create(**tx)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
        self.stdout.write(f'Created 3 users and 8 transactions')
        self.stdout.write('\nTest credentials:')
        self.stdout.write('  Viewer: viewer@test.com / viewer123')
        self.stdout.write('  Analyst: analyst@test.com / analyst123')
        self.stdout.write('  Admin: admin@test.com / admin123')
