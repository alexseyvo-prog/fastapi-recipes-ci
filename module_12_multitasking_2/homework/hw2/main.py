"""
Анализ процессов.

Функции:
- process_count(username) — количество процессов пользователя.
- total_memory_usage(root_pid) — суммарное потребление памяти
  древа процессов с корнем root_pid в процентах.

Для работы требуются утилиты:
- ps
- pgrep
- wc
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
    # pgrep -u username возвращает PID процессов пользователя,
    # по одному в строке.
    # wc -l считает количество строк.
    output = run_command(
        ["pgrep", "-u", username]
    )

    # Считаем количество строк в выводе.
    # Каждая строка — один PID.
    lines = output.strip().splitlines()

    return len(lines)


def get_children_pids(root_pid: int) -> List[int]:
    """
    Рекурсивно собирает все PID потомков процесса.

    Args:
        root_pid: PID корневого процесса.

    Returns:
        Список всех PID (включая корневой).
    """
    # Получаем прямых потомков через ps --ppid.
    output = run_command(
        ["ps", "-o", "pid", "--no-headers", "--ppid", str(root_pid)]
    )

    children = []

    for line in output.strip().splitlines():
        if not line.strip():
            continue

        child_pid = int(line.strip())
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

    Args:
        root_pid: PID корневого процесса.

    Returns:
        Суммарный процент использования памяти (float).
    """
    # Получаем все PID древа процессов.
    all_pids = get_children_pids(root_pid)

    if not all_pids:
        return 0.0

    # Формируем список PID для ps.
    pid_list = [str(pid) for pid in all_pids]

    # ps -o %mem --no-headers -p PID1,PID2,...
    # возвращает процент памяти для каждого процесса.
    output = run_command(
        ["ps", "-o", "%mem", "--no-headers", "-p", ",".join(pid_list)]
    )

    total = 0.0

    for line in output.strip().splitlines():
        if not line.strip():
            continue

        percent = float(line.strip())
        total += percent

    return total


if __name__ == "__main__":
    import getpass

    current_user = getpass.getuser()

    count = process_count(current_user)

    print(
        f"Количество процессов пользователя "
        f"'{current_user}': {count}"
    )

    # Пример: потребление памяти древа процесса с PID 1.
    root_pid_example = 1

    memory = total_memory_usage(root_pid_example)

    print(
        f"Суммарное потребление памяти древа "
        f"с корнем PID {root_pid_example}: {memory:.2f}%"
    )