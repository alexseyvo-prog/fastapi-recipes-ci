"""
Посчитать среднее, макс и мин количество просроченных заданий для каждого класса.
Вариант с JOIN.
"""

import sqlite3
from pathlib import Path

# Вычисляем путь относительно текущего файла (2 уровня вверх до корня репозитория)
db_path = Path(__file__).resolve().parents[2] / "homework.db"


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
    sg.group_id,
    ROUND(AVG(overdue_count), 2) AS avg_overdue,
    MAX(overdue_count) AS max_overdue,
    MIN(overdue_count) AS min_overdue
FROM students_groups sg
JOIN (
    SELECT 
        s.group_id,
        s.student_id,
        COUNT(ag.grade_id) AS overdue_count
    FROM students s
    JOIN assignments_grades ag ON s.student_id = ag.student_id
    JOIN assignments a ON ag.assisgnment_id = a.assisgnment_id
    WHERE ag.date > a.due_date
    GROUP BY s.group_id, s.student_id
) AS student_overdue ON sg.group_id = student_overdue.group_id
GROUP BY sg.group_id
ORDER BY sg.group_id;
"""

cursor.execute(query)
results = cursor.fetchall()

print("=== Статистика просроченных заданий по классам (JOIN) ===\n")
print(f"{'Класс':<10} {'Среднее':<10} {'Макс':<10} {'Мин':<10}")
print("-" * 45)

for row in results:
    group_id, avg_overdue, max_overdue, min_overdue = row
    print(f"{group_id:<10} {avg_overdue:<10} {max_overdue:<10} {min_overdue:<10}")

conn.close()