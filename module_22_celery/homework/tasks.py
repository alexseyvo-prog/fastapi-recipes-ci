"""
В этом файле будут Celery-задачи
"""
import time
from typing import List

from celery import Celery, group

from config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    DATABASE_PATH,
)
from image import blur_image
from mail import send_email

celery_app = Celery(
    "image_blur_service",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

celery_app.config_from_object("config")

# Настройки для Windows и JSON-сериализации
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_pool="solo",
)


# ==================== Модели / БД (упрощённо через SQLite) ====================

import sqlite3
from contextlib import contextmanager

DB_PATH = DATABASE_PATH


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_subscribers_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL
            )
            """
        )
        conn.commit()


def add_subscriber(email: str) -> bool:
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO subscribers (email) VALUES (?)",
                (email,),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_subscriber(email: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM subscribers WHERE email = ?",
            (email,),
        )
        conn.commit()
        return cursor.rowcount > 0


def get_all_subscribers() -> List[str]:
    with get_db_connection() as conn:
        rows = conn.execute("SELECT email FROM subscribers").fetchall()
        return [row["email"] for row in rows]


# ==================== Задачи Celery ====================


@celery_app.task(bind=True, name="tasks.blur_image_task")
def blur_image_task(self, src_filename: str, dst_filename: str, delay: float = 0.0):
    """
    Задача размытия одного изображения.
    """
    if delay:
        time.sleep(delay)

    blur_image(src_filename, dst_filename)

    return {
        "src": src_filename,
        "dst": dst_filename,
        "status": "done",
    }


@celery_app.task(bind=True, name="tasks.send_result_email")
def send_result_email_task(self, order_id: str, receiver: str, archive_path: str):
    """
    Задача отправки письма с архивом размытых изображений.
    Вызывает send_email из mail.py.
    """
    send_email(order_id, receiver, archive_path)
    return {"order_id": order_id, "receiver": receiver, "status": "sent"}


@celery_app.task(bind=True, name="tasks.send_newsletter")
def send_newsletter_task(self, email: str):
    """
    Задача отправки еженедельной рассылки одному подписчику.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    from config import SMTP_USER, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT

    subject = "Новости сервиса размытия изображений"
    body = """
Здравствуйте!

Это еженедельная рассылка от сервиса размытия изображений.
Напоминаем, что вы можете загружать изображения на обработку, 
а мы применим эффект размытия и отправим результат на вашу почту.

С уважением,
Команда сервиса
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    return {"email": email, "status": "sent"}


@celery_app.task(name="tasks.weekly_newsletter")
def weekly_newsletter():
    """
    Периодическая задача: раз в неделю отправляет рассылку всем подписчикам.
    """
    subscribers = get_all_subscribers()
    if not subscribers:
        return {"sent_count": 0, "status": "no_subscribers"}

    tasks = [send_newsletter_task.s(email) for email in subscribers]
    job = group(tasks).apply_async()
    job.join()

    return {
        "sent_count": len(subscribers),
        "status": "done",
    }


# Инициализация БД при импорте
init_subscribers_db()