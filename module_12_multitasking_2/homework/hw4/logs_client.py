"""
Клиент для задачи «Сортировка логов».

- 10 потоков запускаются последовательно с интервалом 1 секунда.
- Каждый поток работает 20 секунд.
- Раз в секунду поток:
    - получает текущий timestamp;
    - делает запрос к http://127.0.0.1:8080/timestamp/<timestamp>;
    - кладёт строку "<timestamp> <дата>" в общую очередь.
- Отдельный поток-писатель записывает логи в файл.
- После завершения всех потоков логи сортируются по timestamp
  и перезаписываются в итоговый файл.
"""

import threading
import time
from datetime import datetime
from queue import Queue, Empty
from typing import List

import requests


LOG_FILE = "logs_raw.txt"
SORTED_LOG_FILE = "logs_sorted.txt"
SERVER_URL = "http://127.0.0.1:8080/timestamp"

NUM_WORKERS = 10
WORKER_DURATION = 20  # секунд
WORK_INTERVAL = 1     # секунда


log_queue: Queue[str] = Queue()
stop_writer = threading.Event()


def worker(worker_id: int) -> None:
    """
    Рабочий поток.

    Каждую секунду в течение WORKER_DURATION:
    - получает текущий timestamp;
    - делает запрос к серверу;
    - кладёт строку "<timestamp> <дата>" в очередь.
    """
    start_time = time.time()

    while time.time() - start_time < WORKER_DURATION:
        # Получаем текущий timestamp непосредственно перед запросом.
        current_timestamp = int(time.time())

        url = f"{SERVER_URL}/{current_timestamp}"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            date_str = response.text.strip()
        except Exception:
            # Если сервер недоступен, используем локальное время.
            date_str = datetime.fromtimestamp(
                current_timestamp
            ).isoformat()

        log_entry = f"{current_timestamp} {date_str}"

        log_queue.put(log_entry)

        # Ждём интервал перед следующей итерацией.
        time.sleep(WORK_INTERVAL)


def writer_thread_func() -> None:
    """
    Поток-писатель.

    Читает строки из очереди и записывает их в файл
    до тех пор, пока не будет установлено событие stop_writer
    и очередь не опустеет.
    """
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        while True:
            try:
                # Ждём элемент из очереди с небольшим таймаутом.
                entry = log_queue.get(timeout=0.5)
                f.write(entry + "\n")
                f.flush()
                log_queue.task_done()
            except Empty:
                # Если очередь пуста и сигнал остановки установлен,
                # завершаем поток-писатель.
                if stop_writer.is_set():
                    break


def main() -> None:
    """
    Запускает 10 рабочих потоков и поток-писатель.
    После завершения всех потоков сортирует логи по timestamp
    и записывает в итоговый файл.
    """
    # Запускаем поток-писатель.
    writer_thread = threading.Thread(target=writer_thread_func)
    writer_thread.start()

    workers: List[threading.Thread] = []

    # Запускаем 10 рабочих потоков последовательно
    # с интервалом 1 секунда.
    for i in range(NUM_WORKERS):
        worker_thread = threading.Thread(
            target=worker,
            args=(i,),
        )
        worker_thread.start()
        workers.append(worker_thread)

        # Ждём 1 секунду перед запуском следующего потока.
        if i < NUM_WORKERS - 1:
            time.sleep(1)

    # Ждём завершения всех рабочих потоков.
    for w in workers:
        w.join()

    # Даём время обработать оставшиеся записи в очереди.
    log_queue.join()

    # Сигнализируем потоку-писателю о завершении.
    stop_writer.set()
    writer_thread.join()

    # Сортируем логи по timestamp.
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Сортируем по первому полю (timestamp).
    lines.sort(key=lambda line: int(line.split()[0]))

    with open(SORTED_LOG_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"Логи записаны в {LOG_FILE}")
    print(f"Отсортированные логи записаны в {SORTED_LOG_FILE}")


if __name__ == "__main__":
    main()