# test_uptime.py

import unittest
from unittest.mock import patch
from uptime import app


class TestUptimeEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    @patch("uptime.os.popen")
    def test_uptime_status_code_ok(self, mock_popen):
        """
        GET /uptime должен возвращать HTTP 200.
        """
        # Мокаем результат вызова uptime -p, чтобы не запускать реальный процесс
        mock_popen.return_value.read.return_value = "up 3 hours, 10 minutes\n"

        print(">>> test_uptime_status_code_ok started")
        response = self.client.get("/uptime")
        self.assertEqual(response.status_code, 200)

    @patch("uptime.os.popen")
    def test_uptime_prefix_text(self, mock_popen):
        mock_popen.return_value.read.return_value = "up 3 hours, 10 minutes\n"

        response = self.client.get("/uptime")
        data = response.data.decode("utf-8")
        self.assertTrue(data.startswith("Current uptime is "))

    @patch("uptime.os.popen")
    def test_uptime_not_empty_value(self, mock_popen):
        mock_popen.return_value.read.return_value = "up 3 hours, 10 minutes\n"

        response = self.client.get("/uptime")
        data = response.data.decode("utf-8")
        prefix = "Current uptime is "
        self.assertTrue(data.startswith(prefix))
        uptime_value = data[len(prefix):].strip()
        self.assertNotEqual(uptime_value, "")