# test_api.py
import requests
from datetime import date, timedelta

BASE_URL = 'http://127.0.0.1:5000'

def print_response(response, title=""):
    """Красивый вывод ответа."""
    print(f"\n{'='*60}")
    if title:
        print(f"=== {title} ===")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")


print("\n" + "="*60)
print("ТЕСТИРОВАНИЕ API БИБЛИОТЕКИ")
print("="*60)

# 1. Получить все книги
print("\n[1] GET /api/books - Получить все книги")
response = requests.get(f'{BASE_URL}/api/books')
print_response(response, "Все книги")

# 2. Получить студентов с общежитием
print("\n[2] GET /api/students/dormitory - Студенты с общежитием")
response = requests.get(f'{BASE_URL}/api/students/dormitory')
print_response(response, "Студенты с общежитием")

# 3. Получить студентов с GPA > 4.0
print("\n[3] GET /api/students/high-gpa?gpa=4.0 - Студенты с GPA > 4.0")
response = requests.get(f'{BASE_URL}/api/students/high-gpa', params={'gpa': 4.0})
print_response(response, "Студенты с высоким GPA")

# 4. Выдать книгу студенту
print("\n[4] POST /api/give - Выдать книгу студенту")
response = requests.post(
    f'{BASE_URL}/api/give',
    json={'student_id': 1, 'book_id': 1}
)
print_response(response, "Выдача книги")

# 5. Получить всех книг (проверка, что книга выдана)
print("\n[5] GET /api/books - Проверка книг")
response = requests.get(f'{BASE_URL}/api/books')
print_response(response, "Книги после выдачи")

# 6. Получить должников
print("\n[6] GET /api/debtors - Должники (> 14 дней)")
response = requests.get(f'{BASE_URL}/api/debtors')
print_response(response, "Должники")

# 7. Сдать книгу
print("\n[7] POST /api/return - Сдать книгу")
response = requests.post(
    f'{BASE_URL}/api/return',
    json={'student_id': 1, 'book_id': 1}
)
print_response(response, "Возврат книги")

# 8. Поиск книг
print("\n[8] GET /api/search?q=мир - Поиск книг")
response = requests.get(f'{BASE_URL}/api/search', params={'q': 'мир'})
print_response(response, "Поиск книг")

# 9. Ошибка: сдать книгу, которой нет
print("\n[9] POST /api/return - Ошибка (несуществующая связка)")
response = requests.post(
    f'{BASE_URL}/api/return',
    json={'student_id': 999, 'book_id': 999}
)
print_response(response, "Ошибка возврата")

# 10. Добавить книгу (если есть роут)
print("\n[10] POST /api/books - Добавить книгу")
response = requests.post(
    f'{BASE_URL}/api/books',
    json={'title': 'Анна Каренина', 'author': 'Толстой', 'year': 1877}
)
print_response(response, "Добавление книги")

print("\n" + "="*60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*60)