"""
Flask-приложение сервиса размытия изображений с Celery, Celery Beat и Flower.
"""
import uuid
import zipfile
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, request, jsonify
from celery.result import GroupResult, AsyncResult
from celery import group as celery_group
from celery import chord

from config import (
    UPLOAD_FOLDER,
    OUTPUT_FOLDER,
    SECRET_KEY,
)
from tasks import (
    celery_app,
    blur_image_task,
    send_result_email_task,
    add_subscriber,
    remove_subscriber,
    get_all_subscribers,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


# ==================== Вспомогательные функции ====================


def save_uploaded_files(files) -> List[Path]:
    saved_paths = []
    for file in files:
        if file and file.filename:
            filename = Path(file.filename).name
            save_path = UPLOAD_FOLDER / f"{uuid.uuid4().hex}_{filename}"
            file.save(str(save_path))
            saved_paths.append(save_path)
    return saved_paths


def prepare_output_paths(input_paths: List[Path]) -> List[Path]:
    output_paths = []
    for in_path in input_paths:
        out_name = f"blurred_{in_path.name}"
        out_path = OUTPUT_FOLDER / out_name
        output_paths.append(out_path)
    return output_paths


def create_archive(output_paths: List[Path], archive_path: Path):
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in output_paths:
            if p.exists():
                zf.write(p, arcname=p.name)


# Хранилище метаданных по задачам (в памяти; для продакшена лучше БД/Redis)
task_metadata: Dict[str, Dict[str, Any]] = {}


# ==================== Endpoint'ы ====================


@app.route("/blur", methods=["POST"])
def blur():
    """
    POST /blur
    Принимает:
      - email (form field)
      - images (multiple files)
    Возвращает:
      { "task_id": "<group_id>" }
    """
    email = request.form.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    files = request.files.getlist("images")
    if not files or all(not f.filename for f in files):
        return jsonify({"error": "At least one image is required"}), 400

    input_paths = save_uploaded_files(files)

    output_paths = prepare_output_paths(input_paths)

    # Создаём задачи размытия
    tasks = [
        blur_image_task.s(str(in_p), str(out_p))
        for in_p, out_p in zip(input_paths, output_paths)
    ]

    # Генерируем order_id для архива
    order_id = str(uuid.uuid4())

    # Callback для отправки email (выполнится после завершения всех задач)
    # Порядок аргументов: order_id, email, archive_path (results передаётся автоматически из chord)
    callback = send_result_email_task.s(order_id, email, "")

    # Формируем аккорд: header (группа задач) + callback
    chord_result = chord(tasks)(callback)

    # Сохраняем GroupResult для возможности отслеживания прогресса
    tasks_group = chord_result.parent  # GroupResult по задачам размытия
    tasks_group.save(backend=celery_app.backend)
    group_id = tasks_group.id

    # Сохраняем метаданные для endpoint /status
    task_ids = [r.id for r in tasks_group.results]

    task_metadata[group_id] = {
        "email": email,
        "order_id": order_id,
        "input_paths": input_paths,
        "output_paths": output_paths,
        "task_ids": task_ids,
    }

    return jsonify({"task_id": group_id}), 202


@app.route("/status/<task_id>", methods=["GET"])
def status(task_id: str):
    """
    GET /status/<task_id>
    Возвращает:
      {
        "task_id": "...",
        "total": int,
        "done": int,
        "status": "PENDING" | "IN_PROGRESS" | "DONE"
      }
    """
    if task_id not in task_metadata:
        return jsonify({"error": "Task not found"}), 404

    meta = task_metadata[task_id]
    task_ids = meta.get("task_ids", [])

    # Проверяем статус каждой задачи напрямую через AsyncResult
    results = [AsyncResult(t_id, app=celery_app) for t_id in task_ids]
    total = len(results)
    done = sum(1 for r in results if r.ready())

    if total == 0:
        status_str = "PENDING"
    elif done == total:
        status_str = "DONE"
    else:
        status_str = "IN_PROGRESS"

    return jsonify(
        {
            "task_id": task_id,
            "total": total,
            "done": done,
            "status": status_str,
        }
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    """
    POST /subscribe
    Принимает JSON: { "email": "user@example.com" }
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    added = add_subscriber(email)
    if added:
        return jsonify({"subscribed": True, "message": "Вы успешно подписаны"}), 201
    else:
        return jsonify({"subscribed": True, "message": "Вы уже подписаны"}), 200


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    """
    POST /unsubscribe
    Принимает JSON: { "email": "user@example.com" }
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    removed = remove_subscriber(email)
    if removed:
        return jsonify({"unsubscribed": True, "message": "Вы успешно отписаны"}), 200
    else:
        return jsonify({"unsubscribed": False, "message": "Подписка не найдена"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)