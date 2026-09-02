# init_db.py
from sqlalchemy import create_engine
from pathlib import Path
from models import Base, Author, Book, Student, ReceivingBook
from datetime import date, datetime

db_path = Path(__file__).parent / "library.db"
engine = create_engine(f'sqlite:///{db_path}')

# Создать все таблицы
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Проверить, есть ли уже данные
if session.query(Book).count() == 0:
    # Авторы
    authors = [
        Author(name='Лев', surname='Толстой'),
        Author(name='Фёдор', surname='Достоевский'),
        Author(name='Михаил', surname='Булгаков'),
    ]

    # Книги (count - количество экземпляров)
    books = [
        Book(name='Война и мир', count=2, release_date=date(1869, 1, 1), author_id=1),
        Book(name='Преступление и наказание', count=1, release_date=date(1866, 1, 1), author_id=2),
        Book(name='Мастер и Маргарита', count=3, release_date=date(1967, 1, 1), author_id=3),
    ]

    # Студенты
    students = [
        Student(name='Иван', surname='Иванов', phone='+79001112233', email='ivanov@test.com', average_score=4.5, scholarship=True, dormitory=101),
        Student(name='Пётр', surname='Петров', phone='+79004445566', email='petrov@test.com', average_score=3.8, scholarship=False, dormitory=102),
        Student(name='Сидор', surname='Сидоров', phone='+79007778899', email='sidorov@test.com', average_score=4.9, scholarship=True, dormitory=None),
    ]

    for a in authors:
        session.add(a)
    for b in books:
        session.add(b)
    for s in students:
        session.add(s)

    session.commit()
    print("База данных инициализирована.")
else:
    print("База данных уже содержит данные.")

session.close()