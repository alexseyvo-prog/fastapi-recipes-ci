import requests

# Подписка
resp = requests.post(
    "http://127.0.0.1:5000/subscribe",
    json={"email": "test@example.com"}
)
print("Subscribe:", resp.status_code, resp.json())

# Повторная подписка (должен вернуть 200)
resp2 = requests.post(
    "http://127.0.0.1:5000/subscribe",
    json={"email": "test@example.com"}
)
print("Subscribe again:", resp2.status_code, resp2.json())