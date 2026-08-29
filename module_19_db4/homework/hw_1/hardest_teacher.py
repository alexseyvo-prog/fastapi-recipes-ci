"""
Найти преподавателя с самыми сложными заданиями.
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
    t.teacher_id,
    t.full_name AS teacher_name,
    COUNT(ag.grade_id) AS total_grades,
    ROUND(AVG(ag.grade), 2) AS avg_grade
FROM teachers t
JOIN assignments a ON t.teacher_id = a.teacher_id
JOIN assignments_grades ag ON a.assisgnment_id = ag.assisgnment_id
GROUP BY t.teacher_id, t.full_name
ORDER BY avg_grade ASC;
"""

cursor.execute(query)
results = cursor.fetchall()

print("=== Преподаватели по сложности заданий (от самых сложных к лёгким) ===\n")
print(f"{'ID':<5} {'Преподаватель':<25} {'Оценок':<10} {'Средняя оценка':<15}")
print("-" * 55)

for row in results:
    teacher_id, teacher_name, total_grades, avg_grade = row
    print(f"{teacher_id:<5} {teacher_name:<25} {total_grades:<10} {avg_grade:<15}")

print("\nВывод:")
if results:
    hardest = results[0]
    print(f"Самые сложные задания у преподавателя: {hardest[1]} (ID: {hardest[0]})")
    print(f"Средняя оценка: {hardest[3]}")

conn.close()