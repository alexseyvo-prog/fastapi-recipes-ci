from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import Base, Author, Book, Student, ReceivingBook, set_sqlite_pragma

engine = create_engine('sqlite:///library.db', echo=True)
event.listen(engine, "connect", set_sqlite_pragma)

Session = sessionmaker(bind=engine)
session = Session()

print("=" * 50)
print("Тест 1: joinedload - загрузка авторов с книгами")
print("=" * 50)
authors = session.query(Author).all()
for author in authors:
    print(f"{author.surname} {author.name}: {len(author.books)} книг")

print("\n" + "=" * 50)
print("Тест 2: subqueryload - загрузка студентов с выдачами")
print("=" * 50)
students = session.query(Student).all()
for student in students:
    print(f"{student.surname} {student.name}: {len(student.receivings)} выдач")

print("\n" + "=" * 50)
print("Тест 3: MANY-TO-MANY - студенты ↔ книги")
print("=" * 50)
book = session.query(Book).first()
print(f"Книга: {book.name}")
print(f"Студенты у книги: {[s.surname for s in book.students]}")

student = session.query(Student).first()
print(f"\nСтудент: {student.surname} {student.name}")
print(f"Книги у студента: {[b.name for b in student.books]}")

session.close()