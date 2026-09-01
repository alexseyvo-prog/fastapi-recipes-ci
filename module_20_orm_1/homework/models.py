# models.py
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    count = Column(Integer, default=1)
    release_date = Column(Date, nullable=False)
    author_id = Column(Integer, nullable=False)


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    average_score = Column(Float, nullable=False)
    scholarship = Column(Boolean, nullable=False)
    dormitory = Column(Integer, nullable=True)

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
    book_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    date_of_issue = Column(DateTime, nullable=False)
    date_of_return = Column(DateTime, nullable=True)

    @hybrid_property
    def count_date_with_book(self):
        """Количество дней, которое читатель держит книгу."""
        if self.date_of_return is None:
            return (datetime.now() - self.date_of_issue).days
        return (self.date_of_return - self.date_of_issue).days