"""
Для каждого поля и валидатора в эндпоинте /registration напишите юнит-тест,
который проверит корректность работы валидатора. Таким образом, нужно проверить, что существуют наборы данных,
которые проходят валидацию, и такие, которые валидацию не проходят.

Этот файл содержит набор юнит-тестов для Flask-эндпоинта /registration.
Тесты используют тестовый клиент Flask, отправляют POST-запросы с разными данными
и проверяют:
- что корректные данные проходят валидацию (ответ 200);
- что некорректные данные не проходят валидацию (ответ 400 и соответствующие сообщения об ошибках).
"""

import unittest

from hw1_registration import app  # приложение с /registration


class TestRegistrationValidators(unittest.TestCase):
    """
    Набор тестов для проверки валидаторов формы RegistrationForm,
    обрабатываемой эндпоинтом /registration.

    Каждый тест отправляет POST-запрос на /registration с конкретным набором данных
    и проверяет статус ответа и наличие ожидаемых сообщений.
    """

    @classmethod
    def setUpClass(cls):
        """
        Инициализация тестового окружения один раз для всего набора тестов.

        - Включаем режим TESTING для Flask-приложения.
        - Отключаем CSRF для удобства тестирования форм (иначе потребуется токен).
        - Устанавливаем секретный ключ, если он ещё не задан.
        - Создаём тестовый клиент, который будет использоваться во всех тестах.
        """
        app.config["TESTING"] = True
        # Отключаем CSRF, чтобы не нужно было передавать токен в каждом запросе
        app.config["WTF_CSRF_ENABLED"] = False
        # Гарантируем наличие секретного ключа
        app.config.setdefault("SECRET_KEY", "test-secret-key")
        cls.client = app.test_client()

    # ===== email =====

    def test_email_valid(self):
        """
        Проверяет, что корректный email проходит валидацию.

        Ожидаемое поведение:
        - статус ответа 200;
        - в тексте ответа присутствует сообщение об успешной регистрации
          с указанным email.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
                "comment": "Hello",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully registered user test@example.com", response.data)

    def test_email_invalid_format(self):
        """
        Проверяет, что email с некорректным форматом не проходит валидацию.

        Используем строку без символа '@' и домена.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствуют:
          - ключ 'email' в словаре ошибок;
          - сообщение 'Invalid email format' от валидатора Email.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "wrong_email",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"email", response.data)
        self.assertIn(b"Invalid email format", response.data)

    def test_email_missing(self):
        """
        Проверяет, что отсутствие обязательного поля email не проходит валидацию.

        Поле email не передаётся в запросе.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует сообщение 'Email is required'
          от валидатора DataRequired.
        """
        response = self.client.post(
            "/registration",
            data={
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Email is required", response.data)

    # ===== phone =====

    def test_phone_valid(self):
        """
        Проверяет, что телефон из 10 цифр проходит валидацию.

        Используем ровно 10 цифр, соответствующих требованиям NumberLength.
        Ожидаемое поведение:
        - статус ответа 200;
        - в тексте ответа присутствует сформированный номер +7<phone>.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"+71234567890", response.data)

    def test_phone_too_short(self):
        """
        Проверяет, что телефон, короче 10 цифр, не проходит валидацию.

        Используем строку из 5 цифр.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует сообщение 'Phone must be 10 digits long'
          от валидатора NumberLength.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "12345",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Phone must be 10 digits long", response.data)

    def test_phone_not_digits(self):
        """
        Проверяет, что телефон с нецифровыми символами не проходит валидацию,
        если в форме предусмотрен такой валидатор.

        Используем строку, содержащую буквы.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует информация об ошибке поля 'phone'.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "12ab567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"phone", response.data)

    def test_phone_missing(self):
        """
        Проверяет, что отсутствие обязательного поля phone не проходит валидацию.

        Поле phone не передаётся в запросе.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует сообщение 'Phone is required'
          от валидатора DataRequired.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Phone is required", response.data)

    # ===== name =====

    def test_name_valid(self):
        """
        Проверяет, что корректное имя (непустая строка) проходит валидацию.

        Ожидаемое поведение:
        - статус ответа 200.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_name_missing(self):
        """
        Проверяет, что отсутствие обязательного поля name не проходит валидацию.

        Поле name не передаётся в запросе.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует сообщение 'Name is required'
          от валидатора DataRequired.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Name is required", response.data)

    # ===== address =====

    def test_address_valid(self):
        """
        Проверяет, что корректный адрес проходит валидацию.

        Ожидаемое поведение:
        - статус ответа 200.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_address_missing(self):
        """
        Проверяет, что отсутствие обязательного поля address не проходит валидацию.

        Поле address не передаётся в запросе.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует сообщение 'Address is required'
          от валидатора DataRequired.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Address is required", response.data)

    # ===== index =====

    def test_index_valid(self):
        """
        Проверяет, что корректный числовой индекс проходит валидацию.

        Ожидаемое поведение:
        - статус ответа 200.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_index_missing(self):
        """
        Проверяет, что отсутствие обязательного поля index не проходит валидацию.

        Поле index не передаётся в запросе.
        Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует сообщение 'Index is required'
          от валидатора DataRequired.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Index is required", response.data)

    def test_index_not_number(self):
        """
        Проверяет, что индекс, переданный как нечисловое значение, не проходит валидацию.

        Поскольку поле index описано как IntegerField, WTForms попытается привести значение к int
        и при неудаче добавит ошибку. Ожидаемое поведение:
        - статус ответа 400;
        - в тексте ответа присутствует упоминание поля 'index' в словаре ошибок.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "abc",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"index", response.data)

    # ===== comment (опциональное поле) =====

    def test_comment_optional_missing(self):
        """
        Проверяет, что отсутствие необязательного поля comment не ломает валидацию.

        Поле comment не передаётся в запросе.
        Ожидаемое поведение:
        - статус ответа 200 (остальные обязательные поля заполнены корректно).
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_comment_present(self):
        """
        Проверяет, что заполненное поле comment также проходит валидацию.

        Ожидаемое поведение:
        - статус ответа 200.
        """
        response = self.client.post(
            "/registration",
            data={
                "email": "test@example.com",
                "phone": "1234567890",
                "name": "Ivan",
                "address": "Moscow",
                "index": "123456",
                "comment": "Test comment",
            },
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    # Запускаем все тесты при запуске файла напрямую
    unittest.main()