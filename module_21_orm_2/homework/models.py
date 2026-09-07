from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Table, event
)
from sqlalchemy.orm import (
    declarative_base, relationship, joinedload, selectinload, subqueryload
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    # Жадная подгрузка книг через joinedload
    books = relationship(
        'Book',
        back_populates='author',
        cascade='all, delete-orphan',
        lazy='joined'
    )


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    count = Column(Integer, default=1)
    release_date = Column(Date, nullable=False)

    # Внешний ключ на автора
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)

    # Связь с автором
    author = relationship('Author', back_populates='books')

    # MANY-TO-MANY со студентами через receiving_books
    students = relationship(
        'Student',
        secondary='receiving_books',
        back_populates='books',
        viewonly=True
    )

    # Жадная подгрузка выдач через selectinload
    receivings = relationship(
        'ReceivingBook',
        back_populates='book',
        cascade='all, delete-orphan',
        lazy='selectin'
    )


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    average_score = Column(Float, nullable=False)
    scholarship = Column(Boolean, nullable=False)

    # MANY-TO-MANY с книгами через receiving_books
    books = relationship(
        'Book',
        secondary='receiving_books',
        back_populates='students',
        viewonly=True
    )

    # Жадная подгрузка выдач через subqueryload
    receivings = relationship(
        'ReceivingBook',
        back_populates='student',
        cascade='all, delete-orphan',
        lazy='subquery'
    )

    @classmethod
    def with_dormitory(cls, session):
        """Получить список студентов, у которых есть общежитие."""
        return session.query(cls).filter(cls.dormitory.isnot(None)).all()

    @classmethod
    def with_average_score_above(cls, session, score_threshold):
        """Получить список студентов со средним баллом выше порога."""
        return session.query(cls).filter(cls.average_score > score_threshold).all()


class ReceivingBook(Base):
    __tablename__ = 'receiving_books'

    id = Column(Integer, primary_key=True)

    # Внешние ключи
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)

    date_of_issue = Column(DateTime, nullable=False)
    date_of_return = Column(DateTime, nullable=True)

    # Связи
    book = relationship('Book', back_populates='receivings')
    student = relationship('Student', back_populates='receivings')

    @hybrid_property
    def count_date_with_book(self):
        """Количество дней, которое читатель держит книгу."""
        if self.date_of_return is None:
            return (datetime.now() - self.date_of_issue).days
        return (self.date_of_return - self.date_of_issue).days


# Включение поддержки внешних ключей в SQLite
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()