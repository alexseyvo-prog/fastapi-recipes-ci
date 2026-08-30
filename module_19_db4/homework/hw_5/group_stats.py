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

# # Вычисляем путь относительно текущего файла (2 уровня вверх до корня репозитория)
# db_path = Path(__file__).resolve().parents[2] / "homework.db"
#
# if not db_path.exists():
#     print(f"Файл не найден: {db_path}")
#     exit(1)
#
# if db_path.stat().st_size == 0:
#     print("Файл пустой — база не инициализирована.")
#     exit(1)
#
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
#
# query = """
# SELECT
#     sg.group_id,
#     COUNT(DISTINCT s.student_id) AS total_students,
#     ROUND(AVG(ag.grade), 2) AS avg_grade,
#     COUNT(DISTINCT CASE
#         WHEN ag.grade IS NULL OR ag.grade = 0 THEN s.student_id
#     END) AS no_submission,
#     COUNT(DISTINCT CASE
#         WHEN ag.date > a.due_date THEN s.student_id
#     END) AS late_submission,
#     COUNT(ag.grade_id) - COUNT(DISTINCT ag.student_id) AS retake_attempts
# FROM students_groups sg
# LEFT JOIN students s ON sg.group_id = s.group_id
# LEFT JOIN assignments_grades ag ON s.student_id = ag.student_id
# LEFT JOIN assignments a ON ag.assisgnment_id = a.assisgnment_id
# GROUP BY sg.group_id
# ORDER BY sg.group_id;
# """
#
# cursor.execute(query)
# results = cursor.fetchall()
#
# print("=== Полная статистика по группам ===\n")
# print(f"{'Группа':<10} {'Учеников':<10} {'Ср. оценка':<12} {'Не сдали':<10} {'Опоздали':<10} {'Повторы':<10}")
# print("-" * 70)
#
# for row in results:
#     group_id, total_students, avg_grade, no_submission, late_submission, retake_attempts = row
#     print(f"{group_id:<10} {total_students:<10} {avg_grade:<12} {no_submission:<10} {late_submission:<10} {retake_attempts:<10}")
#
# conn.close()

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

print("=== Полная статистика по группам ===\n")

# 1. Количество учеников в каждой группе
query_students = """
SELECT 
    sg.group_id,
    COUNT(s.student_id) AS total_students
FROM students_groups sg
LEFT JOIN students s ON sg.group_id = s.group_id
GROUP BY sg.group_id
ORDER BY sg.group_id;
"""

cursor.execute(query_students)
students_data = {row[0]: row[1] for row in cursor.fetchall()}

# 2. Средняя оценка по группе
query_avg_grade = """
SELECT 
    s.group_id,
    ROUND(AVG(ag.grade), 2) AS avg_grade
FROM students s
JOIN assignments_grades ag ON s.student_id = ag.student_id
GROUP BY s.group_id
ORDER BY s.group_id;
"""

cursor.execute(query_avg_grade)
avg_grade_data = {row[0]: row[1] for row in cursor.fetchall()}

# 3. Сколько не сдали работы (нет записи в assignments_grades хотя бы по одному заданию)
query_no_submission = """
SELECT 
    s.group_id,
    COUNT(DISTINCT s.student_id) AS no_submission
FROM students s
WHERE s.student_id NOT IN (
    SELECT DISTINCT student_id FROM assignments_grades
)
GROUP BY s.group_id
ORDER BY s.group_id;
"""

cursor.execute(query_no_submission)
no_submission_data = {row[0]: row[1] for row in cursor.fetchall()}

# 4. Сколько опоздали со сдачей (хотя бы одна работа сдана после due_date)
query_late_submission = """
SELECT 
    s.group_id,
    COUNT(DISTINCT s.student_id) AS late_submission
FROM students s
JOIN assignments_grades ag ON s.student_id = ag.student_id
JOIN assignments a ON ag.assisgnment_id = a.assisgnment_id
WHERE ag.date > a.due_date
GROUP BY s.group_id
ORDER BY s.group_id;
"""

cursor.execute(query_late_submission)
late_submission_data = {row[0]: row[1] for row in cursor.fetchall()}

# 5. Количество повторных попыток (дубли по student_id + assignment_id)
query_retakes = """
SELECT 
    s.group_id,
    COUNT(*) AS retake_attempts
FROM students s
JOIN assignments_grades ag ON s.student_id = ag.student_id
JOIN (
    SELECT student_id, assisgnment_id
    FROM assignments_grades
    GROUP BY student_id, assisgnment_id
    HAVING COUNT(*) > 1
) duplicates ON ag.student_id = duplicates.student_id 
    AND ag.assisgnment_id = duplicates.assisgnment_id
GROUP BY s.group_id
ORDER BY s.group_id;
"""

cursor.execute(query_retakes)
retakes_data = {row[0]: row[1] for row in cursor.fetchall()}

# Вывод сводной таблицы
print(f"{'Группа':<10} {'Учеников':<10} {'Ср. оценка':<12} {'Не сдали':<10} {'Опоздали':<10} {'Повторы':<10}")
print("-" * 70)

all_group_ids = sorted(set(students_data.keys()))

for group_id in all_group_ids:
    total_students = students_data.get(group_id, 0)
    avg_grade = avg_grade_data.get(group_id, 0)
    no_submission = no_submission_data.get(group_id, 0)
    late_submission = late_submission_data.get(group_id, 0)
    retake_attempts = retakes_data.get(group_id, 0)

    print(
        f"{group_id:<10} {total_students:<10} {avg_grade:<12} {no_submission:<10} {late_submission:<10} {retake_attempts:<10}")

conn.close()