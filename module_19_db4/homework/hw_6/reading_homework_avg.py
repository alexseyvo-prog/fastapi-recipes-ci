"""
Средняя оценка заданий, где ученикам нужно было что-то прочитать и выучить.
Используя подзапросы.
"""

import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Администратор\Desktop\PY\M3\python_advanced\module_19_db4\homework.db")

if not db_path.exists():
    print(f"Файл не найден: {db_path}")
    exit(1)

if db_path.stat().st_size == 0:
    print("Файл пустой — база не инициализирована.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """
SELECT 
    ROUND(AVG(grade), 2) AS avg_grade
FROM assignments_grades
WHERE assisgnment_id IN (
    SELECT assisgnment_id
    FROM assignments
    WHERE assignment_text LIKE '%прочитать%'
       OR assignment_text LIKE '%выучить%'
       OR assignment_text LIKE '%read%'
       OR assignment_text LIKE '%learn%'
);
"""

cursor.execute(query)
result = cursor.fetchone()

print("=== Средняя оценка заданий на чтение и заучивание ===\n")
print(f"Средняя оценка: {result[0]}")

conn.close()