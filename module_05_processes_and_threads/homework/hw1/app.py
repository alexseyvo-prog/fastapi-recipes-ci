"""
Консольная утилита lsof (List Open Files) выводит информацию о том, какие файлы используют какие-либо процессы.
Эта команда может рассказать много интересного, так как в Unix-подобных системах всё является файлом.

Но нам пока нужна лишь одна из её возможностей.
Запуск lsof -i :port выдаст список процессов, занимающих введённый порт.
Например, lsof -i :5000.

Функция ниже:
- получает порт,
- находит процессы, которые его занимают (через lsof),
- завершает их,
- запускает Flask-сервер на этом порту.
"""

from typing import List

import os
import signal

from flask import Flask
import psutil  # новый импорт


app = Flask(__name__)


def get_pids(port: int) -> List[int]:
    """
    Возвращает список PID процессов, занимающих переданный порт.
    Работает под Windows и Unix с помощью psutil.
    """
    if not isinstance(port, int):
        raise ValueError("port must be int")

    pids: List[int] = []

    # Перебираем все TCP-соединения и ищем те, что слушают этот порт
    for conn in psutil.net_connections(kind="inet"):
        laddr = conn.laddr
        if not laddr:
            continue

        # laddr.port == порт, статус LISTEN, у соединения есть pid
        if laddr.port == port and conn.pid is not None:
            if conn.pid not in pids:
                pids.append(conn.pid)

    return pids


def free_port(port: int) -> None:
    """
    Завершает процессы, занимающие переданный порт.
    """
    pids: List[int] = get_pids(port)

    for pid in pids:
        try:
            # На Windows SIGTERM интерпретируется как «нормальное завершение» процесса
            os.kill(pid, signal.SIGTERM)
            print(f"Отправлен SIGTERM процессу PID={pid}, занимавшему порт {port}")
        except ProcessLookupError:
            print(f"Процесс PID={pid} уже не существует")
        except PermissionError:
            print(f"Нет прав завершить процесс PID={pid}")


def run(port: int) -> None:
    """
    Запускает flask-приложение по переданному порту.
    Если порт занят каким-либо процессом, завершает его.
    """
    free_port(port)
    app.run(port=port)


if __name__ == '__main__':
    run(5000)