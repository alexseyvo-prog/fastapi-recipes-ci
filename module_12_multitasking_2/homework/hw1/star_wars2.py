"""
Загрузка 20 персонажей из SWAPI.

Программа выполняет две версии загрузки:
1. Параллельные HTTP-запросы с использованием процессов (multiprocessing.Pool).
2. Параллельные HTTP-запросы с использованием потоков (ThreadPoolExecutor).

Для каждого персонажа сохраняются:
- имя;
- возраст / birth_year;
- пол.

Результаты сохраняются в SQLite-базу star_wars.db.
"""


import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from typing import Any, Dict, List

import requests


API_URL = "https://www.swapi.tech/api/people"
DATABASE_NAME = "star_wars.db"
CHARACTER_IDS = [
    *range(1, 17),
    *range(18, 22),
]


def get_character(character_id: int) -> Dict[str, Any]:
    """
    Загружает одного персонажа из SWAPI.

    Args:
        character_id: Номер персонажа в API.

    Returns:
        Словарь с именем, возрастом и полом персонажа.

    Raises:
        requests.HTTPError: Если сервер вернул ошибку.
        KeyError: Если в ответе отсутствуют нужные поля.
    """
    url = f"{API_URL}/{character_id}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    properties = data["result"]["properties"]

    return {
        "name": properties["name"],
        "age": properties.get("birth_year"),
        "gender": properties.get("gender"),
    }


def get_characters_with_processes() -> List[Dict[str, Any]]:
    """
    Параллельно загружает персонажей с использованием
    пула процессов (multiprocessing.Pool).
    """
    # Количество процессов можно менять.
    # Обычно берут cpu_count() или немного больше.
    with Pool(processes=cpu_count()) as pool:
        characters = pool.map(
            get_character,
            CHARACTER_IDS,
        )

    return characters


def get_characters_with_threads() -> List[Dict[str, Any]]:
    """
    Параллельно загружает персонажей с использованием
    пула потоков (ThreadPoolExecutor).
    """
    # Количество потоков для I/O-задач можно ставить больше cpu_count.
    with ThreadPoolExecutor(max_workers=20) as executor:
        characters = list(
            executor.map(
                get_character,
                CHARACTER_IDS,
            )
        )

    return characters


def save_characters_to_database(
    characters: List[Dict[str, Any]],
) -> None:
    """
    Сохраняет персонажей в SQLite-базу.

    Если персонаж с таким именем уже существует,
    его данные обновляются.

    Args:
        characters: Список персонажей для сохранения.
    """
    with sqlite3.connect(DATABASE_NAME) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                age TEXT,
                gender TEXT
            )
        """)

        cursor.executemany("""
            INSERT OR REPLACE INTO characters
                (name, age, gender)
            VALUES (?, ?, ?)
        """, [
            (
                character["name"],
                character["age"],
                character["gender"],
            )
            for character in characters
        ])

        connection.commit()


def print_characters(
    characters: List[Dict[str, Any]],
) -> None:
    """
    Выводит загруженных персонажей в консоль.

    Args:
        characters: Список персонажей.
    """
    for character in characters:
        print(
            f"{character['name']} | "
            f"{character['age']} | "
            f"{character['gender']}"
        )


def main() -> None:
    """
    Запускает загрузку через процессы и потоки,
    измеряет время и сохраняет результат в базу.
    """
    print("Загрузка с использованием процессов (multiprocessing.Pool)")

    start_time = time.perf_counter()

    process_characters = get_characters_with_processes()

    process_time = time.perf_counter() - start_time

    print(
        f"Время загрузки (процессы): "
        f"{process_time:.2f} секунд"
    )

    print_characters(process_characters)

    save_characters_to_database(process_characters)

    print()
    print("Загрузка с использованием потоков (ThreadPoolExecutor)")

    start_time = time.perf_counter()

    thread_characters = get_characters_with_threads()

    thread_time = time.perf_counter() - start_time

    print(
        f"Время загрузки (потоки): "
        f"{thread_time:.2f} секунд"
    )

    print_characters(thread_characters)

    save_characters_to_database(thread_characters)

    print()
    print("Сравнение:")

    if thread_time < process_time:
        print("Потоковая загрузка работает быстрее.")
    elif thread_time > process_time:
        print("Процессорная загрузка работает быстрее.")
    else:
        print("Время выполнения примерно одинаковое.")


if __name__ == "__main__":
    main()