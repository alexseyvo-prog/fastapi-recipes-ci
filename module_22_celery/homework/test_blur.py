import requests
from PIL import Image
import io
import time

url = "http://127.0.0.1:5000/blur"

# Создаём тестовое изображение
img = Image.new("RGB", (100, 100), color="blue")
buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)

files = {"images": ("test.png", buf, "image/png")}
data = {"email": "test@example.com"}

resp = requests.post(url, files=files, data=data)
print("POST /blur:", resp.status_code)
print("Response:", resp.json())

task_id = resp.json()["task_id"]
print(f"Task ID: {task_id}")

# Ждём выполнения задачи
print("Waiting 3 seconds...")
time.sleep(3)

# Проверяем статус
status_resp = requests.get(f"http://127.0.0.1:5000/status/{task_id}")
print("GET /status:", status_resp.status_code)
print("Status:", status_resp.json())