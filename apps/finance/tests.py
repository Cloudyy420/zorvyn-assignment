from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import FinancialRecord

User = get_user_model()

class TestRolePermissions(APITestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(email='viewer@test.com', password='test', first_name='Viewer', last_name='User', role='viewer')
        self.analyst = User.objects.create_user(email='analyst@test.com', password='test', first_name='Analyst', last_name='User', role='analyst')
        self.admin = User.objects.create_user(email='admin@test.com', password='test', first_name='Admin', last_name='User', role='admin', is_staff=True)

    def test_viewer_cannot_list_transactions(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 403)

    def test_analyst_can_create_transaction(self):
        self.client.force_authenticate(user=self.analyst)
        response = self.client.post('/api/transactions/', {
            'amount': 100, 'type': 'income', 'category': 'Test', 'date': '2025-04-06'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FinancialRecord.objects.count(), 1)

    def test_analyst_cannot_see_others_transactions(self):
        FinancialRecord.objects.create(amount=500, type='expense', category='Test', date='2025-04-06', created_by=self.admin)
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/transactions/')
        self.assertEqual(len(response.data['results']), 0)

    def test_dashboard_allows_viewer(self):
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get('/api/transactions/dashboard/summary/')
        self.assertEqual(response.status_code, 200)

    def test_admin_can_see_all_transactions(self):
        FinancialRecord.objects.create(amount=100, type='income', category='Test', date='2025-04-06', created_by=self.viewer)
        FinancialRecord.objects.create(amount=200, type='expense', category='Test', date='2025-04-06', created_by=self.analyst)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_analyst_can_update_own_transaction(self):
        self.client.force_authenticate(user=self.analyst)
        post_resp = self.client.post('/api/transactions/', {
            'amount': 100, 'type': 'income', 'category': 'Test', 'date': '2025-04-06'
        })
        transaction_id = post_resp.data['id']
        update_resp = self.client.patch(f'/api/transactions/{transaction_id}/', {'amount': 200})
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.data['amount'], '200.00')

    def test_analyst_cannot_update_others_transaction(self):
        other_trans = FinancialRecord.objects.create(amount=500, type='expense', category='Test', date='2025-04-06', created_by=self.admin)
        self.client.force_authenticate(user=self.analyst)
        response = self.client.patch(f'/api/transactions/{other_trans.id}/', {'amount': 999})
        self.assertEqual(response.status_code, 403)

    def test_soft_delete_removes_from_list(self):
        self.client.force_authenticate(user=self.analyst)
        post_resp = self.client.post('/api/transactions/', {
            'amount': 100, 'type': 'income', 'category': 'Test', 'date': '2025-04-06'
        })
        trans_id = post_resp.data['id']
        del_resp = self.client.delete(f'/api/transactions/{trans_id}/')
        self.assertEqual(del_resp.status_code, 204)
        list_resp = self.client.get('/api/transactions/')
        self.assertEqual(len(list_resp.data['results']), 0)

    def test_negative_amount_rejected(self):
        self.client.force_authenticate(user=self.analyst)
        response = self.client.post('/api/transactions/', {
            'amount': -50, 'type': 'income', 'category': 'Test', 'date': '2025-04-06'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('amount', response.data['details'])

    def test_dashboard_respects_user_isolation(self):
        FinancialRecord.objects.create(amount=1000, type='income', category='Salary', date='2025-04-06', created_by=self.analyst)
        self.client.force_authenticate(user=self.viewer)
        resp = self.client.get('/api/transactions/dashboard/summary/')
        self.assertEqual(resp.data['total_income'], 0)
        self.assertEqual(resp.data['total_expense'], 0)