"""
Сервер для задачи «Сортировка логов».

Маршруты:
- / — проверка, что сервер запущен.
- /timestamp/<timestamp> — возвращает дату по Unix-времени.
"""

from datetime import datetime
from typing import Any, Dict, Tuple

from flask import Flask, jsonify


app: Flask = Flask(__name__)


@app.route("/")
def index() -> Dict[str, Any]:
    """
    Проверочный эндпоинт.

    Возвращает JSON-сообщение, что сервер работает.
    """
    return {
        "status": "ok",
        "message": "Server is running",
    }


@app.route("/timestamp/<timestamp>")
def get_timestamp(timestamp: str) -> tuple[str, int] | str:
    """
    Возвращает дату по Unix-времени.

    Args:
        timestamp: Строка с Unix-временем (например, "1549892280").

    Returns:
        Дата в строковом формате, например:
        "2019-02-11 15:38:00".

    Raises:
        400: Если timestamp некорректен.
    """
    try:
        timestamp_value: float = float(timestamp)
    except ValueError:
        # Возвращаем ошибку 400 с пояснением.
        return (
            f"Invalid timestamp: {timestamp!r}",
            400,
        )

    try:
        dt = datetime.fromtimestamp(timestamp_value)
    except (OSError, OverflowError, ValueError):
        # timestamp вне допустимого диапазона.
        return (
            f"Timestamp out of range: {timestamp!r}",
            400,
        )

    # Возвращаем дату в удобочитаемом формате.
    return dt.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # debug=False, чтобы отключить автоперезагрузку
    # и лишние логи в консоль.
    app.run("127.0.0.1", port=8080, debug=False)