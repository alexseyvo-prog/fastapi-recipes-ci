"""
Найти всех учеников преподавателя с самыми простыми заданиями.
Вариант с JOIN.
"""

import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Администратор\Desktop\PY\M3\python_advanced\module_19_db4\homework.db")

if not db_path.exists():
    print(f"Файл не найден: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """
SELECT DISTINCT
    s.student_id,
    s.full_name,
    s.group_id
FROM students s
JOIN students_groups sg ON s.group_id = sg.group_id
JOIN teachers t ON sg.teacher_id = t.teacher_id
JOIN (
    SELECT 
        a.teacher_id,
        ROUND(AVG(ag.grade), 2) AS avg_grade
    FROM assignments a
    JOIN assignments_grades ag ON a.assisgnment_id = ag.assisgnment_id
    GROUP BY a.teacher_id
    ORDER BY avg_grade DESC
    LIMIT 1
) best_teacher ON t.teacher_id = best_teacher.teacher_id;
"""

cursor.execute(query)
results = cursor.fetchall()

print("=== Ученики преподавателя с самыми простыми заданиями (JOIN) ===\n")
print(f"{'ID':<5} {'ФИО':<25} {'Группа':<10}")
print("-" * 45)

for row in results:
    student_id, full_name, group_id = row
    print(f"{student_id:<5} {full_name:<25} {group_id:<10}")

print(f"\nВсего учеников: {len(results)}")

conn.close()