# test_add_book.py
import requests

response = requests.post(
    'http://127.0.0.1:5000/api/books',
    json={
        'title': 'Анна Каренина',
        'author': 'Толстой',
        'year': 1877
    }
)

print(response.status_code)
print(response.json())