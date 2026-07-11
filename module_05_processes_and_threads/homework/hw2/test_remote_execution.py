import unittest
from remote_execution import app


class TestRemoteExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False  # чтобы не мешал CSRF
        cls.client = app.test_client()

    def test_timeout_exceeded(self):
        """
        Тайм-аут меньше, чем время выполнения.
        Ожидаем сообщение о том, что выполнение не уложилось.
        """
        response = self.client.post(
            "/run_code",
            json={
                "code": "import time; time.sleep(5); print('done')",
                "timeout": 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["timed_out"])
        self.assertIn("не уложилось", data["message"])
        # 'done' не должно успеть попасть в stdout
        self.assertNotIn("done", data["stdout"])

    def test_invalid_form_data(self):
        """
        Некорректные данные формы:
        - пустой код
        - тайм-аут вне диапазона
        """
        response = self.client.post(
            "/run_code",
            json={
                "code": "",
                "timeout": 0,
            },
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["ok"])
        self.assertIn("code", data["errors"])
        self.assertIn("timeout", data["errors"])

    def test_shell_injection_not_possible(self):
        """
        Пытаемся передать код, который при shell=True мог бы выполнить лишние команды.
        Ожидаем, что ничего стороннего не выполнится.
        """
        inj_code = 'print()"; import os; os.system("echo hacked")  #'
        response = self.client.post(
            "/run_code",
            json={
                "code": inj_code,
                "timeout": 5,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # Никакого "hacked" в stdout
        self.assertNotIn("hacked", data["stdout"])
        # Скорее всего будет SyntaxError — это нормальная реакция интерпретатора
        self.assertTrue(
            "SyntaxError" in data["stderr"] or "Traceback" in data["stderr"]
        )


if __name__ == '__main__':
    unittest.main()