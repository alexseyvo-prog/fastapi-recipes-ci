# test_count_check.py
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
print("ПРОВЕРКА: Нельзя выдать больше книг, чем есть в наличии")
print("="*60)

# 1. Получить все книги и найти книгу с count=1
print("\n[1] GET /api/books - Найти книгу с count=1")
response = requests.get(f'{BASE_URL}/api/books')
books = response.json()

# Найти книгу с count=1 (например, "Преступление и наказание")
book_to_test = None
for book in books:
    if book['count'] == 1:
        book_to_test = book
        break

if not book_to_test:
    print("Нет книги с count=1. Пропускаем тест.")
    exit(0)

print(f"Тестируем книгу: {book_to_test['name']} (count={book_to_test['count']})")
book_id = book_to_test['id']

# 2. Выдать книгу первому студенту (успешно)
print(f"\n[2] POST /api/give - Выдать книгу студенту 1")
response = requests.post(
    f'{BASE_URL}/api/give',
    json={'student_id': 1, 'book_id': book_id}
)
print_response(response, "Первая выдача")

if response.status_code != 201:
    print("Ошибка при первой выдаче!")
    exit(1)

# 3. Попытаться выдать ту же книгу второму студенту (должно быть 409)
print(f"\n[3] POST /api/give - Попытаться выдать ту же книгу студенту 2")
response = requests.post(
    f'{BASE_URL}/api/give',
    json={'student_id': 2, 'book_id': book_id}
)
print_response(response, "Вторая выдача (ошибка)")

if response.status_code == 409:
    print("\n✅ УСПЕХ: Система не позволила выдать книгу, когда count=0")
elif response.status_code == 201:
    print("\n❌ ОШИБКА: Система выдала книгу, хотя count=0!")
else:
    print(f"\n⚠ Неожиданный статус: {response.status_code}")

# 4. Проверить количество книг
print(f"\n[4] GET /api/books - Проверить count книги")
response = requests.get(f'{BASE_URL}/api/books')
books = response.json()

for book in books:
    if book['id'] == book_id:
        print(f"Книга '{book['name']}': count = {book['count']}")
        if book['count'] == 0:
            print("✅ count корректно уменьшился до 0")
        else:
            print(f"⚠ Ожидалось count=0, но получилось {book['count']}")
        break

print("\n" + "="*60)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("="*60)