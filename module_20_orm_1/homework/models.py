# models.py
from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class Student(Base):
    __tablename__ = 'students'

    student_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    dormitory = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=False)

    @classmethod
    def with_dormitory(cls, session):
        """Получить список студентов, у которых есть общежитие."""
        return session.query(cls).filter(cls.dormitory.isnot(None)).all()

    @classmethod
    def with_gpa_above(cls, session, gpa_threshold):
        """Получить список студентов со средним баллом выше порога."""
        return session.query(cls).filter(cls.gpa > gpa_threshold).all()


class Book(Base):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=True)


class ReceivingBook(Base):
    __tablename__ = 'receiving_books'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    book_id = Column(Integer, nullable=False)
    date_get = Column(Date, nullable=False)
    date_return = Column(Date, nullable=True)

    @hybrid_property
    def count_date_with_book(self):
        """Количество дней, которое читатель держит книгу."""
        if self.date_return is None:
            return (date.today() - self.date_get).days
        return (self.date_return - self.date_get).days