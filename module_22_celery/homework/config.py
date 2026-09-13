"""
В этом файле будут секретные данные и конфигурация проекта.

Для создания почтового сервиса воспользуйтесь следующими инструкциями:

- Yandex: https://yandex.ru/support/mail/mail-clients/others.html
- Google: https://support.google.com/mail/answer/7126229
"""

# Почта
SMTP_USER = "ПОЧТА ОТПРАВИТЕЛЯ"
SMTP_HOST = "smtp.yandex.com"
SMTP_PASSWORD = "ПАРОЛЬ ОТ ПОЧТЫ ОТПРАВИТЕЛЯ / СПЕЦИАЛЬНЫЙ ТОКЕН ПРИЛОЖЕНИЯ"
SMTP_PORT = 587

EMAIL_FROM = SMTP_USER  # от кого отправляем (совпадает с пользователем)


# Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"        # или "amqp://guest@localhost//" для RabbitMQ
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"   # или "rpc://", или БД

# Периодические задачи (Celery Beat)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "weekly-newsletter": {
        "task": "tasks.weekly_newsletter",
        "schedule": crontab(hour=10, minute=0, day_of_week="mon"),  # каждый понедельник в 10:00
    },
}

# Пути для файлов
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# База данных подписчиков
DATABASE_PATH = BASE_DIR / "subscribers.db"

# Flask
SECRET_KEY = "secret-key-change-in-production"