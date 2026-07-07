import unittest
import datetime

from person import Person  # имя файла с классом: person.py


class TestPerson(unittest.TestCase):
    """
    Набор модульных тестов для класса Person.

    Этот класс проверяет:
    - корректность вычисления возраста;
    - работу методов получения и изменения имени;
    - работу методов получения и изменения адреса;
    - логику определения, считается ли человек «без адреса».
    """

    def setUp(self):
        """
        Подготовка общего тестового объекта перед каждым тестом.

        Логика:
        - создаётся экземпляр Person с именем 'Petya',
          годом рождения 2000 и адресом 'Moscow';
        - этот объект сохраняется в self.person и используется
          в нескольких тестах, чтобы не дублировать код создания.
        """
        # базовый объект для большинства тестов
        self.person = Person(name='Petya', year_of_birth=2000, address='Moscow')

    def test_get_age(self):
        """
        Проверяет корректность работы метода get_age().

        Шаги:
        - создаётся объект Person с годом рождения 1990;
        - берётся текущий год через datetime.datetime.now().year;
        - ожидаемый возраст вычисляется как (текущий год - 1990);
        - метод get_age() должен вернуть именно эту величину.
        """
        p = Person('Test', 1990)
        now_year = datetime.datetime.now().year
        self.assertEqual(p.get_age(), now_year - 1990)

    def test_get_name(self):
        """
        Проверяет, что метод get_name() возвращает корректное имя.

        Логика:
        - объект self.person был создан в setUp с именем 'Petya';
        - вызов get_name() должен вернуть строку 'Petya'.
        """
        self.assertEqual(self.person.get_name(), 'Petya')

    def test_set_name_changes_name(self):
        """
        Проверяет, что метод set_name() действительно изменяет имя объекта.

        Шаги:
        - вызываем self.person.set_name('Vasya');
        - затем проверяем, что get_name() возвращает новое имя 'Vasya',
          а не старое 'Petya'.
        """
        self.person.set_name('Vasya')
        self.assertEqual(self.person.get_name(), 'Vasya')

    def test_get_address(self):
        """
        Проверяет, что метод get_address() возвращает корректный адрес.

        Логика:
        - у объекта self.person исходный адрес 'Moscow';
        - вызов get_address() должен вернуть именно 'Moscow'.
        """
        self.assertEqual(self.person.get_address(), 'Moscow')

    def test_set_address_changes_address(self):
        """
        Проверяет, что метод set_address() изменяет адрес объекта.

        Шаги:
        - вызываем self.person.set_address('Berlin');
        - проверяем, что get_address() возвращает новый адрес 'Berlin',
          а не старый 'Moscow'.
        """
        self.person.set_address('Berlin')
        self.assertEqual(self.person.get_address(), 'Berlin')

    def test_is_homeless_true_when_empty_string(self):
        """
        Проверяет, что is_homeless() возвращает True,
        когда адрес задан как пустая строка.

        Логика:
        - создаём объект Person с address = '';
        - по контракту метода пустая строка считается отсутствием адреса,
          поэтому is_homeless() должен вернуть True.
        """
        p = Person('NoAddress', 1995, '')
        self.assertTrue(p.is_homeless())

    def test_is_homeless_true_when_none(self):
        """
        Проверяет, что is_homeless() возвращает True,
        когда адрес равен None.

        Логика:
        - создаём объект Person с address = None;
        - отсутствие адреса (None) должно трактоваться как «бездомный»,
          поэтому is_homeless() должен вернуть True.
        """
        p = Person('NoAddress', 1995, None)
        self.assertTrue(p.is_homeless())

    def test_is_homeless_false_when_address_set(self):
        """
        Проверяет, что is_homeless() возвращает False,
        когда у человека указан нормальный адрес.

        Логика:
        - у self.person адрес 'Moscow' задан явно;
        - метод is_homeless() должен вернуть False.
        """
        self.assertFalse(self.person.is_homeless())


if __name__ == '__main__':
    # Запускает все тесты в этом файле, если файл выполняется как скрипт.
    # unittest.main() находит все классы, унаследованные от unittest.TestCase,
    # и запускает все методы, имена которых начинаются с test_.
    unittest.main()