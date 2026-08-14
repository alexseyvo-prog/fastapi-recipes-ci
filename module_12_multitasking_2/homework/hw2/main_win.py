"""
Анализ процессов для Windows.

Функции:
- process_count(username) — количество процессов пользователя.
- total_memory_usage(root_pid) — суммарное потребление памяти
  древа процессов с корнем root_pid в процентах.

Для работы требуются стандартные утилиты Windows:
- tasklist
- wmic
"""

import subprocess
from typing import List


def run_command(command: List[str]) -> str:
    """
    Выполняет системную команду и возвращает её вывод.

    Args:
        command: Список аргументов команды.

    Returns:
        Строка с выводом команды (stdout).

    Raises:
        subprocess.CalledProcessError: Если команда вернула ошибку.
    """
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    return result.stdout


def process_count(username: str) -> int:
    """
    Возвращает количество процессов, запущенных
    от имени указанного пользователя.

    Args:
        username: Имя пользователя в системе.

    Returns:
        Количество процессов (int).
    """
    # tasklist /FI "USERNAME eq username" /FO CSV /NH
    # выводит процессы пользователя в формате CSV без заголовка.
    output = run_command(
        [
            "tasklist",
            "/FI", f"USERNAME eq {username}",
            "/FO", "CSV",
            "/NH",
        ]
    )

    # Каждая строка — один процесс.
    lines = [
        line
        for line in output.strip().splitlines()
        if line.strip()
    ]

    return len(lines)


def get_children_pids(root_pid: int) -> List[int]:
    """
    Рекурсивно собирает все PID потомков процесса.

    Args:
        root_pid: PID корневого процесса.

    Returns:
        Список всех PID (включая корневой).
    """
    # wmic process where "ParentProcessId=PID" get ProcessId
    # возвращает PID прямых потомков.
    output = run_command(
        [
            "wmic",
            "process",
            "where",
            f"ParentProcessId={root_pid}",
            "get",
            "ProcessId",
        ]
    )

    children = []

    for line in output.strip().splitlines():
        line = line.strip()

        # Пропускаем заголовок "ProcessId" и пустые строки.
        if not line or line == "ProcessId":
            continue

        try:
            child_pid = int(line)
        except ValueError:
            continue

        children.append(child_pid)

        # Рекурсивно добавляем потомков потомка.
        children.extend(
            get_children_pids(child_pid)
        )

    # Возвращаем корневой PID плюс все потомки.
    return [root_pid] + children


def total_memory_usage(root_pid: int) -> float:
    """
    Возвращает суммарное потребление памяти древа процессов
    с корнем root_pid в процентах.

    Для Windows считаем процент от общей физической памяти.

    Args:
        root_pid: PID корневого процесса.

    Returns:
        Суммарный процент использования памяти (float).
    """
    import psutil

    # Получаем все PID древа процессов.
    all_pids = get_children_pids(root_pid)

    if not all_pids:
        return 0.0

    total_bytes = 0

    for pid in all_pids:
        try:
            process = psutil.Process(pid)
            mem_info = process.memory_info()
            total_bytes += mem_info.rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Процесс мог завершиться или нет доступа.
            continue

    # Общая физическая память системы.
    total_physical_memory = psutil.virtual_memory().total

    if total_physical_memory == 0:
        return 0.0

    percent = (total_bytes / total_physical_memory) * 100

    return percent


if __name__ == "__main__":
    import getpass

    current_user = getpass.getuser()

    count = process_count(current_user)

    print(
        f"Количество процессов пользователя "
        f"'{current_user}': {count}"
    )

    # Пример: потребление памяти древа процесса с PID 4 (System).
    root_pid_example = 4

    memory = total_memory_usage(root_pid_example)

    print(
        f"Суммарное потребление памяти древа "
        f"с корнем PID {root_pid_example}: {memory:.2f}%"
    )