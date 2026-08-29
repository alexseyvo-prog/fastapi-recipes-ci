"""
Выбрать 10 лучших учеников по среднему баллу.
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
    s.student_id,
    s.full_name AS student_name,
    s.group_id,
    COUNT(ag.grade_id) AS total_grades,
    ROUND(AVG(ag.grade), 2) AS avg_grade
FROM students s
JOIN assignments_grades ag ON s.student_id = ag.student_id
GROUP BY s.student_id, s.full_name, s.group_id
ORDER BY avg_grade DESC
LIMIT 10;
"""

cursor.execute(query)
results = cursor.fetchall()

print("=== 10 лучших учеников по среднему баллу ===\n")
print(f"{'ID':<5} {'ФИО':<25} {'Группа':<10} {'Оценок':<10} {'Средний балл':<12}")
print("-" * 65)

for row in results:
    student_id, student_name, group_id, total_grades, avg_grade = row
    print(f"{student_id:<5} {student_name:<25} {group_id:<10} {total_grades:<10} {avg_grade:<12}")

conn.close()