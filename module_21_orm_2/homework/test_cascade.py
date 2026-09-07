from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import Base, Author, Book, Student, ReceivingBook, set_sqlite_pragma

engine = create_engine('sqlite:///library.db')
event.listen(engine, "connect", set_sqlite_pragma)

Session = sessionmaker(bind=engine)
session = Session()

print("До удаления:")
authors_count = session.query(Author).count()
books_count = session.query(Book).count()
print(f"Авторов: {authors_count}, Книг: {books_count}")

author = session.query(Author).filter_by(id=3).first()
print(f"\nУдаляем автора: {author.surname} {author.name}")

session.delete(author)
session.commit()

print("\nПосле удаления:")
authors_count = session.query(Author).count()
books_count = session.query(Book).count()
print(f"Авторов: {authors_count}, Книг: {books_count}")

session.close()