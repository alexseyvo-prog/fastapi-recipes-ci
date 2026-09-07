from pathlib import Path
import sqlite3

db_path = Path.cwd() / "library.db"

with sqlite3.connect(db_path) as connection:
    triggers = connection.execute("""
        SELECT name FROM sqlite_master WHERE type = 'trigger';
    """).fetchall()

if triggers:
    print("Триггеры найдены:")
    for (name,) in triggers:
        print(f"  - {name}")
else:
    print("Триггеров нет в этой базе.")
