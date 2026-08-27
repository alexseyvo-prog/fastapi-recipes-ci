"""
Полная статистика по группам:
- Количество учеников
- Средняя оценка
- Сколько не сдали работы
- Сколько опоздали со сдачей
- Количество повторных попыток
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
    sg.group_id,
    COUNT(DISTINCT s.student_id) AS total_students,
    ROUND(AVG(ag.grade), 2) AS avg_grade,
    COUNT(DISTINCT CASE 
        WHEN ag.grade IS NULL OR ag.grade = 0 THEN s.student_id 
    END) AS no_submission,
    COUNT(DISTINCT CASE 
        WHEN ag.date > a.due_date THEN s.student_id 
    END) AS late_submission,
    COUNT(ag.grade_id) - COUNT(DISTINCT ag.student_id) AS retake_attempts
FROM students_groups sg
LEFT JOIN students s ON sg.group_id = s.group_id
LEFT JOIN assignments_grades ag ON s.student_id = ag.student_id
LEFT JOIN assignments a ON ag.assisgnment_id = a.assisgnment_id
GROUP BY sg.group_id
ORDER BY sg.group_id;
"""

cursor.execute(query)
results = cursor.fetchall()

print("=== Полная статистика по группам ===\n")
print(f"{'Группа':<10} {'Учеников':<10} {'Ср. оценка':<12} {'Не сдали':<10} {'Опоздали':<10} {'Повторы':<10}")
print("-" * 70)

for row in results:
    group_id, total_students, avg_grade, no_submission, late_submission, retake_attempts = row
    print(f"{group_id:<10} {total_students:<10} {avg_grade:<12} {no_submission:<10} {late_submission:<10} {retake_attempts:<10}")

conn.close()