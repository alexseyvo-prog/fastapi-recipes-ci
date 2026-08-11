FROM python:3.10-slim

WORKDIR /app

# Сначала устанавливаем зависимости (меняются реже)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем копируем код и ресурсы (меняются чаще)
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]