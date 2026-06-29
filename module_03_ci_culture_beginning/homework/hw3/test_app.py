import unittest

from app import app, storage


class TestFinanceApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def setUp(self):
        storage.clear()
        storage.update({
            '20240101': {'food': 100, 'transport': 50},
            '20240102': {'food': 200},
        })

    def test_add_endpoint_ok(self):
        response = self.client.get('/add/?date=20240103&amount=300&category=salary')
        self.assertEqual(response.status_code, 200)

    def test_add_endpoint_adds_value(self):
        self.client.get('/add/?date=20240103&amount=300&category=salary')
        response = self.client.get('/calculate/?date=20240103')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'300', response.data)

    def test_add_endpoint_invalid_date(self):
        response = self.client.get('/add/?date=2024-01-03&amount=300&category=salary')
        self.assertEqual(response.status_code, 500)

    def test_calculate_by_date(self):
        response = self.client.get('/calculate/?date=20240101')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'150', response.data)

    def test_calculate_by_category(self):
        response = self.client.get('/calculate/?category=food')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'300', response.data)

    def test_calculate_total(self):
        response = self.client.get('/calculate/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'350', response.data)

    def test_calculate_empty_by_date(self):
        storage.clear()
        response = self.client.get('/calculate/?date=20240101')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'0', response.data)

    def test_calculate_empty_by_category(self):
        storage.clear()
        response = self.client.get('/calculate/?category=food')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'0', response.data)

    def test_calculate_empty_total(self):
        storage.clear()
        response = self.client.get('/calculate/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'0', response.data)


if __name__ == '__main__':
    unittest.main()