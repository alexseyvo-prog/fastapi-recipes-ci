"""
Скрипт для анализа структуры базы данных SQLite.

Выводит:
- Список всех таблиц
- Колонки с типами данных и ограничениями
- Внешние ключи (связи между таблицами)
- Количество записей в каждой таблице
"""

import sqlite3
from pathlib import Path

# Путь к файлу базы данных
db_path = Path("homework.db")

# Проверка существования файла
if not db_path.exists():
    print(f"Файл {db_path} не найден.")
    print("Положите homework.db рядом со скриптом или укажите полный путь.")
    exit(1)

# Подключение к базе данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== СХЕМА БАЗЫ ДАННЫХ ===\n")

# Получение списка всех таблиц в базе
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [row[0] for row in cursor.fetchall()]

# Обход каждой таблицы
for table_name in tables:
    print(f"Таблица: {table_name}")
    print("-" * 40)

    # Получение информации о колонках таблицы
    # Возвращает: (cid, name, type, notnull, default_value, pk)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    print("Колонки:")
    for col in columns:
        cid, name, type_, notnull, default_value, pk = col
        pk_str = " PRIMARY KEY" if pk else ""
        nullable = "NOT NULL" if notnull else "NULL"
        default = f" DEFAULT {default_value}" if default_value is not None else ""
        print(f"  - {name}: {type_} {nullable}{default}{pk_str}")

    # Получение информации о внешних ключах (связях)
    # Возвращает: (id, seq, table, from, to, on_update, on_delete, match)
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    fks = cursor.fetchall()

    if fks:
        print("Внешние ключи (связи):")
        for fk in fks:
            id_, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
            print(f"  - {from_col} → {ref_table}({to_col})")

    # Подсчёт количества записей в таблице
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"Записей: {count}")
    print()

# Закрытие соединения
conn.close()