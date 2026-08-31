# test_queries.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from models import Base, Student, Book, ReceivingBook

# Путь к базе данных
db_path = Path(__file__).parent / "library.db"
engine = create_engine(f'sqlite:///{db_path}')

Session = sessionmaker(bind=engine)
session = Session()

print("=== 1. Все книги ===")
books = session.query(Book).all()
for book in books:
    print(f"  {book.book_id}: {book.title} ({book.author}, {book.year})")

print("\n=== 2. Все студенты ===")
students = session.query(Student).all()
for s in students:
    print(f"  {s.student_id}: {s.name} (GPA: {s.gpa}, Общежитие: {s.dormitory})")

print("\n=== 3. Студенты с общежитием (classmethod) ===")
students_with_dorm = Student.with_dormitory(session)
for s in students_with_dorm:
    print(f"  {s.student_id}: {s.name} (Общежитие: {s.dormitory})")

print("\n=== 4. Студенты с GPA > 4.0 (classmethod) ===")
high_gpa_students = Student.with_gpa_above(session, 4.0)
for s in high_gpa_students:
    print(f"  {s.student_id}: {s.name} (GPA: {s.gpa})")

print("\n=== 5. Все выдачи книг ===")
receiving = session.query(ReceivingBook).all()
for r in receiving:
    status = "сдана" if r.date_return else "не сдана"
    print(f"  ID: {r.id}, Студент: {r.student_id}, Книга: {r.book_id}, "
          f"Дней: {r.count_date_with_book}, Статус: {status}")

print("\n=== 6. Должники (> 14 дней) ===")
debtors = session.query(ReceivingBook).filter(
    ReceivingBook.date_return.is_(None)
).all()
for r in debtors:
    if r.count_date_with_book > 14:
        student = session.query(Student).filter_by(student_id=r.student_id).first()
        book = session.query(Book).filter_by(book_id=r.book_id).first()
        print(f"  {student.name} держит '{book.title}' уже {r.count_date_with_book} дней")

print("\n=== 7. Поиск книг по названию (мир) ===")
search_query = "мир"
found_books = session.query(Book).filter(
    Book.title.ilike(f'%{search_query}%')
).all()
for book in found_books:
    print(f"  {book.book_id}: {book.title} ({book.author})")

session.close()