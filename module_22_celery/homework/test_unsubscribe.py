import requests

# Отписка
resp = requests.post(
    "http://127.0.0.1:5000/unsubscribe",
    json={"email": "test@example.com"}
)
print("Unsubscribe:", resp.status_code, resp.json())

# Повторная отписка (должен вернуть 404)
resp2 = requests.post(
    "http://127.0.0.1:5000/unsubscribe",
    json={"email": "test@example.com"}
)
print("Unsubscribe again:", resp2.status_code, resp2.json())