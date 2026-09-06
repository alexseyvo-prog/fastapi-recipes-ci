from sqlalchemy import create_engine, event
from pathlib import Path
from models import Base, Author, Book, Student, ReceivingBook, set_sqlite_pragma
from datetime import date, datetime

db_path = Path(__file__).parent / "library.db"
engine = create_engine(f'sqlite:///{db_path}', echo=False)

# Включение внешних ключей SQLite
event.listen(engine, "connect", set_sqlite_pragma)

# Создать все таблицы
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

try:
    if session.query(Book).count() == 0:
        # Авторы
        authors = [
            Author(name='Лев', surname='Толстой'),
            Author(name='Фёдор', surname='Достоевский'),
            Author(name='Михаил', surname='Булгаков'),
        ]

        # Книги
        books = [
            Book(name='Война и мир', count=2, release_date=date(1869, 1, 1), author_id=1),
            Book(name='Преступление и наказание', count=1, release_date=date(1866, 1, 1), author_id=2),
            Book(name='Мастер и Маргарита', count=3, release_date=date(1967, 1, 1), author_id=3),
        ]

        # Студенты
        students = [
            Student(
                name='Иван',
                surname='Иванов',
                phone='+79001112233',
                email='ivanov@test.com',
                average_score=4.5,
                scholarship=True,
            ),
            Student(
                name='Пётр',
                surname='Петров',
                phone='+79004445566',
                email='petrov@test.com',
                average_score=3.8,
                scholarship=False,
            ),
            Student(
                name='Сидор',
                surname='Сидоров',
                phone='+79007778899',
                email='sidorov@test.com',
                average_score=4.9,
                scholarship=True,
            ),
        ]

        # Добавляем авторов
        for author in authors:
            session.add(author)
        session.commit()

        # Добавляем книги
        for book in books:
            session.add(book)
        session.commit()

        # Добавляем студентов
        for student in students:
            session.add(student)
        session.commit()

        # Пример выдачи книги
        receiving = ReceivingBook(
            book_id=1,
            student_id=1,
            date_of_issue=datetime.now(),
            date_of_return=None
        )
        session.add(receiving)

        # Уменьшаем количество доступных экземпляров
        book = session.query(Book).filter_by(id=1).first()
        if book:
            book.count -= 1

        session.commit()
        print("База данных инициализирована.")
    else:
        print("База данных уже содержит данные.")
finally:
    session.close()