# init_db.py
from sqlalchemy import create_engine
from models import Base, Student, Book

engine = create_engine('sqlite:///library.db')
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Пример данных
students = [
    Student(name='Иванов Иван', dormitory=101, gpa=4.5),
    Student(name='Петров Пётр', dormitory=102, gpa=3.8),
    Student(name='Сидоров Сидр', dormitory=None, gpa=4.9),
]

books = [
    Book(title='Война и мир', author='Толстой', year=1869),
    Book(title='Преступление и наказание', author='Достоевский', year=1866),
    Book(title='Мастер и Маргарита', author='Булгаков', year=1967),
]

for s in students:
    session.add(s)
for b in books:
    session.add(b)

session.commit()
session.close()