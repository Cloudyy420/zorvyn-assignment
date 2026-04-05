# Zorvyn Finance Dashboard API

A REST API for managing personal finances. Track income and expenses, filter by category or date, and get summaries—with three user roles (Viewer, Analyst, Admin) controlling what you can see and do.

---

## Setup

1. **Install & activate:**

```bash
git clone <repo-url>
cd zorvyn-assignment
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure database:**

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

3. **Initialize:**

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data  # Optional: Load test data
python manage.py runserver
```

4. **Try it:**

- Open: http://localhost:8000/api/docs/swagger/
- Or: http://localhost:8000/api/docs/redoc/

---

## Test Data

Run the seed command to create test users and transactions:

```bash
python manage.py seed_data
```

Creates:

- **viewer@test.com** (Viewer role) - Can only see dashboard summaries
- **analyst@test.com** (Analyst role) - Can create and manage own transactions
- **admin@test.com** (Admin role) - Full access to all data

All test passwords are: `viewer123`, `analyst123`, `admin123`

Sample transactions are created for both analyst and admin to explore filtering, pagination, and dashboard features.

---

## How It Works

Three user roles with different permissions:

- **Viewer**: See dashboard summaries only (totals, trends)
- **Analyst**: Create and manage own transactions, see own dashboard
- **Admin**: See and manage everything

Each transaction has: amount, type (income/expense), category, date, notes. All changes are tracked (who created it, who last edited it, when).

---

## API Endpoints

### Authentication

```bash
POST /api/token/              # Get access token
POST /api/token/refresh/      # Refresh expired token
POST /api/register/           # Create account (public)
```

### Transactions

```bash
GET    /api/transactions/                    # List (filter by type, category, date_from, date_to, min_amount, max_amount, ordering)
POST   /api/transactions/                    # Create
GET    /api/transactions/{id}/               # View one
PATCH  /api/transactions/{id}/               # Update
DELETE /api/transactions/{id}/               # Delete (soft delete)
GET    /api/transactions/dashboard/summary/  # Get totals, trends, recent activity
```

### Users (Admin only)

```bash
GET    /api/users/                   # List all users
POST   /api/users/                   # Create user
GET    /api/users/{id}/              # View user
PATCH  /api/users/{id}/              # Update user
DELETE /api/users/{id}/              # Delete (soft delete)
PATCH  /api/users/{id}/assign-role/  # Change user role
PATCH  /api/users/{id}/toggle-status/  # Activate/deactivate
```

### Example Requests

Get token:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"password"}'
```

Create transaction:

```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.50,
    "type": "expense",
    "category": "Groceries",
    "date": "2025-04-06"
  }'
```

Filter transactions:

```bash
# By type
GET /api/transactions/?type=income

# By date range
GET /api/transactions/?date_from=2025-01-01&date_to=2025-03-31

# By amount
GET /api/transactions/?min_amount=50&max_amount=500

# Sort descending by amount
GET /api/transactions/?ordering=-amount
```

---

## Error Handling

The API validates input at multiple levels:

- Amounts must be positive and at least 0.01
- Dates can't be in the future
- Transaction types must be "income" or "expense"
- All required fields must be sent

Invalid requests return 400 with field errors:

```json
{
  "status": "error",
  "message": "amount: Amount must be positive.",
  "details": { "amount": ["Amount must be positive."] }
}
```

Unauthorized access returns 403. Missing token returns 401. Not found returns 404.

---

## Key Design Decisions

- **PostgreSQL**: Required (not SQLite). Better for production, proper decimal precision
- **Soft delete**: Records stay in DB with is_deleted=True for audit trail and compliance
- **UUID primary keys**: Better privacy/security than guessable auto-increment IDs
- **Decimal amounts**: Prevents floating-point rounding errors with money
- **Data isolation**: Analysts only see their own records; admins see all
- **Pagination**: 20 items per page to handle large datasets efficiently
- **Read-only fields**: id, created_by, created_at, updated_at, is_deleted are system-managed

---

## Testing

**Use Swagger UI:**

1. Go to http://localhost:8000/api/docs/swagger/
2. Click "Authorize", get token from /api/token/
3. Try endpoints directly

**Run tests:**

```bash
python manage.py test
```

Expected: 10 passing tests

---

## Project Structure

```
zorvyn-assignment/
├── apps/
│   ├── users/              # User auth, roles, management
│   │   ├── models.py       # CustomUser with soft delete
│   │   ├── views.py        # Register, admin endpoints
│   │   └── serializers.py  # Validation
│   └── finance/            # Financial records
│       ├── models.py       # FinancialRecord, soft delete
│       ├── views.py        # CRUD, dashboard
│       ├── services.py     # Aggregations
│       ├── filters.py      # Advanced queries
│       └── tests.py
├── core/
│   ├── permissions.py      # Role-based access control
│   ├── responses.py        # Consistent API responses
│   └── custom_exception_handler.py  # Error handling
└── zorvyn_assignment/
    ├── settings.py         # Django config
    └── urls.py             # Routes
```

---

## Troubleshooting

**Database connection refused:**

- Check PostgreSQL is running
- Verify .env has correct credentials
- Create the database: psql -U postgres -c "CREATE DATABASE zorvyn-db;"

**No module named 'apps':**

- Make sure you're in zorvyn-assignment/ directory
- Run: python manage.py check

**Token expired:**

- Get new token from /api/token/
- Or refresh: POST /api/token/refresh/

**Permission denied on create:**

- Your role must be Analyst or Admin
- Ask an admin to upgrade your role

---

## Architecture & Key Patterns

**Models:**

- CustomUser: Email login, UUID PK, soft delete (is_deleted flag), role-based (Viewer/Analyst/Admin)
- FinancialRecord: Amount as Decimal (precision), type/category/date fields, tracks created_by/updated_by with timestamps

**Permission System:**

- View-level: IsAnalystOrAbove for listing, IsAdmin for user management
- Object-level: CanModifyRecord prevents users from editing others' transactions
- Queryset-level: Analysts see only their own data, admins see all

**Data Handling:**

- Soft delete: Records marked is_deleted=True stay in DB (audit trail)
- UUID primary keys: Non-guessable IDs for security
- Decimal amounts: Prevents floating-point rounding errors with money
- Pagination: 20 items per page by default

**Validation:**

- Serializer layer: Catches invalid input (positive amount, future dates)
- Model layer: Database constraints as backup
- Permission layer: Role checks before data access
- Response formatter: APIResponse ensures consistent error/success responses
