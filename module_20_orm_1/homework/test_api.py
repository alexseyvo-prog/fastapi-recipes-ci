# test_api.py
import requests

BASE_URL = 'http://127.0.0.1:5000'

def print_response(response, title=""):
    """Красивый вывод ответа."""
    print(f"\n{'='*60}")
    if title:
        print(f"=== {title} ===")
    print(f"Статус: {response.status_code}")
    try:
        print(f"Ответ: {response.json()}")
    except:
        print(f"Ответ (текст): {response.text}")


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

# 3. Получить студентов с average_score > 4.0
print("\n[3] GET /api/students/high-score?score=4.0 - Студенты с баллом > 4.0")
response = requests.get(f'{BASE_URL}/api/students/high-score', params={'score': 4.0})
print_response(response, "Студенты с высоким баллом")

# 4. Выдать книгу студенту
print("\n[4] POST /api/give - Выдать книгу студенту")
response = requests.post(
    f'{BASE_URL}/api/give',
    json={'student_id': 1, 'book_id': 3}  # Книга с count=3
)
print_response(response, "Выдача книги")

# 5. Проверить количество книг (count должен уменьшиться)
print("\n[5] GET /api/books - Проверка количества книг")
response = requests.get(f'{BASE_URL}/api/books')
print_response(response, "Книги после выдачи")

# 6. Сдать книгу
print("\n[6] POST /api/return - Сдать книгу")
response = requests.post(
    f'{BASE_URL}/api/return',
    json={'student_id': 1, 'book_id': 3}
)
print_response(response, "Возврат книги")

# 7. Проверить количество книг (count должен увеличиться)
print("\n[7] GET /api/books - Проверка количества книг после возврата")
response = requests.get(f'{BASE_URL}/api/books')
print_response(response, "Книги после возврата")

# 8. Получить должников
print("\n[8] GET /api/debtors - Должники (> 14 дней)")
response = requests.get(f'{BASE_URL}/api/debtors')
print_response(response, "Должники")

# 9. Поиск книг
print("\n[9] GET /api/search?q=мир - Поиск книг")
response = requests.get(f'{BASE_URL}/api/search', params={'q': 'мир'})
print_response(response, "Поиск книг")

# 10. Ошибка: сдать книгу, которой нет
print("\n[10] POST /api/return - Ошибка (несуществующая связка)")
response = requests.post(
    f'{BASE_URL}/api/return',
    json={'student_id': 999, 'book_id': 999}
)
print_response(response, "Ошибка возврата")

print("\n" + "="*60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*60)