#apps/finance/models.py
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class RecordType(models.TextChoices):
    INCOME  = "income",  "Income"
    EXPENSE = "expense", "Expense"

class ActiveManager(models.Manager):
    """Custom manager that excludes soft-deleted records by default."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class FinancialRecord(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount     = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.01)])
    type       = models.CharField(max_length=10, choices=RecordType.choices)
    category   = models.CharField(max_length=100)
    date       = models.DateField()
    notes      = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="records",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()
    class Meta:
        db_table = "financial_records"
        ordering  = ["-date", "-created_at"]
        indexes   = [
            models.Index(fields=["date"]),
            models.Index(fields=["type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_deleted"]),
        ]

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])