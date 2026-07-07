import unittest

from app import app, storage

# Импортируем unittest для написания модульных тестов.
# Из модуля app импортируем Flask-приложение app и глобальное хранилище storage,
# чтобы тестировать HTTP-эндпоинты и работу с данными.


class TestFinanceApp(unittest.TestCase):
    """
    Класс TestFinanceApp содержит набор тестов для финансового Flask-приложения.
    Он проверяет:
    - корректность работы эндпоинта /add/ (добавление данных);
    - корректность расчётов по дате, по категории и общего итога через /calculate/;
    - поведение на пустом хранилище и некорректных входных данных.
    """

    @classmethod
    def setUpClass(cls):
        """
        setUpClass вызывается один раз перед запуском всех тестов класса.
        Здесь создаём тестовый клиент Flask, чтобы отправлять HTTP-запросы к приложению
        без запуска реального сервера.
        """
        cls.client = app.test_client()

    def setUp(self):
        """
        setUp вызывается перед каждым отдельным тестом.
        В этом методе мы очищаем и заново заполняем storage базовым набором данных,
        чтобы каждый тест начинался с одинакового известного состояния.

        Исходные данные:
        - на дату 20240101: категория 'food' = 100, 'transport' = 50 (итого 150);
        - на дату 20240102: категория 'food' = 200.
        """
        storage.clear()
        storage.update({
            '20240101': {'food': 100, 'transport': 50},
            '20240102': {'food': 200},
        })

    def test_add_endpoint_ok(self):
        """
        Проверяет, что эндпоинт /add/ корректно отвечает при валидных параметрах.

        Отправляем GET-запрос:
        /add/?date=20240103&amount=300&category=salary

        Ожидаем:
        - код ответа 200 (успешная обработка);
        - это означает, что вызов add_income внутри эндпоинта не привёл к ошибке.
        """
        response = self.client.get('/add/?date=20240103&amount=300&category=salary')
        self.assertEqual(response.status_code, 200)

    def test_add_endpoint_adds_value(self):
        """
        Проверяет, что эндпоинт /add/ действительно добавляет новое значение в хранилище.

        Шаги:
        - сначала отправляем запрос на добавление дохода:
          /add/?date=20240103&amount=300&category=salary;
        - затем вызываем /calculate/?date=20240103 для проверки суммы по этой дате.

        Ожидаем:
        - код ответа 200;
        - в теле ответа присутствует строка '300', означающая, что доход добавлен.
        """
        self.client.get('/add/?date=20240103&amount=300&category=salary')
        response = self.client.get('/calculate/?date=20240103')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'300', response.data)

    def test_add_endpoint_invalid_date(self):
        """
        Проверяет реакцию на некорректный формат даты при добавлении дохода.

        Шаг:
        - отправляем запрос с датой '2024-01-03' (с дефисами), что нарушает условие
          формата 'YYYYMMDD'.

        Ожидаем:
        - код ответа 500 (внутренняя ошибка сервера), так как add_income должен
          выбросить TypeError('Invalid date format'), который Flask превратит в ошибку.
        """
        response = self.client.get('/add/?date=2024-01-03&amount=300&category=salary')
        self.assertEqual(response.status_code, 500)

    def test_calculate_by_date(self):
        """
        Проверяет вычисление суммы доходов по конкретной дате через /calculate/?date=...

        Исходные данные из setUp:
        - на дату 20240101: food = 100, transport = 50, итого 150.

        Шаг:
        - вызываем /calculate/?date=20240101.

        Ожидаем:
        - код ответа 200;
        - в теле ответа присутствует '150'.
        """
        response = self.client.get('/calculate/?date=20240101')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'150', response.data)

    def test_calculate_by_category(self):
        """
        Проверяет вычисление суммы доходов по категории через /calculate/?category=...

        Исходные данные:
        - категория 'food' встречается:
          * 20240101: 100
          * 20240102: 200
          суммарно 300.

        Шаг:
        - вызываем /calculate/?category=food.

        Ожидаем:
        - код ответа 200;
        - в теле ответа присутствует '300'.
        """
        response = self.client.get('/calculate/?category=food')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'300', response.data)

    def test_calculate_total(self):
        """
        Проверяет общий расчёт суммы всех доходов через /calculate/ без параметров.

        Исходные данные:
        - 20240101: 100 (food) + 50 (transport) = 150;
        - 20240102: 200 (food) = 200;
        Итого: 150 + 200 = 350.

        Шаг:
        - вызываем /calculate/ (без date и category).

        Ожидаем:
        - код ответа 200;
        - в теле ответа присутствует '350'.
        """
        response = self.client.get('/calculate/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'350', response.data)

    def test_calculate_empty_by_date(self):
        """
        Проверяет расчёт по дате, когда хранилище пустое.

        Шаги:
        - полностью очищаем storage;
        - вызываем /calculate/?date=20240101.

        Ожидаем:
        - код ответа 200;
        - в теле ответа '0', так как данных по этой дате нет.
        """
        storage.clear()
        response = self.client.get('/calculate/?date=20240101')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'0', response.data)

    def test_calculate_empty_by_category(self):
        """
        Проверяет расчёт по категории, когда хранилище пустое.

        Шаги:
        - очищаем storage;
        - вызываем /calculate/?category=food.

        Ожидаем:
        - код ответа 200;
        - в теле ответа '0', так как данных по категории 'food' нет.
        """
        storage.clear()
        response = self.client.get('/calculate/?category=food')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'0', response.data)

    def test_calculate_empty_total(self):
        """
        Проверяет общий расчёт суммы доходов для пустого хранилища.

        Шаги:
        - очищаем storage;
        - вызываем /calculate/ без параметров.

        Ожидаем:
        - код ответа 200;
        - в теле ответа '0', так как нет ни одной записи дохода.
        """
        storage.clear()
        response = self.client.get('/calculate/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'0', response.data)


if __name__ == '__main__':
    # Запускаем все тесты из этого файла, если он выполняется как скрипт.
    # unittest.main() автоматически находит все классы TestCase и запускает методы test_*.
    unittest.main()