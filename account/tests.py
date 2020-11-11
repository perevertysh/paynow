from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from .models import Account


class CheckerTest(APITestCase):
    fixtures = ["account/fixtures/test.json"]

    task_id: int = None

    def setUp(self):
        pass

    def test_get_accounts(self):
        """'Get' accounts list"""
        response = self.client.get(reverse("account-list"),
                                   format='json')

        self.assertEqual(response.status_code, 200,
                         f"Wrong status code: {response.status_code}")
        self.assertTrue(response.data,
                        f"Wrong data: {response.data}")

    def test_create_account(self):
        """Test creating of new account"""
        response = self.client.post(reverse("account-list"),
                                    {"inn": "012345678912",
                                     "amount": 100000.00,
                                     "user": 5})

        self.assertEqual(response.status_code, 201,
                         f"Wrong status code: {response.status_code} "
                         f"\n {response.data}")
        self.assertTrue(response.data,
                        f"Wrong data: {response.data}")

    def test_validation_inn(self):
        """Validation account' inn field test"""
        response = self.client.post(reverse("account-list"),
                                    {"inn": "0123456789XX",
                                     "amount": 100000.00,
                                     "user": 5})

        self.assertEqual(response.status_code, 400,
                         f"Wrong status code: {response.status_code} "
                         f"\n {response.data}")

        response = self.client.post(reverse("account-list"),
                                    {"inn": "012345678900 000000000000",
                                     "amount": 100000.00,
                                     "user": 5})

        self.assertEqual(response.status_code, 400,
                         f"Wrong status code: {response.status_code} "
                         f"\n {response.data}")

    def test_send_money(self):
        """Send money endpoint test"""

        response = self.client.post(
            reverse("account-send-money"),
            {
                "amount": 100,
                "recipients": "325648698745 654987655498",
                "sender": "9ff555bb-90f2-435d-86fa-6b9ef1970dd7"
            }, format='json'
        )

        self.assertEqual(response.status_code, 200,
                         f"Wrong status code: {response.status_code}")

        self.assertEqual(50.0, Account.objects.all().first().amount,
                         f"Wrong transaction processing: "
                         f"{Account.objects.all().first().amount} != 50.0")

    def test_send_money_over_amount(self):
        """Test amount validation"""
        response = self.client.post(
            reverse("account-send-money"),
            {
                "amount": 1000000,
                "recipients": "325648698745 654987655498",
                "sender": "9ff555bb-90f2-435d-86fa-6b9ef1970dd7"
            }, format='json'
        )

        self.assertEqual(response.status_code, 400,
                         f"Wrong status code: {response.status_code}")

        self.assertFalse(1000000 == Account.objects.all().first().amount,
                         f"Amount validation error: "
                         f"{Account.objects.all().first().amount} == 1000000")

    def test_send_money_wrong_inn(self):
        """Test recipients inn validation"""
        response = self.client.post(
            reverse("account-send-money"),
            {
                "amount": 100,
                "recipients": "000000000000 654987655498",
                "sender": "9ff555bb-90f2-435d-86fa-6b9ef1970dd7"
            }, format='json'
        )

        test_case = ['000000000000', '654987655498']

        self.assertEqual(response.status_code, 400,
                         f"Wrong status code: {response.status_code}")

        recipients = Account.objects.filter(inn__in=test_case)
        self.assertFalse(len(recipients) == len(test_case),
                         f"inn validation error: {recipients}")
