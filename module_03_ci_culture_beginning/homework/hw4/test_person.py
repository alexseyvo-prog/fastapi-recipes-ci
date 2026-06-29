import unittest
import datetime

from person import Person  # имя файла с классом: person.py


class TestPerson(unittest.TestCase):
    def setUp(self):
        # базовый объект для большинства тестов
        self.person = Person(name='Petya', year_of_birth=2000, address='Moscow')

    def test_get_age(self):
        p = Person('Test', 1990)
        now_year = datetime.datetime.now().year
        self.assertEqual(p.get_age(), now_year - 1990)

    def test_get_name(self):
        self.assertEqual(self.person.get_name(), 'Petya')

    def test_set_name_changes_name(self):
        self.person.set_name('Vasya')
        self.assertEqual(self.person.get_name(), 'Vasya')

    def test_get_address(self):
        self.assertEqual(self.person.get_address(), 'Moscow')

    def test_set_address_changes_address(self):
        self.person.set_address('Berlin')
        self.assertEqual(self.person.get_address(), 'Berlin')

    def test_is_homeless_true_when_empty_string(self):
        p = Person('NoAddress', 1995, '')
        self.assertTrue(p.is_homeless())

    def test_is_homeless_true_when_none(self):
        p = Person('NoAddress', 1995, None)
        self.assertTrue(p.is_homeless())

    def test_is_homeless_false_when_address_set(self):
        self.assertFalse(self.person.is_homeless())


if __name__ == '__main__':
    unittest.main()