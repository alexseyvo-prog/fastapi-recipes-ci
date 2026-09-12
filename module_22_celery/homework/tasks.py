"""
В этом файле будут Celery-задачи
"""
import time
import zipfile
from pathlib import Path
from typing import List, Any, Dict

from celery import Celery, group

from config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    DATABASE_PATH,
    OUTPUT_FOLDER,
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
def send_result_email_task(
    self,
    order_id: str,
    receiver: str,
    archive_path: str,
    results: List[Dict[str, Any]] = None,
):
    """
    Задача отправки письма с архивом размытых изображений.
    Вызывает send_email из mail.py.

    results - результаты задач blur_image_task (передаются автоматически из chord)
    """
    # Создаём архив из результатов задач
    output_paths = [Path(r["dst"]) for r in (results or []) if r and "dst" in r]

    if output_paths:
        archive_name = f"blurred_images_{order_id}.zip"
        archive_path_obj = OUTPUT_FOLDER / archive_name

        with zipfile.ZipFile(archive_path_obj, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in output_paths:
                if p.exists():
                    zf.write(p, arcname=p.name)

        send_email(order_id, receiver, str(archive_path_obj))

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


@celery_app.task(bind=True, name="tasks.send_result_email")
def send_result_email_task(
        self,
        results: List[Dict[str, Any]],
        order_id: str,
        receiver: str,
        archive_path: str = "",
):
    """
    Задача отправки письма с архивом размытых изображений.
    results передаётся автоматически из chord как первый аргумент.
    """
    # Создаём архив из результатов задач
    output_paths = [Path(r["dst"]) for r in (results or []) if r and "dst" in r]

    if output_paths:
        archive_name = f"blurred_images_{order_id}.zip"
        archive_path_obj = OUTPUT_FOLDER / archive_name

        with zipfile.ZipFile(archive_path_obj, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in output_paths:
                if p.exists():
                    zf.write(p, arcname=p.name)

        send_email(order_id, receiver, str(archive_path_obj))

    return {"order_id": order_id, "receiver": receiver, "status": "sent"}


# Инициализация БД при импорте
init_subscribers_db()