from pathlib import Path
import sqlite3

db_path = Path.cwd() / "library.db"
sql_path = Path.cwd().parent / "materials" / "db.sql"

with sqlite3.connect(db_path) as connection:
    sql_script = sql_path.read_text(encoding="utf-8")
    connection.executescript(sql_script)

print("Триггер добавлен в library.db")