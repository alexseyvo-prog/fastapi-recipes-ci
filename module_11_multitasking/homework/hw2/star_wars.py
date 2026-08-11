"""
Загрузка 20 персонажей из SWAPI.

Программа выполняет две версии загрузки:
1. Последовательные HTTP-запросы.
2. Параллельные HTTP-запросы с использованием потоков.

Для каждого персонажа сохраняются:
- имя;
- возраст / birth_year;
- пол.

Результаты сохраняются в SQLite-базу star_wars.db.
"""


import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
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


def get_characters_sequential() -> List[Dict[str, Any]]:
    """
    Последовательно загружает 20 существующих персонажей.
    """
    characters = []

    for character_id in CHARACTER_IDS:
        character = get_character(character_id)
        characters.append(character)

    return characters


def get_characters_parallel() -> List[Dict[str, Any]]:
    """
    Параллельно загружает 20 существующих персонажей
    с использованием потоков.
    """
    with ThreadPoolExecutor(max_workers=10) as executor:
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

        # Создаём таблицу, если она ещё не существует.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                age TEXT,
                gender TEXT
            )
        """)

        # INSERT OR REPLACE позволяет повторно запустить программу
        # без появления дубликатов по имени персонажа.
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
    Запускает последовательную и параллельную загрузку,
    измеряет время и сохраняет результат в базу.
    """
    print("Последовательная загрузка")

    start_time = time.perf_counter()

    sequential_characters = get_characters_sequential()

    sequential_time = time.perf_counter() - start_time

    print(
        f"Время последовательной загрузки: "
        f"{sequential_time:.2f} секунд"
    )

    print_characters(sequential_characters)

    # Сохраняем результат последовательной загрузки.
    save_characters_to_database(sequential_characters)

    print()
    print("Параллельная загрузка")

    start_time = time.perf_counter()

    parallel_characters = get_characters_parallel()

    parallel_time = time.perf_counter() - start_time

    print(
        f"Время параллельной загрузки: "
        f"{parallel_time:.2f} секунд"
    )

    print_characters(parallel_characters)

    # Сохраняем результат параллельной загрузки.
    save_characters_to_database(parallel_characters)

    print()
    print("Сравнение:")

    if parallel_time < sequential_time:
        print("Параллельная загрузка работает быстрее.")
    elif parallel_time > sequential_time:
        print("Последовательная загрузка работает быстрее.")
    else:
        print("Время выполнения одинаковое.")


if __name__ == "__main__":
    main()